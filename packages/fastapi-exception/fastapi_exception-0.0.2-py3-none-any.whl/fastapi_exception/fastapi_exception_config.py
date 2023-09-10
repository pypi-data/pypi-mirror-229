from typing import Any

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from fastapi_exception.handlers.request_exception_handler import validation_exception_handler


class FastApiException:
    i18n_service: Any = None

    @staticmethod
    def init(app: FastAPI, i18n_service):
        return FastApiException(app, i18n_service)

    def __init__(self, app: FastAPI, i18n_service):
        self.i18n_service = i18n_service

        app.exception_handler(RequestValidationError)(validation_exception_handler)

    @staticmethod
    def get_i18n_service():
        return FastApiException.i18n_service


i18n_service = FastApiException.i18n_service
