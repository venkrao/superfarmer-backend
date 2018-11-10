# When a http request is sent, it carries access token, and some userdata.
# question is, for example, if user X claims to be sending the token, is the token really meant to be used for user X?
# i.e is he the one that generated it originally?
class CheckAccessTokenMixin:
    def __init__(self):
        pass

    def is_token_valid(self, request):


