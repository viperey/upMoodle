import json

from rest.controllers.controllers import get_random_string
from rest.models import User, ErrorMessage, NoteBoard
from rest.models.message.errorMessage import ErrorMessageType
from tests.integration.system import AuthenticationTestBase
from tests.utils import load_fixture, assert_error_response


class NoteTestCase(AuthenticationTestBase):

    def setUp(self):
        super(NoteTestCase, self).setUp()
        load_fixture("provision-data")
        self.createUser()

    def test_01_basic_note_get(self):
        self.login()
        self.addDefaultNote()
        pk = '1'
        response = self.client.get('/note/' + pk + '/')
        self.assertEqual(response.status_code, 200)
        decoded = json.loads(response.content)
        self.assertIsNotNone(decoded['id'])
        self.assertEqual(decoded['topic'], self.DEFAULT_NOTE_TOPIC)

    def test_02_getNote_not_signed_in(self):
        self.logout()
        pk = '1'
        response = self.client.get('/note/' + pk + '/')
        assert_error_response(response, ErrorMessageType.NOT_SIGNED_IN)

    def test_03_getNote_id_overflow(self):
        self.login()
        pk = '191289347901273481236498712634971234123481263984'
        response = self.client.get('/note/' + pk + '/')
        assert_error_response(response, ErrorMessageType.INCORRECT_DATA)

    def test_04_postNote_basic(self):
        self.login()
        self.addDefaultNote()
        pk = 1
        topic = 'topic'
        response = self.client.post('/note/' + str(pk) + '/', {'topic': topic, 'text': 'text', 'level_id': 1})
        self.assertEqual(response.status_code, 200)
        note = NoteBoard.objects.get(id=1)
        self.assertEqual(topic, note.topic)

    def test_05_postNote_signedOut(self):
        self.logout()
        pk = 1
        topic = 'topic'
        response = self.client.post('/note/' + str(pk) + '/', {'topic': topic, 'text': 'text', 'level_id': 1})
        assert_error_response(response, ErrorMessageType.NOT_SIGNED_IN)

    def test_06_postNote_forbiddenFields(self):
        self.login()
        self.addDefaultNote()
        pk = 1
        topic = 'topic'
        response = self.client.post('/note/' + str(pk) + '/', {'topic': topic, 'text': 'text', 'author_id': 2})
        assert_error_response(response, ErrorMessageType.INVALID_LEVEL)
        note = NoteBoard.objects.get(id=1)
        self.assertEqual(note.author_id, User.objects.get(id=1).id)

    def test_07_postNote_emptyQuery(self):
        self.login()
        pk = 1
        response = self.client.post('/note/' + str(pk) + '/', {})
        assert_error_response(response, ErrorMessageType.INCORRECT_DATA)

    def test_08_postNote_length_overflows(self):
        self.login()
        pk = 1
        # Topic
        response = self.client.post('/note/' + str(pk) + '/', {'topic': get_random_string(2001), 'text': 'text', 'level_id': 1})
        assert_error_response(response, ErrorMessageType.INCORRECT_DATA)
        # Text
        response = self.client.post('/note/' + str(pk) + '/',
                                    {'topic': 'topic', 'text': get_random_string(2001), 'level_id': 1})
        assert_error_response(response, ErrorMessageType.DISABLED_COOKIES)

    def test_09_createNote_basic(self):
        self.login()
        pk = 1
        topic = 'Create'
        response = self.client.post('/note/', {'topic': topic, 'text': 'text', 'level_id': 1})
        self.assertEqual(response.status_code, 200)
        note = NoteBoard.objects.get(id=1)
        self.assertEqual(topic, note.topic)

    def test_10_createNote_signedOut(self):
        self.logout()
        pk = 1
        topic = 'topic'
        response = self.client.post('/note/', {'topic': topic, 'text': 'text', 'level_id': 1})
        assert_error_response(response, ErrorMessageType.NOT_SIGNED_IN)

    def test_11_createNote_forbiddenFields(self):
        self.login()
        pk = 1
        topic = 'topic'
        response = self.client.post('/note/', {'topic': topic, 'text': 'text', 'level_id': 1, 'author_id': 2})
        self.assertEqual(response.status_code, 200)
        note = NoteBoard.objects.get(id=1)
        self.assertEqual(note.author_id, User.objects.get(id=1).id)

    def test_12_createNote_emptyQuery(self):
        self.login()
        pk = 1
        response = self.client.post('/note/', {})
        assert_error_response(response, ErrorMessageType.INVALID_LEVEL)

    def test_13_createNote_length_overflows(self):
        self.login()
        pk = 1
        # Topic
        response = self.client.post('/note/', {'topic': get_random_string(2001), 'text': 'text', 'level_id': 1})
        assert_error_response(response, ErrorMessageType.INCORRECT_DATA)
        # Text
        response = self.client.post('/note/', {'topic': 'topic', 'text': get_random_string(2001), 'level_id': 1})
        assert_error_response(response, ErrorMessageType.DISABLED_COOKIES)

    def test_14_deleteNote_wrong_id(self):
        self.login()
        pk = 4
        response = self.client.delete('/note/' + str(pk) + '/')
        assert_error_response(response, ErrorMessageType.INCORRECT_DATA)

    def test_15_deleteNote_basic(self):
        self.login()
        self.addDefaultNote()
        pk = 1
        response = self.client.delete('/note/' + str(pk) + '/')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(NoteBoard.objects.get(id=pk).visible)

        response = self.client.get('/note/' + str(pk) + '/')
        assert_error_response(response, ErrorMessageType.INCORRECT_DATA)

    def test_16_getNote_level_basic(self):
        self.login()
        pk = 1
        response = self.client.get('/note/level/' + str(pk) + '/')
        self.assertEqual(response.status_code, 200)

    def test_17_getNote_level_notExisting(self):
        self.login()
        pk = 200
        response = self.client.get('/note/level/' + str(pk) + '/')
        assert_error_response(response, ErrorMessageType.INCORRECT_DATA)

    def test_18_getNote_level_empty(self):
        self.login()
        pk = 2
        response = self.client.get('/note/level/' + str(pk) + '/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, '[]')