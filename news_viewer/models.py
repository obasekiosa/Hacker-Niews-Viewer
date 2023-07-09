from django.db import models

# Create your models here.

class Base(models.Model):
    source_id = models.CharField(max_length=250)
    source_creator_id = models.CharField(max_length=250, null=True)
    source_created_at = models.DateTimeField(null=True)

    direct_comment_count = models.IntegerField(default=0)
    text = models.TextField(null=True)
    url = models.URLField(null=True)

    item_type = models.CharField(max_length=200)
    origin = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    


class Comment(Base):
    parent_comment = models.ForeignKey("self", on_delete=models.CASCADE, null=True, default=None)
    parent_post = models.ForeignKey("Story", on_delete=models.CASCADE)
    

class Story(Base):
    comment_count = models.IntegerField(default=0)
    title = models.CharField(max_length=600, null=True)
    score = models.IntegerField(null=True, default=0)

    def direct_comments(self):
        return self.comment_set.filter(parent_comment_id=None).order_by("source_created_at")

class HNFetchState(models.Model):
    last_id = models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)