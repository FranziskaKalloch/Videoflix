from django.contrib.auth import authenticate # prüft die Zugangsdaten über Djangos Authentifizierungs Backend

from rest_framework import serializers
from ..models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirmed_password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'confirmed_password')
    
    def validate(self, data):
        ''' Validate that the passwords match and meet the minimum length requirement. '''
        password = data['password']
        confirmed_password = data['confirmed_password']
        
        if password != confirmed_password:
            raise serializers.ValidationError({'password': "Passwörter stimmen nicht überein"})
        
        if len(password) < 8:
            raise serializers.ValidationError({"password": "Das Passwort muss mindestens 8 Zeichen haben"})
        
        return data
    
    def create(self, validated_data):
        ''' Create an inactive user with a hashed password. '''
        email = validated_data['email']
        password = validated_data['password']
        
        user = User.objects.create_user(
            email =  email,
            password = password
        )
        
        return user
    
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True)        
    password = serializers.CharField(write_only=True, trim_whitespace=False)
            
    def validate(self, validated_data):
        ''' Validate the login credentials and add the authenticated user to the validated data. '''
        email = validated_data['email']
        password = validated_data['password']
            
        user = authenticate(email=email, password=password)
        
        if user is None:
            raise serializers.ValidationError("Ungültige Email Adresse oder falsches Passwort")
        
        validated_data['user'] = user # User wird in den geprüften Daten gespeichert
        
        return validated_data # Diesen Rückgabewert stellt der Serializer nach erfolgreicher Validierung als serializer.validated_data bereit.

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    
    def validate(self, validated_data):
        ''' Validate that a user with the provided email address exists. '''
        email = validated_data['email']
        
        user_exists = User.objects.filter(email=email).exists()
        
        if not user_exists:
            raise serializers.ValidationError("Ein Benutzer mit dieser Email existiert nicht")
        
        return validated_data