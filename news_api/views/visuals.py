from ..models.schemas import ArchivesSchema
from ..models import Archives
from sqlalchemy.exc import DataError
from pyramid_restful.viewsets import APIViewSet
from pyramid.response import Response
import numpy as np
import json
import pandas as pd
import bokeh.plotting as bk
import datetime as dt
# hover pan, zoom, reset, lables, etc tools
from bokeh.models import HoverTool, Label, BoxZoomTool, PanTool, ZoomInTool, ZoomOutTool, ResetTool
import requests
from collections import Counter
from math import pi
from urllib.parse import urlparse
import codecs
from bokeh.io import output_file, show
from bokeh.palettes import Category20c
from bokeh.plotting import figure
from bokeh.transform import cumsum


class VisualizationAPIViewset(APIViewSet):
    def retrieve(self, request, id=None):
        """Ping database and send back list of all news articles in archives
        """


        # test_parse = urllib.parse.parse_qs()

        body = ''

        id = id.lower()
        try:
            archives_sql = Archives.get_all(request)
        except (DataError, AttributeError):
            return Response(json='Not Found', status=404)
        sample_data = []
        for article in archives_sql:
            schema = ArchivesSchema()
            sample_data.append(schema.dump(article).data)


        parsed_url = request.current_route_url()
        chart_type = urlparse(parsed_url).query.split('=')[1]

        if chart_type == 'pie':
            df = pd.DataFrame(sample_data)
            df_source = df.loc[df['source'].str.lower() == id]
            df_count_anger = df_source.loc[df['dom_tone'] == 'Anger'].shape[0]
            df_count_fear = df_source.loc[df['dom_tone'] == 'Fear'].shape[0]
            df_count_joy = df_source.loc[df['dom_tone'] == 'Joy'].shape[0]
            df_count_sadness = df_source.loc[df['dom_tone'] == 'Sadness'].shape[0]
            df_count_analytical = df_source.loc[df['dom_tone'] == 'Analytical'].shape[0]
            df_count_confident = df_source.loc[df['dom_tone'] == 'Confident'].shape[0]
            df_count_tentative = df_source.loc[df['dom_tone'] == 'Tentative'].shape[0]

            # output_file("pie.html")

            x = Counter({
                'Anger': df_count_anger,
                'Fear': df_count_fear,
                'Joy': df_count_joy,
                'Sadness': df_count_sadness,
                'Analytical': df_count_analytical,
                'Confident': df_count_confident,
                'Tentative': df_count_tentative
            })

            data = pd.DataFrame.from_dict(dict(x), orient='index').reset_index().rename(index=str, columns={0: 'value', 'index': 'tone'})
            data['angle'] = data['value']/sum(x.values()) * 2*pi
            data['color'] = Category20c[len(x)]

            p = figure(plot_height=350, title=id, toolbar_location=None, tools="hover", tooltips="@tone: @value")

            p.wedge(x=0, y=1, radius=0.4,
                    start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
                    line_color="white", fill_color='color', legend='tone', source=data)

            p.axis.axis_label = None
            p.axis.visible = False
            p.grid.grid_line_color = None

            bk.save(
                p,
                './news_api/static/pie_{}.html'.format(id),
                title='source_versus_tone_{}'.format(id)
            )
            f = codecs.open(
                './news_api/static/pie_{}.html'.format(id),
                'r'
            )
            body = f.read()

        return Response(body=body, status=200)
