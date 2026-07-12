from django.db import models

# Create your models here.
class Bill(models.Model):
    bno=models.IntegerField(primary_key=True)
    bdate=models.DateField()
    cname=models.CharField(max_length=100)

    def __str__(self):
        return self.cname
    
