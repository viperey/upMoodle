from upmoodle.routers.decorators.routing_decorators import authenticated, method
from upmoodle.services.rol import RolService


@authenticated
@method('GET')
def roles_list(request, **kwargs):
    return RolService.get_roles_list()