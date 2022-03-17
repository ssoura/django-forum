from dataclasses import field
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import Post, User


class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        # fields = ['name', 'username', 'email', 'password1', 'password2']
        fields = ['username', 'email', 'password1', 'password2']
        

class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = '__all__'
        exclude = ['host', 'participants']


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['avatar', 'username', 'email', 'bio']
