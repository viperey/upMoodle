import uuid

from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.datastructures import MultiValueDictKeyError
from django.views.decorators.csrf import csrf_exempt

from backend import settings
from backend.settings import SESSION_COOKIE_NAME
from rest.JSONResponse import JSONResponse, JSONResponseID
from rest.MESSAGES_ID import REQUEST_CANNOT, INCORRECT_DATA, ALREADY_CONFIRMED, DISABLED_COOKIES, \
    UNCONFIRMED_EMAIL, SUCCESS_LOGIN, UNAUTHORIZED, RECOVER_PASS_EMAIL, ACCOUNT_VALIDATED
from rest.controllers.Exceptions.requestException import RequestExceptionByCode, RequestExceptionByMessage, \
    RequestException
from rest.controllers.controllers import check_cookies, get_email_confirmation_message, cookies_are_ok, \
    get_random_password, send_recover_password_email, check_request_method
from rest.models import User, Level, FileType
from rest.orm.serializers import LevelSerializer, FileTypeSerializer
from rest.orm.unserializers import unserialize_user


@csrf_exempt
def signup_sys(request):
    try:
        check_cookies(request)
        if request.method == 'POST':
            sessionCookie = request.COOKIES[SESSION_COOKIE_NAME]
            user = unserialize_user(request.POST, sessionToken=sessionCookie,
                                    fields=['email', 'password', 'nick', 'name'])
            send_mail('Email confirmation',
                      get_email_confirmation_message(request, cookie=sessionCookie),
                      'info@upmoodle.com', [user.email],
                      fail_silently=False)
            user.save()
            return JSONResponse({"userId": user.id}, status=200)
        else:
            return RequestExceptionByCode(REQUEST_CANNOT).jsonResponse
    except ValidationError as v:
        r = RequestExceptionByMessage(v)
        return r.jsonResponse
    except RequestException as r:
        return r.jsonResponse
    except Exception:
        return RequestExceptionByCode(INCORRECT_DATA).jsonResponse


def confirmEmail_sys(request):
    try:
        check_request_method(request, method='POST')
        token = request.POST['token']
        user = User.objects.get(sessionToken=token)
        if user.confirmedEmail:
            return RequestExceptionByCode(ALREADY_CONFIRMED).jsonResponse
        else:
            user.confirmedEmail = True
            user.save()
            return JSONResponseID(ACCOUNT_VALIDATED)
    except RequestException as r:
        return r.jsonResponse
    except ObjectDoesNotExist or OverflowError or ValueError:
        return RequestExceptionByCode(INCORRECT_DATA).jsonResponse


def login_sys(request):
    try:
        if not cookies_are_ok(request):
            exception = RequestExceptionByCode(DISABLED_COOKIES)
            exception.jsonResponse.set_cookie(SESSION_COOKIE_NAME, uuid.uuid4().hex)
            return exception.jsonResponse
        elif request.method == 'POST':
            session_key = request.COOKIES[SESSION_COOKIE_NAME]
            emailIn = request.POST['email']
            passwordIn = request.POST['password']
            user = User.objects.get(email=emailIn, password=passwordIn)
            if not user.confirmedEmail:
                return RequestExceptionByCode(UNCONFIRMED_EMAIL).jsonResponse
            else:
                user.sessionToken = session_key
                user.lastTimeActive = timezone.now()
                user.save()
                jsonResponse = JSONResponseID(SUCCESS_LOGIN)
                jsonResponse.set_cookie(settings.SESSION_COOKIE_NAME, session_key)
                return jsonResponse
        else:
            raise RequestExceptionByCode(REQUEST_CANNOT)
    except ObjectDoesNotExist or MultiValueDictKeyError as e:
        return RequestExceptionByCode(INCORRECT_DATA).jsonResponse
    except MultiValueDictKeyError:
        return RequestExceptionByCode(INCORRECT_DATA).jsonResponse
    except RequestException as r:
        return r.jsonResponse


@csrf_exempt
def logout_sys(request):
    try:
        if not cookies_are_ok(request):
            return RequestExceptionByCode(DISABLED_COOKIES).jsonResponse
        elif request.method == 'POST':
            session_key = request.COOKIES[SESSION_COOKIE_NAME]
            user = User.objects.get(sessionToken=session_key)
            user.sessionToken = ''
            user.save()
            jsonResponse = JSONResponse({"null"}, status=200)
            # jsonResponse.delete_cookie(SESSION_COOKIE_NAME)
            jsonResponse.delete_cookie(SESSION_COOKIE_NAME)
            return jsonResponse
        else:
            raise RequestExceptionByCode(REQUEST_CANNOT)
    except Exception:
        return JSONResponse({"null"}, status=400)


def recoverPassword_sys(request):
    try:
        if request.method == 'POST':
            emailRequest = request.POST['email']
            user = User.objects.get(email=emailRequest)
            if not user.confirmedEmail:
                raise RequestExceptionByCode(UNCONFIRMED_EMAIL)
            elif user.banned:
                raise RequestExceptionByCode(UNAUTHORIZED)
            else:
                password = get_random_password()
                send_recover_password_email(user.email, password)
                user.password = password
                user.save()
        return JSONResponseID(RECOVER_PASS_EMAIL)
    except RequestException as r:
        return r.jsonResponse
    except Exception:
        return RequestExceptionByCode(INCORRECT_DATA).jsonResponse


def subjectsTree_get(id=None):
    if not id:
        subjects = Level.objects.filter(parent=None, visible=True)
        serializer = LevelSerializer(subjects, many=True)
        for item in serializer.data:
            item['children'] = subjectsTree_get(item.get('id'))
        return JSONResponse(serializer.data)
    else:
        subjects = Level.objects.filter(parent=id, visible=True)
        serializer = LevelSerializer(subjects, many=True)
        for item in serializer.data:
            item['children'] = subjectsTree_get(item.get('id'))
            if not item['children'] or len(item['children']) is 0:
                del item['children']
        return serializer.data


def subjectsTree_get_ids(id=None):
    if not id:
        subjects = Level.objects.filter(parent=None, visible=True)
        ids = []
        for subject in subjects:
            ids.append(subject.id)
            ids.extend(subjectsTree_get_ids(subject.id))
        return list(set(ids))
    else:
        subjects = Level.objects.filter(parent=id, visible=True)
        ids = [id]
        for subject in subjects:
            ids.append(subject.id)
            ids.extend(subjectsTree_get_ids(subject.id))
        return list(set(ids))


def fileTypes_get():
    filesTypes = FileType.objects.all()
    serializer = FileTypeSerializer(filesTypes, many=True)
    return JSONResponse(serializer.data)