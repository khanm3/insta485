"""Views, one for each Insta485 page."""
from insta485.views.index import show_index
from insta485.views.accounts import get_account_login
from insta485.views.accounts import get_account_create
from insta485.views.accounts import get_account_delete
from insta485.views.accounts import get_account_edit
from insta485.views.accounts import get_account_password
from insta485.views.follow import get_followers
from insta485.views.follow import get_following
from insta485.views.users import get_user
from insta485.views.explore import get_explore
#from insta485.views.posts import get_post
