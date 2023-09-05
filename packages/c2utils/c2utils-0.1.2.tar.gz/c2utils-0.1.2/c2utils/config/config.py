# -*- coding: UTF-8 -*-
from functools import lru_cache

from pydantic import BaseSettings


class Settings(BaseSettings):
    EMAIL_PATTERN = r'^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z_-]+)+$'
    CELLPHONE_PATTERN = r'^((\+86)?([- ])?)?(|(13[0-9])|(14[0-9])|(15[0-9])|(17[0-9])|(18[0-9])|(19[0-9]))([- ])?\d{3}([- ])?\d{4}([- ])?\d{4}$'
    ID_CARDS_PATTERN = r'^[1-9][0-7]\d{4}((19\d{2}(0[13-9]|1[012])(0[1-9]|[12]\d|30))|(19\d{2}(0[13578]|1[02])31)|(19\d{2}02(0[1-9]|1\d|2[0-8]))|(19([13579][26]|[2468][048]|0[48])0229))\d{3}(\d|X|x)?$'


@lru_cache()
def get_settings():
    return Settings()


ALL_CONFIG = get_settings()
