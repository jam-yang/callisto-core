import logging

from six.moves.urllib.parse import parse_qs, urlsplit

from django.core.exceptions import ValidationError
from django.forms import URLField

logger = logging.getLogger(__name__)


def _clean_url(url):
    url_field = URLField()
    return url_field.clean(url.strip())


def _get_url_parts(url):
    url = _clean_url(url)
    return urlsplit(url)


def _get_initial_path(url_parts):
    return url_parts[2].strip('/').split('/')[0].lower()


generic_twitter_urls = [
    'i',
    'following',
    'followers',
    'who_to_follow',
    'settings',
    'search',
    'tos',
    'privacy',
    'about',
]


def twitter_validation_function(value):
    path = None
    try:
        url_parts = _get_url_parts(value)
        # check if acceptable domain
        domain = url_parts[1]
        if not (domain == 'twitter.com' or domain ==
                'www.twitter.com' or domain == 'mobile.twitter.com'):
            return None
        path = _get_initial_path(url_parts)
    except ValidationError:
        if value.startswith('@'):
            path = value[1:]
    if not path or path == "" or len(
            path) > 15 or path in generic_twitter_urls:
        return None
    else:
        return path


generic_fb_urls = [
    'messages',
    'hashtag',
    'events',
    'pages',
    'groups',
    'bookmarks',
    'lists',
    'developers',
    'topic',
    'help',
    'privacy',
    'campaign',
    'policies',
    'support',
    'settings',
    'games',
    'people', ]


def facebook_validation_function(url):
    try:
        url_parts = _get_url_parts(url)
        # check if acceptable domain
        domain = url_parts[1]
        if not (domain == 'facebook.com' or domain.endswith('.facebook.com')):
            return None
        path = _get_initial_path(url_parts)

        # old style numeric profiles
        if path == "profile.php":  # ex. https://www.facebook.com/profile.php?id=100010279981469
            path = parse_qs(url_parts[3]).get('id')[0]
        if path == 'people':  # ex. https://www.facebook.com/people/John-Doe/100013326345115
            path = url_parts[2].strip('/').split('/')[2].lower()

        # TODO: validate against allowed username characteristics
        # https://github.com/project-callisto/callisto-core/issues/181
        if not path or path == "" or path.endswith(
                '.php') or path in generic_fb_urls:
            return None
        else:
            return path
    except ValidationError:
        return None


'''
 NOTE: because identifiers are irreversibly encrypted and Facebook was the original matching identifier, Facebook
 identifiers are stored plain, with the prefix "www.facebook.com/" stripped. All other identifiers should be prefixed
 to allow for global uniqueness from Facebook profile identifiers.
'''
facebook_validation_info = {
    'validation': facebook_validation_function,
    'example': 'http://www.facebook.com/perpetratorname',
    'unique_prefix': ''}

'''
    potential options for identifier_domain_info, used in SubmitToMatchingForm
    identifier_domain_info is an ordered dictionary of matching identifiers
        key:
            the type of identifier requested
                example: 'Facebook profile URL' for Facebook
        value:
            a dictionary with
                a globally unique prefix (see note about Facebook's) to avoid cross-domain matches
                a validation function
                    should return None for invalid entries & return a minimal unique (within domain) path for valid
                an example input

    will return on first valid option tried
    see MatchingValidation.facebook_only (default)
'''


def perp_identifiers():
    return {
        'twitter': {
            'label': 'WHAT IS THEIR TWITTER HANDLE?',
            'id': 'twitter',
            'validation_function': twitter_validation_function,
            'example': 'http://www.twitter.com/perpetratorname or @perpetratorname',
            'unique_prefix': 'twitter',
        },
        'facebook': {
            'label': 'WHAT IS THEIR FACEBOOK URL?',
            'id': 'facebook',
            'validation_function': facebook_validation_function,
            'example': 'http://www.facebook.com/perpetratorname',
            'unique_prefix': '',
        },
        'mobile': {
            'label': 'WHAT IS THEIR MOBILE NUMBER?',
            'id': 'mobile',
            'validation_function': facebook_validation_function,
            'example': '(xxx) xxx xxxx',
            'unique_prefix': 'mobile',
        },
        'instagram': {
            'label': 'WHAT IS THEIR INSTAGRAM?',
            'id': 'instagram',
            'validation_function': facebook_validation_function,
            'example': 'http://www.instagram.com/perpetratorname',
            'unique_prefix': 'instagram',
        },
    }


def join_list_with_or(lst):
    if len(lst) < 2:
        return lst[0]
    all_but_last = ', '.join(lst[:-1])
    last = lst[-1]
    return ' or '.join([all_but_last, last])


class Validators(object):

    def __init__(self, validator):
        self.validator = validator

    def invalid(self):
        return 'Please enter a valid ' + self.validator['id']

    def titled(self):
        return "Perpetrator's " + self.validator['id']

    def examples(self):
        return 'ex. ' + self.validator['example']
