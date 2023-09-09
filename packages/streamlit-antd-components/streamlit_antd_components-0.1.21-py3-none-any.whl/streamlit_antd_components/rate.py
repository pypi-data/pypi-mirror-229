#!/usr/bin/env python
# _*_coding:utf-8_*_

"""
@Time     : 2023/7/24 15:00
@Author   : ji hao ran
@File     : rate.py
@Project  : StreamlitAntdComponents
@Software : PyCharm
"""
from .utils import *


def rate(
        value: float = 0,
        count: int = 5,
        symbol: Union[str, BsIcon] = None,
        clear: bool = False,
        half: bool = False,
        readonly: bool = False,
        size: int = 20,
        color: str = None,
        key=None,
) -> float:
    """antd design rate

    :param value: rate default value,must be divide by 0.5
    :param count: rate total count
    :param symbol: symbol,default star,can be str or BsIcon
    :param clear: allow double click to clear select
    :param half: allow half select
    :param readonly: readonly mode
    :param size: symbol size in px
    :param color: symbol color,default primary color
    :param key: component key
    :return: select value
    """
    assert value % 0.5 == 0, 'value must be divisible by 0.5'
    if value % 1 != 0 and not half:
        raise ValueError('value must be int when half is False')
    kw = dict(locals())
    kw.update(symbol={'bs': symbol.__dict__.get('name')} if isinstance(symbol, BsIcon) else symbol)
    # pass component id and params to frontend
    r = component_func(id='rate', kw=kw)
    # parse result
    return r if r is not None else value
