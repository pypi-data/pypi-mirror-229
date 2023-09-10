import json

from keycloak import KeycloakAuthenticationError, KeycloakPostError
from starlette.responses import JSONResponse
from fastapi_exception import app


@app.exception_handler(KeycloakAuthenticationError)
async def keycloak_exception_handler(request, error: KeycloakAuthenticationError):
    print('KeycloakAuthenticationError', error)

    message = 'Authentication failed.'
    if error.error_message:
        decoded_error = json.loads(error.error_message.decode("utf-8"))
        error_type = decoded_error.get('error')

        match error_type:
            case 'invalid_grant':
                message = 'Your email or password is incorrect!'
            case 'invalid_token':
                message = decoded_error.get('error_description')

    response = {'message': message}
    return JSONResponse(response, status_code=error.response_code)


@app.exception_handler(KeycloakPostError)
async def keycloak_post_exception_handler(request, error: KeycloakPostError):
    exception = json.loads(error.error_message.decode("utf-8"))
    response = {
        'message': exception.get('error_description'),
    }
    return JSONResponse(response, status_code=error.response_code)
