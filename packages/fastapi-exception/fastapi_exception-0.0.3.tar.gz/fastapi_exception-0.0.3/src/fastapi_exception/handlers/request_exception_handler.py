import json
from urllib.error import HTTPError

from requests import RequestException
from starlette.responses import JSONResponse

from fastapi_exception import app


@app.exception_handler(RequestException)
async def validation_exception_handler(request, error: HTTPError):  # pylint: disable=unused-argument
    error = json.loads(error.response.text).get('error')
    response = {'message': error.get('message')}
    return JSONResponse(response, status_code=error.get('code'))
