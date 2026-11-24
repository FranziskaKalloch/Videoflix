from django.contrib.auth.tokens import default_token_generator

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
            "token": activation_token
            }, status=status.HTTP_201_CREATED) 

class ActivationView(APIView):
    pass