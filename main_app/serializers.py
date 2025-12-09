from rest_framework import serializers
from .models import Literature, Library
from django.contrib.auth.models import User


class LibrarySerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    literature_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Library
        fields = ['id', 'name', 'user', 'literature_count']
    
    def get_literature_count(self, obj):
        return obj.literature_set.count()

class LibraryDetailSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    literature = serializers.SerializerMethodField()
    literature_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Library
        fields = ['id', 'name', 'user', 'literature', 'literature_count']
    
    def get_literature(self, obj):
        literature = obj.literature_set.all()
        return SimpleLiteratureSerializer(literature, many=True).data
    
    def get_literature_count(self, obj):
        return obj.literature_set.count()

class SimpleLiteratureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Literature
        fields = ['id', 'title', 'authors', 'description', 'literature_type', 'url', 'created_at']

class LiteratureSerializer(serializers.ModelSerializer):
    libraries = LibrarySerializer(many=True, read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    
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