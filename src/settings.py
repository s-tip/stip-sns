import os
from decouple import Csv, config, UndefinedValueError
from unipath import Path
import stip.common.const as const
from stix_customizer import StixCustomizer

PROJECT_DIR = Path(__file__).parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# If you will use S-TIP in production mode, please change SECRET_KEY in .env file.
# Please keep same SECRET_KEY among S-TIP apps (for Single Sign On).
DEFAULT_SECRET_KEY = 'j%yjl@$v=xi6((y3!=bf3$n5)e)+af)*+syuia#co)1edp=dv-'
SECRET_KEY = config('SECRET_KEY', default=DEFAULT_SECRET_KEY)


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

mysql_user = config('MYSQL_USER')
mysql_password = config('MYSQL_PASSWORD')
try:
    mysql_dbname = config('MYSQL_DBNAME')
except UndefinedValueError:
    mysql_dbname = 's_tip'
try:
    mysql_host = config('MYSQL_HOST')
except UndefinedValueError:
    mysql_host = 'localhost'
try:
    mysql_port = config('MYSQL_PORT')
except UndefinedValueError:
    mysql_port = '3306'

try:
    TIME_ZONE = config('TIME_ZONE')
except UndefinedValueError:
    TIME_ZONE = 'UTC'
try:
    cookie_domain_name = config('COOKIE_DOMAIN_NAME')
except UndefinedValueError:
    cookie_domain_name = None

stix_customizer = StixCustomizer.get_instance()
try:
    stix_customizer.init_customizer_conf(config('STIX_CUSTOMIZER_CONF_PATH'))
except UndefinedValueError:
    pass

try:
    NLP_TYPE = config('NLP_TYPE').lower()
except UndefinedValueError:
    NLP_TYPE = None

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': mysql_dbname,
        'USER': mysql_user,
        'PASSWORD': mysql_password,
        'HOST': mysql_host,
        'PORT': mysql_port,
    }
}

ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())

# Application definition

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'activities',
    'authentication',
    'boot_sns.StipSnsBoot',
    'core',
    'feeds',
    'groups',
    'management',
    'messenger',
    'search',
    'bulk_upload',
    'ctirs',
)

MIDDLEWARE = [ 
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware'
]
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

ROOT_URLCONF = 'urls'
WSGI_APPLICATION = 'wsgi.application'
COMMON_PROJECT_DIR = '/opt/s-tip/common'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            PROJECT_DIR.child('templates'),
            Path(os.path.join(COMMON_PROJECT_DIR, 'src/templates')),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.headers',
            ],
            'debug': DEBUG
        },
    },
]

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = const.LANGUAGES

LOCALE_PATHS = (PROJECT_DIR.child('locale'), )

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

AUTH_USER_MODEL = 'ctirs.STIPUser'

STATIC_ROOT = PROJECT_DIR.parent.child('staticfiles')
STATIC_URL = '/static/'

SESSION_COOKIE_NAME = 'stip'
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
# HTTP 上で動作させるかどうかのフラグ
ENV_DEV_OVER_HTTP_KEY = 'DEV_OVER_HTTP'
dev_over_http = False
if ENV_DEV_OVER_HTTP_KEY in os.environ:
    if os.environ[ENV_DEV_OVER_HTTP_KEY] == 'True':
        dev_over_http = True
# http で動作させないときは SESSION_COOKIE_SECURE を立てる
if not dev_over_http:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
SESSION_COOKIE_DOMAIN = cookie_domain_name

MEDIA_ROOT = PROJECT_DIR.parent.child('media')
MEDIA_URL = '/media/'

LOGIN_URL = '/'
LOGIN_REDIRECT_URL = '/feeds/'

ALLOWED_SIGNUP_DOMAINS = ['*']

FILE_UPLOAD_TEMP_DIR = '/tmp/'
FILE_UPLOAD_PERMISSIONS = 0o644

CONF_DIR = PROJECT_DIR.parent.child('conf')
CONF_FILE_PATH = CONF_DIR + os.sep + 'sns.conf'
RS_PROJECT_DIR = '/opt/s-tip/rs'
RS_SRC_ROOT_DIR = RS_PROJECT_DIR + os.sep + 'src' + os.sep + 'ctirs'
RS_MODELS_DIR = RS_SRC_ROOT_DIR + os.sep + 'models'
RS_SNS_MODELS_DIR = RS_MODELS_DIR + os.sep + 'sns'

STATICFILES_DIRS = (
    os.path.join(COMMON_PROJECT_DIR, 'src/static'),
)

FIXTURE_DIRS = (
    RS_SNS_MODELS_DIR + os.sep + 'core' + os.sep + 'fixture',
    RS_SNS_MODELS_DIR + os.sep + 'groups' + os.sep + 'fixture',
    RS_SNS_MODELS_DIR + os.sep + 'config' + os.sep + 'fixture',
)

PDF_BASE_DIR = MEDIA_ROOT + os.sep + 'pdf'
PDF_FONT_DIR = PDF_BASE_DIR + os.sep + 'font' + os.sep
PDF_IMAGE_DIR = PDF_BASE_DIR + os.sep + 'image' + os.sep
