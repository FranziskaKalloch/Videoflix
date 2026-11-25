from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken


from .serializers import VideoListSerializer
from ..models import Video


class CookieJWTAuthentication(JWTAuthentication): # Prüft bei einer geschützten Anfrage den Access-Token aus dem Cookie und ermittelt den Benutzer.
    '''Validate the access token from the cookie and return the authenticated user and token.'''
    cookie_name = "access_token"
    
    def authenticate(self, request):
        token = request.COOKIES.get(self.cookie_name)
        
        if token is None:
            return None
        
        validated_token = self.get_validated_token(token) # Die geerbte Methode prüft unter anderem Signatur, Ablaufzeit und Token-Typ.
        user = self.get_user(validated_token)
        
        return (user, validated_token) # Dieses Tupel ist die von DRF erwartete Rückgabe. Damit belegt DRF request.user und request.auth.
            

class VideoListView(ListAPIView):
    ''' Return video metadata for users authenticated via a JWT cookie. '''
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]
    queryset = Video.objects.all()
    serializer_class = VideoListSerializer
    
    