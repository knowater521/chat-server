from django.contrib import admin
from . import models
# Register your models here.

admin.site.register(models.Users)
admin.site.register(models.Friends)
admin.site.register(models.Off_msg)
admin.site.register(models.Make_friends_requests)