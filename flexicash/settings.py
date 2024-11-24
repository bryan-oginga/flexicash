import os
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
DEBUG = True
import dj_database_url
from dotenv import load_dotenv
load_dotenv()

SECRET_KEY =  os.getenv('SECRET_KEY')
ALLOWED_HOSTS = ['flexicash-7b2ddc94d56c.herokuapp.com','localhost','127.0.0.1',]

if os.getenv('DJANGO_ENV') != 'production':
    load_dotenv()


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
    # 'django_celery_beat',

   
]
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

MIDDLEWARE = [
    
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add this line
    'django.middleware.security.SecurityMiddleware',
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
    'default': dj_database_url.config()
}
DATABASE_URL = os.getenv('DATABASE_URL')

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


# production settings
INTASEND_PUBLISHABLE_KEY = os.getenv('INTASEND_PUBLISHABLE_KEY')
INTASEND_SECRET_KEY = os.getenv('INTASEND_SECRET_KEY')
INTASEND_CHALLENGE_TOKEN = os.getenv('INTASEND_CHALLENGE_TOKEN')
INTASEND_WEBHOOK_URL = os.getenv('INTASEND_WEBHOOK_URL')



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
