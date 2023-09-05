try:
    from . import pandas
    from . import jstream
except ImportError:
    from . import py_pandas as pandas
    from . import py_jstream as jstream
