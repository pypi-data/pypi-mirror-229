# FastAPI Exception

### Setup python environment

```shell
python3 -m venv venv
```

### Active the python environemt

```shell
. venv/bin/activate
```

### Install requirements

```shell
pip install -r requirements.txt
```

## How to use

1. Set global app env

```python
from fastapi import FastAPI
from fastapi_global_variable import GlobalVariable

app = FastAPI(title="Application")

GlobalVariable.set('app', app)
```

2. Init FastAPI

```python
from config.i18n import i18n_service
from bootstraps import app
from fastapi_exception import FastApiException

FastApiException.init(app, i18n_service)
```
