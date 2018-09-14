from ..models.schemas import FeedSchema
from ..models.schemas import PreferencesSchema
from ..models import Feed
from ..models import Preferences
from ..models import Account
from sqlalchemy.exc import IntegrityError, DataError
from pyramid_restful.viewsets import APIViewSet
from pyramid.response import Response


class FeedAPIView(APIViewSet):
    def list(self, request):
        """Ping database and send back list of all news articles
        """

        if request.authenticated_userid:
            account = Account.one(request, request.authenticated_userid)
            preferences = Preferences.one_by_account_id(request, account.id)

        schema = PreferencesSchema()
        preference_order = schema.dump(preferences).data['preference_order']

        try:
            feed_sql = Feed.get_all(request)
        except (DataError, AttributeError):
            return Response(json='Not Found', status=404)

        feed_parsed = {}

        for article in feed_sql:
            schema = FeedSchema()
            el = schema.dump(article).data
            try:
                feed_parsed[el['dom_tone'].lower()].append({'title': el['title'], 'url': el['url'], 'source': el['source'], 'date_published': el['date_published'], 'description': el['description'], 'image': el['image']})
            except KeyError:
                feed_parsed[el['dom_tone'].lower()] = [{'title': el['title'], 'url': el['url'], 'source': el['source'], 'date_published': el['date_published'], 'description': el['description'], 'image': el['image']}]
        print(feed_parsed)

        feed_sorted = {}

        for pref in preference_order:
            try:
                feed_sorted[pref] = feed_parsed[pref]
            except KeyError:
                continue

        return Response(json={'feed': feed_sorted}, status=200)
