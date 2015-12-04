import logging
import time

from config import Config
from firebase import firebase

FIREBASE_URL_TEMPLATE = 'https://{0}.firebaseio.com'
GET_PARAMETER_TEMPLATE = '"{0}"'

MEDIA_NODE = '/media'
AUTH = 'auth'

PATH_TO_MEDIA = 'pathToMedia'
PATH_TO_THUMBNAIL = 'pathToThumbnail'
DATE_TAKEN = 'dateTaken'
DATE_INDEXED = 'dateIndexed'
SOURCE_DEVICE_ID = 'sourceDeviceId'
HASH = 'hash'
TYPE = 'type'

ORDER_BY = 'orderBy'
EQUAL_TO = 'equalTo'


class Index:
    def __init__(self, config=None):
        if config is None:
            config = Config()

        self.config = config

        firebase_name = self.config.firebase_name()
        self.fb_ref = firebase.FirebaseApplication(FIREBASE_URL_TEMPLATE.format(firebase_name), None)

    def index_media(self, path_to_media, path_to_thumbnail, taken, device_id, hash, type):
        logging.info('Indexing media. path_to_media=%s path_to_thumbnail=%s taken=%d device_id=%s hash=%s type=%s',
                     path_to_media, path_to_thumbnail, taken, device_id, hash, type)

        media_data = {
            PATH_TO_MEDIA: path_to_media,
            PATH_TO_THUMBNAIL: path_to_thumbnail,
            DATE_TAKEN: taken,
            DATE_INDEXED: int(time.time()),
            SOURCE_DEVICE_ID: device_id,
            HASH: hash,
            TYPE: type
        }

        parameters = {
            AUTH: self.config.firebase_secret()
        }

        self.fb_ref.post(MEDIA_NODE, media_data, parameters)

    def is_duplicate(self, hash_to_check):
        parameters = {
            AUTH: self.config.firebase_secret(),
            ORDER_BY: GET_PARAMETER_TEMPLATE.format(HASH),
            EQUAL_TO: GET_PARAMETER_TEMPLATE.format(hash_to_check)
        }

        results = self.fb_ref.get(MEDIA_NODE, None, params=parameters)

        return len(results) != 0
