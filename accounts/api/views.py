from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .serializers import RegisterSerializer, LoginSerializer
from ..models import User
from .utils import send_activation_mail

class RegisterView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        ''' Register an inactive user, send an activation email, and return the registration details. '''
        serializer = RegisterSerializer(data=request.data)# Serializer mit den request.data instanzieren
        serializer.is_valid(raise_exception=True) # prüfen, ob die Daten valide sind
        user = serializer.save() # save() aufrufen und damit die create() Methode
        activation_token = default_token_generator.make_token(user)
        
        send_activation_mail(request, user, activation_token) # Versandfunktion aufrufen und user + activation_token übergeben
        
        return Response({
            "user": {
                "id": user.id,
                "email": user.email,
            },
            "token": "activation_token"
            }, status=status.HTTP_201_CREATED) 

class ActivationView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, uidb64, token):
        ''' Decode the user ID, validate the activation token, and activate the account. '''
        try:
            uid = urlsafe_base64_decode(uidb64).decode() # Ergebnis die Benutzer ID # mit decode werden die Bytes in einen string umgewandelt.
            user = User.objects.get(pk=uid) # Benutzer suchen
        except (ValueError, TypeError, UnicodeDecodeError, User.DoesNotExist):
            return Response(
                {"error": "Ungültiger Aktivierungslink."
                    },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not default_token_generator.check_token(user, token): # den Token prüfen mit check_tocken(user, token) - user: der gefundene Benutzer, token: der Token aus der URL
            return Response(
                {"error": "Ungültiger oder abgelaufener Token"}, status=status.HTTP_400_BAD_REQUEST
            )
        # Bei gültigem Token user.is_active = True setzen und speichern.
        user.is_active = True
        user.save()

        return Response({
            "message": "Account successfully activated."
        }, status=status.HTTP_200_OK)
        

class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        ''' Authenticate the user, set JWT access and refresh tokens as HttpOnly cookies, and return the user details. '''
        serializer = LoginSerializer(data=request.data) # email und password werden an den Serializer übergeben
        serializer.is_valid(raise_exception=True) # hier werden die Felder mit der validate() Methode geprüft
        user = serializer.validated_data['user'] # Benutzer wird ausgelesen
        
        refresh_token = RefreshToken.for_user(user) # erzeugt einen refresh Token
        access_token = str(refresh_token.access_token) # über den RefreshToken erhält man den zugehörigen access token | Der Access-Token authentifiziert spätere API-Anfragen. Der länger gültige Refresh-Token ermöglicht es, einen neuen Access-Token anzufordern.
        
        response = Response({
                    "detail": "Login successful",
                    "user": {
                        "id": user.id,
                        "username": user.email
                    }
                }, status=status.HTTP_200_OK)
        
        response.set_cookie(
            key="access_token", # Name des Cookies, unter dem der Browser es speichert und bei Requests mitsendet
            value=access_token,  # Der eigentliche Inhalt (hier der JWT-Access-Token als String)
            httponly=True, # Schutz vor XSS: JavaScript im Browser (document.cookie) kann das Cookie nicht auslesen
            secure=True,  # Erzwingt HTTPS-Übertragung
            samesite="Lax", # CSRF-Schutz: Cookie wird bei normalen Navigationen mitgesendet
            # max_age=300,  # Lebensdauer des Cookies in Sekunden (300 Sekunden = 5 Minuten); danach löscht der Browser das Cookie automatisch
            )
        response.set_cookie(
            key="refresh_token",
            value=str(refresh_token),
            httponly=True,
            secure=True,
            samesite="Lax",
            
        )
        
        return response
        
        
class LogoutView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        ''' Blacklist the refresh token, delete the authentication cookies, and return a logout confirmation. '''
        try:
            refresh_token = request.COOKIES.get("refresh_token")
            if not refresh_token:
                return Response({"error": "Refresh Token fehlt"}, status=status.HTTP_400_BAD_REQUEST)
            token = RefreshToken(refresh_token)     
            token.blacklist()
            
            response =  Response({
                "detail": "Logout successful! All tokens will be deleted. Refresh token is now invalid."
                }, status=status.HTTP_200_OK)
            
            response.delete_cookie("access_token") # Die Methode ergänzt die Antwort um einen abgelaufenen Cookie. Sobald der Browser die Antwort erhält, entfernt er den entsprechenden gespeicherten Cookie.
            response.delete_cookie("refresh_token")
            
            return response
            
        except TokenError:
            return Response(status=status.HTTP_400_BAD_REQUEST)