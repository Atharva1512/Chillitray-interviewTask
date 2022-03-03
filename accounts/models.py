from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.contrib.auth import get_user_model

# Create your models here.

class User(AbstractUser):
    email_verify = models.BooleanField(default=False)
    sign_in_attempt_cnt =models.IntegerField(default=0)

    def __str__(self):
        return str(self.username) 

class login_history(models.Model):
    hist_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    login_dt= models.DateTimeField(auto_now_add=False)

    def __str__(self):
        return str(self.hist_id) + ': ' + str(self.user)