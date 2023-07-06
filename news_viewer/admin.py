from django.contrib import admin
from .models import Story, Comment, HNFetchState

# Register your models here.

admin.register(Story)
admin.register(Comment)
admin.register(HNFetchState)
