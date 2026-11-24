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