from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.http import HttpResponse
from django.utils.datastructures import MultiValueDictKeyError

from backend.settings import SESSION_COOKIE_NAME
from rest.JSONResponse import JSONResponse, JSONResponseID
from rest.controllers.Exceptions.requestException import RequestException, RequestExceptionByCode, \
    RequestExceptionByMessage
from rest.controllers.controllers import check_authorized_author, is_authorized_author
from rest.models import File, Level, User, FileType
from rest.models.message.errorMessage import ErrorMessageType
from rest.models.message.message import MessageType
from rest.orm.serializers import FileSerializer, FileTypeSerializer
from rest.orm.unserializer import unserialize_file_binary, unserialize_file


class FileService:

    def __init__(self):
        pass

    @staticmethod
    def add(session_token=None, data=None, files=None):
        try:

            uploader_id = User.objects.get(sessionToken=session_token).id
            is_authorized_author(session_token=session_token, author_id=uploader_id, level=True)

            Level.validate_exists_level(data['subject_id'])

            fields = ['uploader_id', 'subject_id', 'name', 'text', 'fileType_id']
            new_file = unserialize_file_binary(data, fields=fields, optional=True, binary=files['file'])
            new_file.save()
            return JSONResponseID(MessageType.FILE_UPLOADED)
        except Exception:
            return RequestExceptionByCode(ErrorMessageType.INCORRECT_DATA).jsonResponse

    @staticmethod
    def delete(session_token=None, file_hash=None, **kwargs):
        try:
            model = File.objects.get(hash=file_hash)
            is_authorized_author(session_token=session_token, author_id=model.uploader_id, level=True, same=False)
            model.visible = False
            model.save()
            return JSONResponseID(MessageType.FILE_REMOVED)
        except RequestException as r:
            return r.jsonResponse
        except ObjectDoesNotExist:
            return RequestExceptionByCode(ErrorMessageType.INCORRECT_DATA).jsonResponse

    @staticmethod
    def metadata_get(file_hash=None, **kwargs):
        try:
            file_returning = File.objects.filter(hash=file_hash, visible=True)
            serializer = FileSerializer(file_returning, many=True)
            return JSONResponse(serializer.data)
        except RequestException as r:
            return r.jsonResponse
        except ObjectDoesNotExist or OverflowError or ValueError:
            return RequestExceptionByCode(ErrorMessageType.INCORRECT_DATA).jsonResponse

    @staticmethod
    def metadata_update(session_token=None, file_hash=None, data=None):
        try:

            file_original = File.objects.get(hash=file_hash)
            is_authorized_author(session_token=session_token, author_id=file_original.uploader_id, level=True, same=False)

            fields = ['name', 'text', 'fileType_id']
            file_updated = unserialize_file(data, fields=fields, optional=True)

            file_original.update(file_updated, fields)
            file_original.lastUpdater_id = User.get_signed_user_id(session_token)
            file_original.save()

            return JSONResponseID(MessageType.FILE_UPDATED)
        except RequestException as r:
            return r.jsonResponse
        except ObjectDoesNotExist or OverflowError or ValueError or MultiValueDictKeyError:
            return RequestExceptionByCode(ErrorMessageType.INCORRECT_DATA).jsonResponse
        except ValidationError as v:
            return RequestExceptionByMessage(v).jsonResponse

    @staticmethod
    def binary_get(file_hash=None, **kwargs):
        try:
            response_file = File.objects.get(hash=file_hash)

            response = HttpResponse(response_file.file)
            response['Content-Disposition'] = 'attachment; filename=' + response_file.filename
            return response
        except RequestException as r:
            return r.jsonResponse
        except ObjectDoesNotExist or OverflowError or ValueError:
            return RequestExceptionByCode(ErrorMessageType.INCORRECT_DATA).jsonResponse


class FileTypeService:
    def __init__(self):
        pass

    @staticmethod
    def get():
        try:
            return FileTypeService.__get__file_types()
        except RequestException as r:
            return r.jsonResponse
        except ObjectDoesNotExist or OverflowError or ValueError:
            return RequestExceptionByCode(ErrorMessageType.INCORRECT_DATA).jsonResponse

    @staticmethod
    def __get__file_types():
        files_types = FileType.objects.all()
        serializer = FileTypeSerializer(files_types, many=True)
        return JSONResponse(serializer.data)
