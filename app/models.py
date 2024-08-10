
from django.db import models
class MongoUser(models.Model):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(max_length=254, unique=True)
    additional_data = models.JSONField()
    
    class Meta:
        db_table = 'skindetect'

    def __str__(self):
        return self.username
