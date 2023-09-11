# Django FastAPI Bridge

Allows to use [FastAPI](fastapi.tiangolo.com/) top of
[Django](https://www.djangoproject.com/)

## Quickstart

Install required packages:

`pip install django-fastapi-bridge daphne`

*Note that `daphne` is required only for changing `runserver` command to
work with ASGI. It is not required for production usage.*

Add `django_fastapi` and `daphne` to `INSTALLED_APPS` in your `settings.py` file:

```
INSTALLED_APPS = [
    # ...
    "daphne",  # must be before django.cotrib.staticfiles
    "django.contrib.staticfiles",
    # ...
    "django_fastapi",
]
```

Set `ASGI_APPLICATION` in your `settings.py` file:

```
ASGI_APPLICATION = "django_fastapi.asgi.application"
```

### Development server (ASGI w/Daphne)

Run development server:

```
python manage.py runserver
```

### Production server (ASGI w/Uvicorn)

Install Uvicorn:

```
pip install uvicorn
```

Run uvicorn:

```
DJANGO_SETTINGS_MODULE=yourproject.settings uvicorn django_fastapi.asgi:application
```


## Configuration

### Base settings

To configure default `FastAPI` instance you can use these settings:

 * `FASTAPI_TITLE`: set's API title [`FastAPI(title=FASTAPI_TITLE)`]
 * `FASTAPI_VERSION`: set's API version [`FastAPI(version=FASTAPI_VERSION)`]
 * `FASTAPI_ROOT_PATH`: set's API root path [`FastAPI(root_path=FASTAPI_ROOT_PATH)`]

### CORS

 * `FASTAPI_CORS_ENABLED`: if True, adds CORS middleware to the default
   FastAPI instance (disabled by default)
 * `FASTAPI_CORS_ALLOW_ORIGINS`: defaults to `["*"]`
 * `FASTAPI_CORS_ALLOW_CREDENTIALS`: defaults to `True`
 * `FASTAPI_CORS_ALLOW_METHODS`: defaults to `["*"]`
 * `FASTAPI_CORS_ALLOW_HEADERS`: defaults to `["*"]`

### Autodiscover

 * `FASTAPI_AUTODISCOVER`: if True, Django FastAPI will automatically
   import `FASTAPI_AUTODISCOVER_MODULES` from your `INSTALLED_APPS`.
   Default: `True`
 * `FASTAPI_AUTODISCOVER_MODULES`: defaults to `["api"]`

## License

ISC

Copyright 2023 Marcin Nowak <marcin.j.nowak.gmail.com>

Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby granted, provided that the above copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED “AS IS” AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
