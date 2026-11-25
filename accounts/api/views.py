from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated

from .serializers import RegisterSerializer
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