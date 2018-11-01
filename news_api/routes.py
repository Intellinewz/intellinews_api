from pyramid_restful.routers import ViewSetRouter
from .views.feed import FeedAPIView
from .views.preferences import PreferencesAPIView
from .views.auth import AuthAPIView
from .views.visuals import VisualizationAPIViewset


def includeme(config):
    """Route adding and configuration
    """
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')  # TODO: Go into default.py and change homeview.

    router = ViewSetRouter(config)
    router.register('api/v1/auth/{auth}', AuthAPIView, 'auth')
    # TODO: Add in permissions for preferences.
    router.register('api/v1/preferences', PreferencesAPIView, 'preferences', permission='admin')
    # TODO: Add in permissions for feed.
    router.register('api/v1/feed', FeedAPIView, 'feed')
    router.register('api/v1/visuals', VisualizationAPIViewset, 'visuals')
