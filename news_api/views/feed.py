from ..models.schemas import FeedSchema
from ..models.schemas import PreferencesSchema
from ..models import Feed
from ..models import Preferences
from ..models import Account
from sqlalchemy.exc import IntegrityError, DataError
from pyramid_restful.viewsets import APIViewSet
from pyramid.response import Response

from urllib import parse


class FeedAPIView(APIViewSet):
    def list(self, request):
        """Ping database and send back list of all news articles. First, is for saved preferences (still needs to be refactored). Second, section is an unauthenticated route.
        """
        full_url = request.current_route_url() # 'http://localhost:6543/api/v1/feed/?pref=joy+analytical+confident'
        full_query = parse.urlparse(full_url).query # 'pref=joy+analytical+confident'

        if full_query:
            prefs_array = parse.parse_qs(full_query)['pref'][0].split(' ') # ['joy', 'analytical', 'confident']

            try:
                feed_sql = Feed.get_all(request)
            except (DataError, AttributeError):
                return Response(json='Not Found', status=404)

            feed_filtered = []
            # Create array of objects sorted by time (only articles with requested tone)

            for article in feed_sql:
                schema = FeedSchema()
                el = schema.dump(article).data

                if el['dom_tone'].lower() in prefs_array:
                    feed_filtered.append(el)

            # Currently feed is already sorted by time, but we'll keep this in case we need to sort by another key (i.e., vocab score, social media hits, etc)
            # feed_sorted = sorted(feed_filtered, key=lambda x: x['id'], reverse=True)

            return Response(json={'feed': feed_filtered}, status=200, headerlist=[('Access-Control-Allow-Origin', 'http://localhost:8080'), ('Content-Type', 'application/json')])

        else:
            try:
                feed_sql = Feed.get_all(request)
            # Eventually, use this except or an if conditional to hit the temp table.
            except (DataError, AttributeError):
                return Response(json='Not Found', status=404)

            schema = FeedSchema()
            feed = [schema.dump(article).data for article in feed_sql]
            # Create array of objects sorted by time (only articles with requested tone)

            # Currently feed is already sorted by time, but we'll keep this in case we need to sort by another key (i.e., vocab score, social media hits, etc)
            # feed_sorted = sorted(feed_filtered, key=lambda x: x['id'], reverse=True)

            return Response(json={'feed': feed}, status=200, headerlist=[('Access-Control-Allow-Origin', 'http://localhost:8080'), ('Content-Type', 'application/json')])

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

            feed_sorted = []

            for pref in preference_order:
                try:
                    tone_category = {}
                    tone_category[pref] = feed_parsed[pref]
                    feed_sorted.append(tone_category)
                except KeyError:
                    continue

            return Response(json={'feed': feed_sorted}, status=200, headerlist=[('Access-Control-Allow-Origin', 'http://localhost:8080'), ('Content-Type', 'application/json')])
