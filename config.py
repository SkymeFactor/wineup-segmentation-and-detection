import logging.config
import os


# Kafka
NEW_WINE_MESSAGE_SENT_TOPIC = 'eventTopic'
NEW_SEGMENTATION_IS_READY_TOPIC = 'segmentedImage'
KAFKA_POLLING_TIMEOUT = int(os.getenv('KAFKA_POLLING_TIMEOUT', '30'))
KAFKA_BOOTSTRAP_SERVERS = ['kafka:9092']

# hosts
_WINE_UP_DOMAIN_ADDRESS = 'http://77.234.215.138:18080'
_CATALOG_SERVICE_HOST = os.getenv(
    'CATALOG_SERVICE_HOST',
    f'{_WINE_UP_DOMAIN_ADDRESS}/catalog-service'
)
RECOMMENDATION_SERVICE_HOST = os.getenv(
    'RECOMMENDATIONS_SERVICE_HOST',
    f'{_WINE_UP_DOMAIN_ADDRESS}/ml4-recommendation-service'
)

# endpoints
CATALOG_POSITION_BY_ID_CONTROLLER = f'{_CATALOG_SERVICE_HOST}/position/true/byId'

RECOMMENDATION_SERVICE_API = f'{RECOMMENDATION_SERVICE_HOST}/api/v1.0'
RECOMMENDATION_SEGMENTATION_ENDPOINT = f'{RECOMMENDATION_SERVICE_API}/segmentation'
RECOMMENDATION_GET_IMAGE_ENDPOINT = f'{RECOMMENDATION_SERVICE_API}/get_image='

logging.config.dictConfig(
    {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'simple': {
                'format': '{asctime} {levelname} {name}:{lineno} - {message}',
                'style': '{',
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'simple',
            },
        },
        'root': {
            'handlers': ['console'],
            'level': os.getenv('LOGGING_LEVEL', 'INFO'),
        },
    }
)
