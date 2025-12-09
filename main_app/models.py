from django.db import models
from django.contrib.auth.models import User

class Library(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='libraries')  
    
    def __str__(self):
        return f"{self.name} (by {self.user.username})"



class Literature(models.Model):
    title = models.CharField(max_length=100)
    authors = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    url = models.TextField(max_length=250)
    
    
    literature_type = models.IntegerField(
        choices=[  
            (1, 'Book'),
            (2, 'Article'),
            (3, 'Journal'),
            (4, 'Conference Paper'),
            (5, 'Thesis'),
            
        ]
    )
    
    created_at = models.DateField(auto_now_add=True)  
    libraries = models.ManyToManyField('Library')  
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True)

    def __str__(self):
        return self.title