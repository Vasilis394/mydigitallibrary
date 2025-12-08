from rest_framework import serializers
from .models import Literature, Library
from django.contrib.auth.models import User

class LibrarySerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = Library
        fields = '__all__'
        # If 'literature' is a ForeignKey to Literature, you might want:
        # read_only_fields = ('literature',)  # Note the comma to make it a tuple

class LiteratureSerializer(serializers.ModelSerializer):
    libraries = LibrarySerializer(many=True, read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)  # FIXED: Use PrimaryKeyRelatedField instead of ForeignKey
    
    class Meta:
        model = Literature
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user