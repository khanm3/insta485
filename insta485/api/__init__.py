"""Insta485 REST API."""

from insta485.api.posts import rest_get_post
from insta485.api.posts import rest_get_posts
from insta485.api.index import rest_get_index
from insta485.api.likes import rest_create_like
from insta485.api.likes import rest_delete_like
from insta485.api.comments import rest_create_comment
from insta485.api.comments import rest_delete_comment
from insta485.api.helpers import InvalidUsage
from insta485.api.helpers import handle_invalid_usage
