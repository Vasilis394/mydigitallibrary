from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import Literature, Library
from .serializers import UserSerializer, LiteratureSerializer, LibrarySerializer
from rest_framework.exceptions import PermissionDenied # include this additional import

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
    user = User.objects.get(username=request.user)  # Fetch user profile
    refresh = RefreshToken.for_user(request.user)  # Generate new refresh token
    return Response({
      'refresh': str(refresh),
      'access': str(refresh.access_token),
      'user': UserSerializer(user).data
    })

class LiteratureList(generics.ListCreateAPIView):
    queryset = Literature.objects.all()
    serializer_class = LiteratureSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
      # This ensures we only return literature belonging to the logged-in user
        user = self.request.user
        return Literature.objects.filter(user=user)

    def perform_create(self, serializer):
        # This associates the newly created literature with the logged-in user
        serializer.save(user=self.request.user)

class LiteratureDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Literature.objects.all()
    serializer_class = LiteratureSerializer
    lookup_field = 'id'

    def get_queryset(self):
        user = self.request.user
        return Literature.objects.filter(user=user)

    # add (override) the retrieve method below
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
    
        libraries_not_associated = Library.objects.exclude(id__in=instance.libraries.all())
        libraries_serializer = LibrarySerializer(libraries_not_associated, many=True)
        
        return Response({
            'literature': serializer.data,
            'libraries_not_associated': libraries_serializer.data
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

    # add (override) the retrieve method below
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)


        libraries_not_associated = Library.objects.exclude(id__in=instance.libraries.all())
        libraries_serializer = LibrarySerializer(libraries_not_associated, many=True)

        return Response({
            'literature': serializer.data,
            'libraries_not_associated': libraries_serializer.data
        })

class LibraryList(generics.ListCreateAPIView):
    queryset = Library.objects.all()
    serializer_class = LibrarySerializer
    

class LibraryDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Library.objects.all()
    serializer_class = LibrarySerializer
    lookup_field = 'id'
 
class AddLibraryToLiterature(APIView):
    def post(self, request, literature_id, library_id):
        literature = Literature.objects.get(id=literature_id)
        library = Library.objects.get(id=library_id)
        literature.libraries.add(library)
        return Response({'message': f'Library {library.name} added to literature {literature.title}'})
    
class RemoveLibraryFromLiterature(APIView):
    def post(self, request, literature_id, library_id):
        literature = Literature.objects.get(id=literature_id)
        library = Library.objects.get(id=library_id)
        literature.libraries.remove(library)

        return Response({'message': f'Library {library.name} removed to literature {literature.title}'})   