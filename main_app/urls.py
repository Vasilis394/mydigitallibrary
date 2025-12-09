
from django.contrib import admin
from django.urls import path, include
from .views import (
    LiteratureList, LiteratureDetail, 
    LibraryList, LibraryDetail, 
    CreateUserView, LoginView, VerifyUserView,
    AddLibraryToLiterature, RemoveLibraryFromLiterature
)

urlpatterns = [
    path('users/register/', CreateUserView.as_view(), name='register'),
    path('users/login/', LoginView.as_view(), name='login'),
    path('users/token/refresh/', VerifyUserView.as_view(), name='token_refresh'),
    
    
    path('literatures/', LiteratureList.as_view(), name='literature-list'),
    path('literatures/<int:id>/', LiteratureDetail.as_view(), name='literature-detail'),
    
    
    path('libraries/', LibraryList.as_view(), name='library-list'),
    path('libraries/<int:id>/', LibraryDetail.as_view(), name='library-detail'),
    
    
    path('literatures/<int:literature_id>/add-library/<int:library_id>/', 
         AddLibraryToLiterature.as_view(), name='add-library'),
    path('literatures/<int:literature_id>/remove-library/<int:library_id>/', 
         RemoveLibraryFromLiterature.as_view(), name='remove-library'),
]