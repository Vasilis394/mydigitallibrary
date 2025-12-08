from django.contrib import admin
# Add the include function to the import
from django.urls import path, include
from .views import LiteratureList, LiteratureDetail, LibraryList, LibraryDetail, CreateUserView, LoginView, VerifyUserView

urlpatterns = [
    path('users/register/', CreateUserView.as_view(), name='register'),
    path('users/login/', LoginView.as_view(), name='login'),
    path('users/token/refresh/', VerifyUserView.as_view(), name='token_refresh'),
    path('literatures/', LiteratureList.as_view(), name='literature-list'),
    path('literatures/<int:id>/', LiteratureDetail.as_view(), name='literature-detail'),
    path('libraries/', LibraryList.as_view(), name='library-list'),
	path('libraries/<int:id>/', LibraryDetail.as_view(), name='library-detail'),
    
]