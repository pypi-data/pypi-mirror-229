import asyncio
from asyncio import SelectorEventLoop
import asyncio.events as events
import sys
from contextlib import contextmanager
from heapq import heappop
import functools
import inspect
import threading
import time
import weakref
import atexit
from typing import Optional, Union, TYPE_CHECKING, List, Callable, NamedTuple, Coroutine
from collections import defaultdict
# noinspection PyProtectedMember
from concurrent.futures._base import Future, PENDING, TimeoutError as FutureTimeout
from concurrent.futures import thread

from loguru import logger

from deepfos.options import OPTION
from deepfos.exceptions import BadFutureError
from .constant import UNSET


__all__ = [
    'evloop',
    'deepfosio',
    'register_on_loop_shutdown',
    'async_to_sync',
    'future_property',
    'FuturePropertyMeta',
    'cache_async',
]


MAIN_TID = threading.get_ident()
T_CoroutineFunc = Callable[[], Coroutine]
_LATER_THAN_3_10 = sys.version_info >= (3, 10)


# -----------------------------------------------------------------------------
# make Reentrant
# noinspection PyUnresolvedReferences,PyProtectedMember
def _patch_task():
    """Patch the Task's step and enter/leave methods to make it reentrant."""
    asyncio.Task = asyncio.tasks._CTask = asyncio.tasks.Task = \
        asyncio.tasks._PyTask
    asyncio.Future = asyncio.futures._CFuture = asyncio.futures.Future = \
        asyncio.futures._PyFuture

    Task = asyncio.Task  # noqa
    if getattr(Task, '__deepfos_patched__', False):
        return

    # noinspection PyProtectedMember
    def step(task, exc=None):
        curr_task = curr_tasks.get(task._loop)
        try:
            step_orig(task, exc)
        finally:
            if curr_task is None:
                curr_tasks.pop(task._loop, None)
            else:
                curr_tasks[task._loop] = curr_task

    def enter_task(loop, task):
        curr_tasks[loop] = task

    def leave_task(loop, task):  # noqa
        curr_tasks.pop(loop, None)

    asyncio.tasks._enter_task = enter_task
    asyncio.tasks._leave_task = leave_task
    curr_tasks = asyncio.tasks._current_tasks
    step_orig = Task._Task__step
    Task._Task__step = step
    setattr(Task, '__deepfos_patched__', True)


_patch_task()


# noinspection PyUnresolvedReferences,PyAttributeOutsideInit,PyProtectedMember
class ReentrantLoop(SelectorEventLoop):
    _num_runs_pending = 0
    _nest_patched = True

    def run_forever(self):
        with self.manage_run(), self.manage_asyncgens():
            while True:
                self._run_once()
                if self._stopping:
                    break
        self._stopping = False

    def run_until_complete(self, future):
        with self.manage_run():
            f = asyncio.ensure_future(future, loop=self)
            if f is not future:
                f._log_destroy_pending = False
            while not f.done():
                self._run_once()
                if self._stopping:
                    break  # pragma: no cover
            if not f.done():  # pragma: no cover
                raise RuntimeError(
                    'Event loop stopped before Future completed.')
            return f.result()

    @contextmanager
    def manage_run(self):
        """Set up the loop for running."""
        self._check_closed()
        old_thread_id = self._thread_id
        old_running_loop = events._get_running_loop()
        try:
            self._thread_id = threading.get_ident()
            events._set_running_loop(self)
            self._num_runs_pending += 1
            yield
        finally:
            self._thread_id = old_thread_id
            events._set_running_loop(old_running_loop)
            self._num_runs_pending -= 1

    @contextmanager
    def manage_asyncgens(self):
        if not hasattr(sys, 'get_asyncgen_hooks'):
            # Python version is too old.
            return  # pragma: no cover
        old_agen_hooks = sys.get_asyncgen_hooks()
        try:
            self._set_coroutine_origin_tracking(self._debug)
            if self._asyncgens is not None:
                sys.set_asyncgen_hooks(
                    firstiter=self._asyncgen_firstiter_hook,
                    finalizer=self._asyncgen_finalizer_hook)
            yield
        finally:
            self._set_coroutine_origin_tracking(False)
            if self._asyncgens is not None:
                sys.set_asyncgen_hooks(*old_agen_hooks)

    def _check_running(self):  # pragma: no cover
        """Do not throw exception if loop is already running."""
        pass

    def _run_once(self):
        """
        Simplified re-implementation of asyncio's _run_once that
        runs handles as they become ready.
        """
        ready = self._ready
        scheduled = self._scheduled
        while scheduled and scheduled[0]._cancelled:
            heappop(scheduled)

        timeout = (
            0 if ready or self._stopping
            else min(max(
                scheduled[0]._when - self.time(), 0), 86400) if scheduled
            else None)
        event_list = self._selector.select(timeout)
        self._process_events(event_list)

        end_time = self.time() + self._clock_resolution
        while scheduled and scheduled[0]._when < end_time:  # pragma: no cover
            handle = heappop(scheduled)
            ready.append(handle)

        for _ in range(len(ready)):
            if not ready:  # pragma: no cover
                break
            handle = ready.popleft()
            if not handle._cancelled:
                handle._run()
        handle = None  # noqa


# -----------------------------------------------------------------------------
# core
class Node:
    __slots__ = ('next', 'value', '_prev', '__weakref__')

    def __init__(self, value=None):
        self.value = value
        self.next: Optional[Node] = None
        self._prev = None

    @property
    def prev(self):
        if not self._prev:  # pragma: no cover
            return self._prev
        return self._prev()

    @prev.setter
    def prev(self, value):
        if value is None:  # pragma: no cover
            self._prev = None
        else:
            self._prev = weakref.ref(value)

    def __bool__(self):
        return True

    def __repr__(self):  # pragma: no cover
        return repr(self.value)


class LinkedList:
    def __init__(self):
        self.tail = self.root = Node()

    def __len__(self):
        return sum(1 for _ in self)

    def append(self, node: Node):
        self.tail.next = node
        node.prev = self.tail
        self.tail = node

    def wrap_append(self, value):
        node = Node(value)
        self.append(node)
        return node

    def remove(self, node: Node):
        _prev = node.prev
        _next = node.next

        _prev.next = _next

        if _next is None:
            self.tail = _prev
        else:
            _next.prev = _prev

    def __repr__(self):
        return "[{}]".format(', '.join(repr(item) for item in self))

    def __iter__(self):
        node = self.root
        while node := node.next:
            yield node.value

    def clear(self):
        node = self.root
        while node := node.next:
            self.remove(node)


class _AbstractTask:
    def __init__(self, future: Union[asyncio.Future, Future], coro: Coroutine, ensure):
        self.future = future
        self._display_name = coro.__qualname__
        self.ensure = ensure

    def result(self, timeout: float = None):  # pragma: no cover
        raise NotImplementedError

    def done(self):
        return self.future.done()

    def add_done_callback(self, callback):
        return self.future.add_done_callback(callback)

    def cancel(self):
        return self.future.cancel()

    def __repr__(self):
        return f"<{self.__class__.__name__} {self._display_name} at 0x{hex(id(self))}>"


class AsyncIOTask(_AbstractTask):
    if TYPE_CHECKING:  # pragma: no cover
        future: asyncio.Future

    def __init__(self, future, coro, ensure):
        super().__init__(future, coro, ensure)
        self.r = UNSET
        self.future.add_done_callback(self.set_task_done)

    def set_task_done(self, future):
        self.r = future.result()

    async def _wait_for_result(self, timeout=None):
        if _LATER_THAN_3_10:
            return await asyncio.wait_for(self.future, timeout)
        return await asyncio.wait_for(self.future, timeout, loop=evloop.loop)

    def result(self, timeout: float = None):
        if self.r is UNSET:
            if not evloop.in_same_thread():
                raise RuntimeError('Waiting a pending aio-task outside evloop is not allowed!')
            else:
                return self.r
        return evloop.run(self._wait_for_result(timeout))


class ThreadTask(_AbstractTask):
    if TYPE_CHECKING:  # pragma: no cover
        future: Future

    def result(self, timeout: float = None):
        # noinspection PyUnresolvedReferences,PyProtectedMember
        if self.future._state == PENDING and evloop.in_same_thread():  # pragma: no cover
            raise RuntimeError("Waiting a pending task in same thread will lead to deadlock!")

        return self.future.result(timeout=timeout)


class _PeriodicTask(NamedTuple):
    task: ThreadTask
    on_stop: Optional[T_CoroutineFunc]


class EventLoop:

    class _Loop(threading.Thread):
        def __init__(self, bind):
            threading.Thread.__init__(self)
            self.daemon = True
            self.id = None
            self._bind = weakref.ref(bind)
            self.loop = ReentrantLoop()

        def run(self):
            try:
                loop = self.loop
                self._bind().set_loop(loop)
                self.id = threading.get_ident()
                logger.debug(f"Starting loop in thread: [{self.id}]")
                asyncio.set_event_loop(loop)
                loop.run_forever()
                logger.debug(f"Loop in thread: [{self.id}] stopped.")
            except (KeyboardInterrupt, SystemExit):  # pragma: no cover
                try:
                    import _thread as thread
                except ImportError:
                    import thread  # noqa
                thread.interrupt_main()
            except Exception:  # pragma: no cover
                logger.exception("Loop stopped due to unexpected error.")
                raise

        def stop(self):
            self.loop.call_soon_threadsafe(self.loop.stop)
            time.sleep(0.001)
            self.join()

    def __init__(self):
        self.__thread = None
        self.__loop = None
        self._tasks = LinkedList()
        atexit.register(self.stop)
        self._setup()
        self._on_shutdown = []
        self._periodic_task: List[_PeriodicTask] = []

    @property
    def loop(self) -> asyncio.BaseEventLoop:
        if self.__loop is None:
            self._setup()
        elif self.__loop.is_closed():  # pragma: no cover
            self._setup()
        return self.__loop

    @property
    def thread(self):
        if self.__thread is None:
            self._setup()
        return self.__thread

    def _setup(self):
        self.stop()
        self.__thread = self._Loop(self)
        self.__thread.start()

    def set_loop(self, loop):
        self.__loop = loop

    def run(self, coro):
        if self.in_same_thread():
            return self.loop.run_until_complete(coro)
        else:
            return self.create_task(coro).result()

    def create_task(self, coro, ensure=False) -> _AbstractTask:
        if self.in_same_thread():
            task = AsyncIOTask(asyncio.create_task(coro), coro, ensure)
        else:
            task = ThreadTask(asyncio.run_coroutine_threadsafe(coro, self.loop), coro, ensure)
        node = self._tasks.wrap_append(task)
        task.add_done_callback(self._report_task_done(node))
        return task

    apply = create_task

    def _report_task_done(self, node: Node):
        def cb(fut):
            logger.debug(f"Task {node.value} finished.")
            self._tasks.remove(node)
        return cb

    def register_shutdown(self, handler, is_coro=UNSET):
        self._on_shutdown.append((handler, is_coro))

    def stop(self):
        if self.__loop is None:
            return

        for periodic_task in self._periodic_task:
            self.cancel_periodic_task(periodic_task)

        self.run(DeepFOSIO.apply_handler(self._on_shutdown))
        timeout = OPTION.general.coro_graceful_timeout

        for task in self._tasks:
            # noinspection PyBroadException
            try:
                if not task.done():
                    if task.ensure:
                        timeout = None
                    if isinstance(task, AsyncIOTask):
                        self.__loop.call_soon_threadsafe(task.result, timeout)
                    else:
                        task.result(timeout)
            except FutureTimeout:  # pragma: no cover
                logger.error(f"Wait for task: {task} timed out.")
            except FutureAbandonedError:
                pass
            except Exception:  # pragma: no cover
                logger.exception("Failed to wait task.")

        waited = 0
        interval = 0.05
        while (n := len(asyncio.all_tasks(loop=self.__loop))) > 0 and waited < timeout:
            time.sleep(interval)
            waited += interval
            interval *= 2
            logger.debug(f"Still waiting {n} tasks to finish..")

        if self.__thread is not None:
            logger.debug(f"Stopping loop in thread: [{self.__thread.id}] ...")
            self.__thread.stop()
            self.__thread = None

        if self.__loop is not None:
            self.__loop.call_soon_threadsafe(self.__loop.stop)
            self.__loop = None

        self._tasks.clear()
        self._periodic_task.clear()

    def in_same_thread(self):
        return threading.get_ident() == self.thread.id

    def create_periodic_task(
        self,
        coro: T_CoroutineFunc,
        loop_when: Callable[[], bool] = None,
        interval: int = 2,
        on_stop: T_CoroutineFunc = None,
    ) -> _PeriodicTask:
        if loop_when is None:
            loop_when = lambda: True

        async def task_body():
            while loop_when():
                await coro()
                await asyncio.sleep(interval)
            if on_stop is not None:
                await on_stop()
        task = self.create_task(task_body())
        periodic_task = _PeriodicTask(
            task=task,
            on_stop=on_stop,
        )
        self._periodic_task.append(periodic_task)
        return periodic_task

    def cancel_periodic_task(self, periodic_task: _PeriodicTask):
        if periodic_task.task.done():
            return
        try:
            periodic_task.task.cancel()
            if periodic_task.on_stop is not None:
                self.run(periodic_task.on_stop())
        except Exception:  # pragma: no cover
            logger.exception("Exception occurs when cancel task.")


evloop = EventLoop()


def async_to_sync(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        coro = func(*args, **kwargs)
        return evloop.run(coro)
    return wrapper


class ErrorFuture:  # pragma: no cover
    __slots__ = ('_name_', '_err_')

    def __init__(self, name, error):
        self._name_ = name
        self._err_ = error

    def __getattr__(self, item):
        raise BadFutureError(self._get_msg(), self)

    def _get_msg(self):
        err = self._err_
        ref_chain = [self._name_]

        while isinstance(err, BadFutureError):
            ref_chain.append(err.obj._name_)  # noqa
            err = err.obj

        ref_str = ' -> '.join(ref_chain)
        err_repr = repr(err)

        return f"\nReference Chain: {ref_str}\n" \
               f"Error: {err_repr}"

    def __repr__(self):
        return repr(self._err_)


class FutureAbandonedError(Exception):
    """Future is pending while thread wants to exit,
    thus the future should be safely abandoned."""


class AbandonFuture(Exception):
    def __getattr__(self, item):
        raise FutureAbandonedError('Future is abandoned.')


class _TaskProp:
    def __init__(self):
        self.task = None
        self.result = UNSET
        self.redo = False
        if _LATER_THAN_3_10:
            self.done = asyncio.Event()
            self.guard = asyncio.Event()
        else:
            self.done = asyncio.Event(loop=evloop.loop)
            self.guard = asyncio.Event(loop=evloop.loop)


# noinspection PyPep8Naming
class future_property:
    def __init__(self, func):
        self.func = func
        self.__doc__ = func.__doc__
        self._tasks = defaultdict(_TaskProp)

    def __set_name__(self, owner, name):
        self.attrname = name

    # noinspection PyProtectedMember
    def __get__(self, instance, owner=None):
        if instance is None:
            return self

        task = self._tasks[instance]
        if task.task is None:  # pragma: no cover
            raise RuntimeError(
                f'Coroutine returned by method: {self.func.__qualname__} '
                f'is never awaited.')

        if task.result is UNSET:
            if task.redo:
                task.result = evloop.run(self.func(instance))
                task.redo = False
            else:
                if task.guard.is_set() and task.guard._owner_ != self.attrname:
                    raise RuntimeError(  # pragma: no cover
                        f'Referring to a future_property ({self.attrname}) inside '
                        f'another future_property ({task.guard._owner_}) is strictly forbidden!')
                try:
                    task.guard.set()
                    task.guard._owner_ = self.attrname

                    if evloop.in_same_thread():
                        evloop.run(self.wait_for(instance))
                    else:
                        task.result = task.task.result()
                finally:
                    task.guard.clear()

        setattr(instance, self.attrname, task.result)
        return task.result

    def submit(self, instance):
        t = self._tasks[instance]
        t.task = task = evloop.create_task(self.func(instance))
        task.add_done_callback(functools.partial(self.set_task_done, instance))

    async def wait_for(self, instance):
        task = self._tasks[instance]
        await task.done.wait()
        return task.result

    def set_task_done(self, instance, future):
        task = self._tasks[instance]
        try:
            task.result = future.result()
        except Exception as e:
            if not thread._shutdown:
                # Fetching a future property on thread exit should not raise
                task.result = ErrorFuture(self.attrname, e)
                raise
            else:
                task.result = AbandonFuture()
        finally:
            task.done.set()

    def reset(self, instance):
        if instance not in self._tasks:
            return

        task = self._tasks[instance]
        task.result = UNSET
        task.redo = True
        delattr(instance, self.attrname)


class FuturePropertyMeta(type):
    def __init__(cls, name, bases, namespace):
        submit_calls = []

        for _name, attr in cls.__dict__.items():
            if not isinstance(attr, future_property):
                continue
            submit_calls.append(attr.submit)

        ori_init = cls.__init__

        if ori_init is None:
            def new_init(self, *_args, **_kwargs):
                for call in submit_calls:
                    call(self)  # noqa

        else:
            def new_init(self, *_args, **_kwargs):
                ori_init(self, *_args, **_kwargs)
                for call in submit_calls:
                    call(self)  # noqa

        cls.__init__ = new_init
        if callable(ori_init):
            cls.__init__.__signature__ = inspect.signature(ori_init)

        super().__init__(name, bases, namespace)


def cache_async(coro_func):
    lock_key = '__cache_lock__'

    @functools.wraps(coro_func)
    async def wrapper(self, *args, **kwargs):
        key = f"_{coro_func.__name__}_"
        if not hasattr(self, lock_key):
            setattr(self, lock_key, asyncio.Lock())

        async with getattr(self, lock_key):
            cache = getattr(self, key, None)
            if cache is not None:
                return cache

            value = await coro_func(self, *args, **kwargs)
            setattr(self, key, value)
            return value
    return wrapper


class DeepFOSIO:
    def __init__(self):
        self.__running = False
        self.on_startup = []
        self.on_shutdown = []

    def register_shutdown(self, coro, is_coro=UNSET):
        if not self.__running:
            return
        self.on_shutdown.append((coro, is_coro))

    def register_startup(self, coro, is_coro=UNSET):
        if self.__running:
            return
        self.on_startup.append((coro, is_coro))

    def run(self, coro):
        self.__running = True
        try:
            return asyncio.run(self._managed_run(coro))
        finally:
            self.__running = False

    @staticmethod
    async def apply_handler(handlers: List[Callable]):
        for handler, is_coro in handlers:
            if is_coro is True:
                await handler()
            elif is_coro is False:
                handler()
            else:
                if inspect.iscoroutinefunction(handler):
                    await handler()
                else:
                    handler()
        handlers.clear()

    async def _managed_run(self, main):
        await self.apply_handler(self.on_startup)
        self.on_startup.clear()
        try:
            return await main
        finally:
            try:
                await self.apply_handler(self.on_shutdown)
            except Exception:  # pragma: no cover
                pass


deepfosio = DeepFOSIO()


def register_on_loop_shutdown(coro_or_func, is_coro=UNSET):
    if evloop.in_same_thread():
        evloop.register_shutdown(coro_or_func, is_coro)
    else:
        deepfosio.register_shutdown(coro_or_func, is_coro)
