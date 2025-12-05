from django.contrib import admin
# import your models here
from .models import Literature, Library

# Register your models here
admin.site.register(Literature)
admin.site.register(Library)