import os
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Recife'
USE_I18N = True
USE_L10N = True
USE_TZ = False

DECIMAL_SEPARATOR = ','
USE_THOUSAND_SEPARATOR = False

REST_FRAMEWORK = {
    'DATE_FORMAT': "%Y-%m-%dT%H:%M:%S",
    'DATETIME_FORMAT': "%Y-%m-%dT%H:%M:%S",
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissions',
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        # 'django_filters.rest_framework.DjangoFilterBackend',
        # 'rest_framework.filters.SearchFilter',
        # 'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    # 'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    # 'PAGE_SIZE': 5,
    'DEFAULT_PARSER_CLASSES': [
            'rest_framework.parsers.JSONParser',
            'rest_framework.parsers.FormParser',
            'rest_framework.parsers.MultiPartParser',
            'rest_framework.parsers.FileUploadParser',
    ],
    'DEFAULT_RENDERER_CLASSES': ['rest_framework.renderers.JSONRenderer'],
    'UPLOADED_FILES_USE_URL': False,
}

SWAGGER_SETTINGS = {
   'USE_SESSION_AUTH': True,
   'SECURITY_DEFINITIONS': {
      'Basic': {
            'type': 'basic'
      },
      'Token': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
      },
      'OAuth2': {
         'type': 'oauth2',
         'authorizationUrl': os.environ.get('OAUTH2_AUTHORIZE_URL', ''),
         'tokenUrl': os.environ.get('OAUTH2_ACCESS_TOKEN_URL', ''),
         'flow': 'accessCode',
         'scopes': {
          'read:groups': 'read groups',
         }
      }
   },
   'OAUTH2_CONFIG': {
      'clientId': os.environ.get('OAUTH2_CLIENTE_ID', ''),
      'clientSecret': os.environ.get('OAUTH2_CLIENT_SECRET', ''),
      'appName': 'OAUTH2'
   },
   'DEFAULT_AUTO_SCHEMA_CLASS': 'api.viewsets.AutoSchema',
}

LOGGING_ = {
    'version': 1,
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
        }
    },
    'loggers': {
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['console'],
        }
    }
}