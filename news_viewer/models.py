from django.db import models

# Create your models here.

class Base(models.Model):
    source_id = models.CharField(max_length=250)
    source_creator_id = models.CharField(max_length=250, null=True)
    source_created_at = models.DateTimeField(null=True)

    item_type = models.CharField(max_length=200)
    origin = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Comment(Base):
    text = models.TextField(null=True)
    url = models.URLField(null=True)
    parent_comment = models.ForeignKey("self", on_delete=models.CASCADE, null=True, default=None)
    parent_post = models.ForeignKey("Story", on_delete=models.CASCADE, null=True, default=None)
    

class Story(Base):
    comment_count = models.IntegerField(null=True)
    text = models.TextField(null=True)
    url = models.URLField(null=True)
    title = models.CharField(max_length=600, null=True)
    score = models.IntegerField(null=True)

class HNFetchState(models.Model):
    last_id = models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)