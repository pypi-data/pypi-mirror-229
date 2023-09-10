from typing import Any


class FastApiException:
    i18n_service: Any = None

    @staticmethod
    def init(i18n_service):
        return FastApiException(i18n_service)

    def __init__(self, i18n_service):
        self.i18n_service = i18n_service

    @staticmethod
    def get_i18n_service():
        return FastApiException.i18n_service


i18n_service = FastApiException.i18n_service
