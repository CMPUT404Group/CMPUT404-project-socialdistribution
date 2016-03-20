# Modified from https://github.com/tomchristie/django-rest-framework/blob/master/rest_framework/authentication.py

from __future__ import unicode_literals

import base64

from django.contrib.auth import authenticate, get_user_model
from django.middleware.csrf import CsrfViewMiddleware
from django.utils.translation import ugettext_lazy as _

from rest_framework.authentication import BasicAuthentication
from rest_framework import HTTP_HEADER_ENCODING, exceptions

from api.models import Author
from django.utils.functional import SimpleLazyObject

def get_authorization_header(request):
    """
    Return request's 'Authorization:' header, as a bytestring.
    Hide some test client ickyness where the header can be unicode.
    """
    auth = request.META.get('HTTP_AUTHORIZATION', b'')
    if isinstance(auth, type('')):
        # Work around django test client oddness
        auth = auth.encode(HTTP_HEADER_ENCODING)
    return auth


class HostBasicAuthentication(BasicAuthentication):
    """
    HTTP Basic authentication against username/password.
    """
    www_authenticate_realm = 'api'

    def authenticate(self, request):
        """
        Returns a `User` if a correct username and password have been supplied
        using HTTP Basic authentication.  Otherwise returns `None`.
        """
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != b'basic':
            return None

        if len(auth) == 1:
            msg = _('Invalid basic header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _('Invalid basic header. Credentials string should not contain spaces.')
            raise exceptions.AuthenticationFailed(msg)

        try:
            # auth_parts = [ userid , ":", host:password ]
            auth_parts = base64.b64decode(auth[1]).decode(HTTP_HEADER_ENCODING).partition(':')
        except (TypeError, UnicodeDecodeError):
            msg = _('Invalid basic header. Credentials not correctly base64 encoded.')
            raise exceptions.AuthenticationFailed(msg)

        user_id, host = auth_parts[0].split("@")
        custom_auth_parts = [ user_id, host, auth_parts[2]]
        # my_auth_parts => [ host , ":", password ]
        # my_auth_parts = auth_parts[2].partition(":")
        # custom_auth_parts => [ userid, host, password ]
        # custom_auth_parts = [ auth_parts[0], my_auth_parts[0], my_auth_parts[2] ]
        # print "BasicAuthentication: custom_auth_parts : ",
        # print custom_auth_parts
        request.META["HTTP_REMOTE_USER"] = user_id
        # userid, password = auth_parts[0], auth_parts[2] # ORIGINAL
        # userid, password = custom_auth_parts[1] + "a", custom_auth_parts[2] + "a"
        userid, password = custom_auth_parts[1], custom_auth_parts[2]

        userObj = self.authenticate_credentials(userid, password)

        # print "CUSTOM BasicAuthentication :"
        # print userObj
        
        # print "\tREQUEST.USER : ",
        # print request.user
        # request.user = SimpleLazyObject(lambda: get_user(request))

        # return self.authenticate_credentials(userid, password) # ORIGINAL

        # author = Author.objects.get(user=userObj[0])
        # print repr(author)
        # request.user = author
        # request.user = userObj[0]
        # print request.user
        # request.author = author
        # print request.author
        # print request.auth

        return userObj


    def authenticate_credentials(self, userid, password):
        """
        Authenticate the userid and password against username and password.
        """
        credentials = {
            get_user_model().USERNAME_FIELD: userid,
            'password': password
        }
        user = authenticate(**credentials)

        if user is None:
            raise exceptions.AuthenticationFailed(_('Invalid username/password.'))

        if not user.is_active:
            raise exceptions.AuthenticationFailed(_('User inactive or deleted.'))

        return (user, None)

    def authenticate_header(self, request):
        return 'Basic realm="%s"' % self.www_authenticate_realm

