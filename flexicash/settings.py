import os
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-50#5$pbme&ajmg%r-c2hlsec(74lqg#69o%)x24)&yj+d$365n'
DEBUG = True

ALLOWED_HOSTS = ['f7c2-41-212-105-164.ngrok-free.app','localhost','127.0.0.1',]

INSTALLED_APPS = [
    
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
     
    'ussd',
    'accounts',
    'reports',
    'fleximembers',
    'loanapplication',
    'lipanampesa',
    'transactions',
    
    'rest_framework',
    'phonenumber_field',
    'django_celery_beat',

   
]
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'flexicash.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,'templates')],
        'APP_DIRS': True,  # This should be True

        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'flexicash.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True
TIME_ZONE = 'Africa/Nairobi'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
USE_THOUSAND_SEPARATOR = True

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'staticfiles')]
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')



EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend' 
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'ogingabrian2017@gmail.com'
EMAIL_HOST_PASSWORD =  'xtfzlyicegpxjnho' 
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'Flexipay Team <noreply@sendify.com>'

INSTASEND_PUBLISHABLE_KEY = 'ISPubKey_test_7c58de8a-2340-4b9d-af0e-1d2b479086c2'
INSTASEND_SECRET_KEY = 'ISSecretKey_test_4532c33f-e7f2-403b-9a35-7b69f7ba659b'
INTASEND_CHALLENGE_TOKEN = "xtfzlyicegpxjnho"

TINYPESA_API_KEY = "hxIAKK4Ab9h9NXSQJ1qEMN-HJ5NTeeawnU169GA0Cw8vVCD0DJ"  # Replace with your API key
TINYPESA_USERNAME = "ogingabrian2017@gmail.com"  # Replace with your username
TINYPESA_BASE_URL = "https://tinypesa.com/api/v1"

PAYHERO_PASSWORD = "kuxgCdwDPvC14WPeHvmY8xI4dRDD2QYT6NzgdsNW"
PAYHERO_USERNAME = "EAk1cW0ondlYisBqcn41"
PAYHERO_ACCOUNT_ID  = "1052"
PAYHERO_CHANNEL_ID  = "1058"
PAYHERO_ENDPOINT_URL = 'https://backend.payhero.co.ke/api/v2/payments'
PAYHERO_CALLBACK_URL = 'https://f7c2-41-212-105-164.ngrok-free.app/payment/payhero_callback/'




CORS_REPLACE_HTTPS_REFERER      = False
HOST_SCHEME                     = "https://"
SECURE_PROXY_SSL_HEADER         = None
SECURE_SSL_REDIRECT             = False
SESSION_COOKIE_SECURE           = False
CSRF_COOKIE_SECURE              = False
SECURE_HSTS_SECONDS             = None
SECURE_HSTS_INCLUDE_SUBDOMAINS  = False
SECURE_FRAME_DENY               = False


CELERY_BROKER_URL = 'redis://localhost:6379/0'  # Redis as the message broker
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'  # Redis as the result backend

broker_connection_retry_on_startup = True


CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

CELERY_TASK_TIME_LIMIT = 30 * 60  # Maximum time a task can run (30 minutes)
CELERY_TASK_SOFT_TIME_LIMIT = 30 * 60  # Time before forcefully terminating the task


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',  # You can use DEBUG to see more detailed logs
            'propagate': True,
        },
        # lipa na mpesa logs
        'lipanampesa': {
            'handlers': ['console', 'file'],  # Logging for your specific app
            'level': 'DEBUG',
            'propagate': True,
        },
        # ussd logs
        'ussd': {
            'handlers': ['console', 'file'],  # Logging for your specific app
            'level': 'DEBUG',
            'propagate': True,
        },
        # accounts logs
        'accounts': {
            'handlers': ['console', 'file'],  # Logging for your specific app
            'level': 'DEBUG',
            'propagate': True,
        },
        # loanapplication logs
        'loanapplication': {
            'handlers': ['console', 'file'],  # Logging for your specific app
            'level': 'DEBUG',
            'propagate': True,
        },
        # transactions logs
        'transactions': {
            'handlers': ['console', 'file'],  # Logging for your specific app
            'level': 'DEBUG',
            'propagate': True,
        },
        # reports logs
    },
}
