# main_app/views.py
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import Literature, Library
from .serializers import UserSerializer, LiteratureSerializer, LibrarySerializer, LibraryDetailSerializer
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
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Literature.objects.all()

    # In LiteratureDetail.retrieve() method, update the serializer usage:
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
    
        if request.user.is_authenticated:
            user_libraries = Library.objects.filter(user=request.user)
            libraries_not_associated = user_libraries.exclude(id__in=instance.libraries.all())
            user_associated_libraries = instance.libraries.filter(user=request.user)
        
            return Response({
                'literature': serializer.data,
                'libraries_not_associated': LibrarySerializer(libraries_not_associated, many=True).data,
                'user_associated_libraries': LibrarySerializer(user_associated_libraries, many=True).data,
                'user_owns': instance.user == request.user
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

# Update LibraryList view
class LibraryList(generics.ListCreateAPIView):
    serializer_class = LibrarySerializer  # Use basic serializer for list
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Library.objects.filter(user=self.request.user)
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# Update LibraryDetail view
class LibraryDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return Library.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        # Use detail serializer for retrieve, basic for update
        if self.request.method == 'GET':
            return LibraryDetailSerializer
        return LibrarySerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class AddLibraryToLiterature(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, literature_id, library_id):
        try:
            literature = Literature.objects.get(id=literature_id)
            library = Library.objects.get(id=library_id)
            
            # FIXED: Ensure the library belongs to the current user
            if library.user != request.user:
                return Response(
                    {'error': 'You do not own this library.'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            literature.libraries.add(library)
            return Response({
                'message': f'Library {library.name} added to literature {literature.title}',
                'library': LibrarySerializer(library).data
            })
        except Literature.DoesNotExist:
            return Response(
                {'error': 'Literature not found.'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Library.DoesNotExist:
            return Response(
                {'error': 'Library not found.'}, 
                status=status.HTTP_404_NOT_FOUND
            )

class RemoveLibraryFromLiterature(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, literature_id, library_id):
        try:
            literature = Literature.objects.get(id=literature_id)
            library = Library.objects.get(id=library_id)
            
            # FIXED: Ensure the library belongs to the current user
            if library.user != request.user:
                return Response(
                    {'error': 'You do not own this library.'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            literature.libraries.remove(library)
            return Response({
                'message': f'Library {library.name} removed from literature {literature.title}'
            })
        except Literature.DoesNotExist:
            return Response(
                {'error': 'Literature not found.'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Library.DoesNotExist:
            return Response(
                {'error': 'Library not found.'}, 
                status=status.HTTP_404_NOT_FOUND
            )