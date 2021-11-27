"""This module will encode and parse the query string params."""

from urllib.parse import parse_qs
from flask.wrappers import Response
from bson.json_util import dumps


def parse_query_params(query_string):
    """
        Function to parse the query parameter string.
        """
    # Parse the query param string
    query_params = dict(parse_qs(query_string))
    # Get the value from the list
    query_params = {k: v[0] for k, v in query_params.items()}
    return query_params

def respose_success(obj):
    return Response(response=dumps(obj),
                    status=200,
                    headers= {'Access-Control-Allow-Origin': '*'},
                    mimetype="application/json")