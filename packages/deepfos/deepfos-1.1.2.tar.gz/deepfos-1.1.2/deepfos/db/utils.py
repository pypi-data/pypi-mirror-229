import asyncio
import base64

from deepfos.api.python import PythonAPI
from deepfos.api.models.python import WorkerRegistry

from deepfos.lib.utils import retry, Wait
from deepfos.lib.constant import UNSET
from deepfos.lib.asynchronous import evloop
from deepfos.options import OPTION
from deepfos.exceptions import APIResponseError
from .cipher import AES

# -----------------------------------------------------------------------------
# constants
PENDING = 0
INITIALIZING = 1
INITIALIZED = 2
#: 账号失效时间
ACCOUNT_EXPIRE = 3600 * 8


class DBConnecetionError(Exception):
    pass


class AbsLeaseManager:
    DB = None

    def __init__(self, interval):
        self._last_renewal = None
        self._interval = interval
        self._task = UNSET
        self._info = UNSET
        self._renew_fn = None

    async def new_api(self):  # pragma: no cover
        raise NotImplementedError

    async def _try_renewal(self, api, raises=False):
        try:
            return True, await api.dml.create_account()
        except APIResponseError as e:
            if raises:
                raise
            py_api = await PythonAPI(version=2.0, sync=False)
            await py_api.worker.register(WorkerRegistry(
                hostname=OPTION.general.task_info['worker_name'],
                db=[self.DB]
            ))
            return False, e

    @retry(wait=Wait(0.5, 'exp_backoff', 2), retries=4)
    async def renew(self):
        api = await self.new_api()

        flag, account = await self._try_renewal(api)
        if flag is False:  # retry once
            _, account = await self._try_renewal(api, raises=True)

        self._info = account
        return account

    async def loop(self, slow_start=True):
        if slow_start:
            await asyncio.sleep(self._interval)
        while True:
            await self.renew()
            await asyncio.sleep(self._interval)

    def schedule(self, slow_start=True):
        if self._task is UNSET:
            try:
                asyncio.get_running_loop()
                self._task = asyncio.create_task(
                    self.loop(slow_start))
            except RuntimeError:
                self._task = evloop.create_task(
                    self.loop(slow_start))

    def cancel(self):
        if self._task is not UNSET:
            self._task.cancel()
            self._task = UNSET


def decrypt(secret, cipher_text, encoding='utf8'):
    return AES(secret).decrypt(
        base64.b16decode(cipher_text)
    ).rstrip().decode(encoding)
