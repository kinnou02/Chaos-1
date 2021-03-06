import os
# URI for postgresql
# postgresql://<user>:<password>@<host>:<port>/<dbname>
# http://docs.sqlalchemy.org/en/rel_0_9/dialects/postgresql.html#psycopg2
DATABASE_HOST = str(os.getenv('DATABASE_HOST', 'localhost'))
SQLALCHEMY_DATABASE_URI = 'postgresql://navitia:navitia@' + DATABASE_HOST + '/chaos'

DEBUG = True

NAVITIA_URL = 'http://navitia2-ws.ctp.dev.canaltp.fr'

# rabbitmq connections string: http://kombu.readthedocs.org/en/latest/userguide/connections.html#urls
RABBITMQ_HOST = str(os.getenv('RABBITMQ_HOST', 'localhost'))
RABBITMQ_CONNECTION_STRING = 'pyamqp://guest:guest@' + RABBITMQ_HOST + ':5672//?heartbeat=60'

# amqp exhange used for sending disruptions
EXCHANGE = 'navitia'

ENABLE_RABBITMQ = True

# Log Level available
# - DEBUG
# - INFO
# - WARN
# - ERROR

# logger configuration

from chaos.logging_utils import ChaosFilter

LOGGER = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] [%(request_id)s] [%(levelname)5s] [%(process)5s] [%(name)25s] %(message)s',
        },
    },
    'filters': {
        'ChaosFilter': {
            '()': ChaosFilter,
        }
    },
    'handlers': {
        'default': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'default',
            'filters': ['ChaosFilter'],
        },
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'DEBUG',
        },
        'amqp': {
            'level': 'DEBUG',
        },
        'sqlalchemy.engine': {
            'handlers': ['default'],
            'level': 'WARN',
            'propagate': False
        },
        'sqlalchemy.pool': {
            'handlers': ['default'],
            'level': 'WARN',
            'propagate': False
        },
        'sqlalchemy.dialects.postgresql': {
            'handlers': ['default'],
            'level': 'WARN',
            'propagate': False
        },
    }
}
