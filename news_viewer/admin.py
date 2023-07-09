from django.contrib import admin
from .models import Story, Comment, HNFetchState

# Register your models here.

admin.site.register(Story)
admin.site.register(Comment)
admin.site.register(HNFetchState)
