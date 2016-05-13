from upmoodle.controllers.decorators.exceptions import zero_exceptions
from upmoodle.controllers.decorators.router import authenticated, method
from upmoodle.routers.response.jsonfactory import JsonResponseFactory
from upmoodle.services.rol import RolService


@authenticated
@method('GET')
@zero_exceptions
def roles_list(request, **kwargs):
    roles = RolService.get_roles_list()
    return JsonResponseFactory().ok().body(obj=roles).build()
