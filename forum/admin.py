from django.contrib import admin

# Register your models here.

from .models import Topic, Post, Message, User

admin.site.register(User)
admin.site.register(Post)
admin.site.register(Topic)
admin.site.register(Message)
