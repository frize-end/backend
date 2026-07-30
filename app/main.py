# -*- coding: utf-8 -*-  # noqa: UP009
from core.config import Settings
from fastapi import FastAPI

#实例化应用
app = FastAPI()


settings = Settings()
print(settings.user, settings.user_host, settings.user_password)
