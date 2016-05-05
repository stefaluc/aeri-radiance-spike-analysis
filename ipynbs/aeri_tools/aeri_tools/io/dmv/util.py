from contextlib import contextmanager
import DmvAdapter

__author__ = 'cphillips'


@contextmanager
def to_dmv(path_or_dmv):
    """
    :param path_or_dmv:
    :return DmvAdapter.DmvAdapter:
    """
    if isinstance(path_or_dmv,basestring):
        # path_or_dmv is a path
        yield DmvAdapter.open(path_or_dmv)
    elif isinstance(path_or_dmv, DmvAdapter.DmvAdapter):
        yield path_or_dmv
    else:
        raise TypeError("{} is not a path or DmvAdapter object".format(path_or_dmv))