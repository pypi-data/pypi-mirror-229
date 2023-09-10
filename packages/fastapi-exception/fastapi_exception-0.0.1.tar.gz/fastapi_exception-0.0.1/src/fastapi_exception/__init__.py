from fastapi_global_variable import GlobalVariable
from fastapi_exception_config import FastApiException
from .enums.error_type_enum import ErrorType

app = GlobalVariable.get_or_fail('app')


__all__ = ('FastApiException', 'ErrorType')
