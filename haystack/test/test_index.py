import unittest

from config import Config
from firebase import firebase
from index import Index
from mock import Mock
from mock import patch

MOCK_INDEX_TIME = 1449092137
MOCK_AUTH_TOKEN = 'fake-auth-token'


class TestIndex(unittest.TestCase):
    def setUp(self):
        self.firebase_patcher = patch('index.firebase')
        self.mock_firebase = self.firebase_patcher.start()

        self.time_patcher = patch('index.time')
        self.mock_time = self.time_patcher.start()
        self.mock_time.time.return_value = MOCK_INDEX_TIME

        self.mock_ref = Mock(spec=firebase.FirebaseApplication)
        self.mock_ref.get.return_value = {}

        self.mock_firebase.FirebaseApplication.return_value = self.mock_ref

        self.mock_config = Mock(spec=Config)
        self.mock_config.firebase_name.return_value = 'mock-firebase'
        self.mock_config.firebase_secret.return_value = MOCK_AUTH_TOKEN

    def __init_test(self):
        self.test_model = Index(self.mock_config)

    def __run_add_test(self):
        self.test_model.index_media('/path/to/media.jpg',
                                    '/path/to/thumbnail.jpg',
                                    1346060000,
                                    'USB',
                                    '098f6bcd4621d373cade4e832627b4f6',
                                    'JPG')

    def tearDown(self):
        self.firebase_patcher.stop()
        self.time_patcher.stop()

    def test_it_should_initiailize_the_firebase(self):
        self.__init_test()
        self.mock_firebase.FirebaseApplication.assert_called_once_with('https://mock-firebase.firebaseio.com', None)

    def test_it_should_use_the_firebase_from_the_config(self):
        self.mock_config.firebase_name.return_value = 'other-mock-firebase'
        self.__init_test()
        self.mock_firebase.FirebaseApplication.assert_called_once_with('https://other-mock-firebase.firebaseio.com',
                                                                       None)

    def test_it_should_use_the_right_values_when_adding_new_media(self):
        self.__init_test()
        self.__run_add_test()

        expected_data = {
            'pathToMedia': '/path/to/media.jpg',
            'pathToThumbnail': '/path/to/thumbnail.jpg',
            'dateTaken': 1346060000,
            'dateIndexed': MOCK_INDEX_TIME,
            'sourceDeviceId': 'USB',
            'hash': '098f6bcd4621d373cade4e832627b4f6',
            'type': 'JPG'
        }

        expected_params = {
            'auth': MOCK_AUTH_TOKEN
        }

        self.mock_ref.post.assert_called_once_with('/media', expected_data, params=expected_params)

    def test_it_should_use_the_right_values_when_checking_for_duplicates(self):
        self.__init_test()
        self.test_model.is_duplicate('dont-care')

        expected_params = {
            'auth': MOCK_AUTH_TOKEN,
            'orderBy': '"hash"',
            'equalTo': '"dont-care"'
        }

        self.mock_ref.get.assert_called_once_with('/media', None, params=expected_params)

    def test_it_should_return_true_if_the_hash_already_exists(self):
        self.mock_ref.get.return_value = {'id': 'data'}
        self.__init_test()

        self.assertTrue(self.test_model.is_duplicate('already-indexed'))

    def test_it_should_return_fales_if_the_hash_doesnt_exist(self):
        self.__init_test()

        self.assertFalse(self.test_model.is_duplicate('doesnt-exist'))


if __name__ == '__main__':
    unittest.main()
