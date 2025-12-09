from django.db import models
from django.contrib.auth.models import User

class Library(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='libraries')  # Remove null=True
    
    def __str__(self):
        return f"{self.name} (by {self.user.username})"



class Literature(models.Model):
    title = models.CharField(max_length=100)
    authors = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    url = models.TextField(max_length=250)
    
    # FIXED: Remove max_length from IntegerField
    literature_type = models.IntegerField(
        choices=[  # Optional: Add choices if you have specific types
            (1, 'Book'),
            (2, 'Article'),
            (3, 'Journal'),
            (4, 'Conference Paper'),
            (5, 'Thesis'),
            # Add more as needed
        ]
    )
    
    created_at = models.DateField(auto_now_add=True)  # Consider using auto_now_add
    libraries = models.ManyToManyField('Library')  # Use string reference if Library is defined below
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True)

    def __str__(self):
        return self.title