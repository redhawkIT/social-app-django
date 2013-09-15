from functools import wraps

from pyramid.httpexceptions import HTTPNotFound, HTTPForbidden

from social.utils import setting_name, module_member
from social.strategies.utils import get_strategy
from social.backends.utils import user_backends_data


DEFAULTS = {
    'STORAGE': 'social.apps.pyramid_app.models.PyramidStorage',
    'STRATEGY': 'social.strategies.pyramid_strategy.PyramidStrategy'
}


def get_helper(request, name):
    return request.registry.settings.get(setting_name(name),
                                         DEFAULTS.get(name, None))


def load_strategy(request, *args, **kwargs):
    backends = get_helper(request, 'AUTHENTICATION_BACKENDS')
    strategy = get_helper(request, 'STRATEGY')
    storage = get_helper(request, 'STORAGE')
    return get_strategy(backends, strategy, storage, request=request,
                        *args, **kwargs)


def strategy(redirect_uri=None):
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            backend = request.matchdict.get('backend')
            if not backend:
                return HTTPNotFound('Missing backend')

            uri = redirect_uri
            if uri and not uri.startswith('/'):
                uri = request.route_url(uri, backend=backend)
            request.strategy = load_strategy(request, backend=backend,
                                             redirect_uri=uri, *args, **kwargs)
            return func(request, *args, **kwargs)
        return wrapper
    return decorator


def login_required(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        is_logged_in = module_member(
            request.strategy.setting('LOGGEDIN_FUNCTION')
        )
        if not is_logged_in(request):
            raise HTTPForbidden('Not authorized user')
        return func(request, *args, **kwargs)
    return wrapper


def backends(request, user):
    """Load Social Auth current user data to context under the key 'backends'.
    Will return the output of social.backends.utils.user_backends_data."""
    storage = module_member(get_helper(request, 'STORAGE'))
    return {
        'backends': user_backends_data(
            user, get_helper(request, 'AUTHENTICATION_BACKENDS'), storage
        )
    }
