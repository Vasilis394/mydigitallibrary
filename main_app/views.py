# main_app/views.py
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import Literature, Library
from .serializers import UserSerializer, LiteratureSerializer, LibrarySerializer
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticatedOrReadOnly  # Add this import

# Create your views here.

class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        user = User.objects.get(username=response.data['username'])
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': response.data
        })

# User Login
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            })
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)

# User Verification
class VerifyUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = User.objects.get(username=request.user)
        refresh = RefreshToken.for_user(request.user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        })

# UPDATE THIS: Allow guests to view literature
class LiteratureList(generics.ListCreateAPIView):
    serializer_class = LiteratureSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # Changed from IsAuthenticated

    def get_queryset(self):
        # Guests can see all literature
        # Users can see all literature too (or filter by user if you prefer)
        return Literature.objects.all()

    def perform_create(self, serializer):
        # Only authenticated users can create
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            raise PermissionDenied({"message": "You must be logged in to create literature."})

# UPDATE THIS: Allow guests to view details
class LiteratureDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Literature.objects.all()
    serializer_class = LiteratureSerializer
    lookup_field = 'id'
    permission_classes = [IsAuthenticatedOrReadOnly]  # Changed from IsAuthenticated

    def get_queryset(self):
        # Guests can view any literature
        return Literature.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        # Only show libraries for authenticated users
        if request.user.is_authenticated:
            libraries_not_associated = Library.objects.exclude(id__in=instance.libraries.all())
            libraries_serializer = LibrarySerializer(libraries_not_associated, many=True)
            return Response({
                'literature': serializer.data,
                'libraries_not_associated': libraries_serializer.data,
                'user_owns': instance.user == request.user  # Add this to check ownership
            })
        else:
            return Response({
                'literature': serializer.data,
                'user_owns': False
            })

    def perform_update(self, serializer):
        literature = self.get_object()
        if literature.user != self.request.user:
            raise PermissionDenied({"message": "You do not have permission to edit this literature."})
        serializer.save()

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise PermissionDenied({"message": "You do not have permission to delete this literature."})
        instance.delete()

# UPDATE THIS: Libraries are user-specific
class LibraryList(generics.ListCreateAPIView):
    serializer_class = LibrarySerializer
    permission_classes = [permissions.IsAuthenticated]  # Only authenticated users

    def get_queryset(self):
        # Users only see their own libraries
        return Library.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class LibraryDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = LibrarySerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        # Users can only access their own libraries
        return Library.objects.filter(user=self.request.user)

class AddLibraryToLiterature(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, literature_id, library_id):
        literature = Literature.objects.get(id=literature_id)
        library = Library.objects.get(id=library_id)
        
        # Check if user owns the library
        if library.user != request.user:
            raise PermissionDenied({"message": "You do not own this library."})
        
        literature.libraries.add(library)
        return Response({'message': f'Library {library.name} added to literature {literature.title}'})

class RemoveLibraryFromLiterature(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, literature_id, library_id):
        literature = Literature.objects.get(id=literature_id)
        library = Library.objects.get(id=library_id)
        
        # Check if user owns the library
        if library.user != request.user:
            raise PermissionDenied({"message": "You do not own this library."})
        
        literature.libraries.remove(library)
        return Response({'message': f'Library {library.name} removed from literature {literature.title}'})