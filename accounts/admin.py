from django.contrib import admin
from .models import login_history

from django.contrib.auth.admin import UserAdmin
from .models import User

# Register your models here.
admin.site.register(login_history)

admin.site.register(User)