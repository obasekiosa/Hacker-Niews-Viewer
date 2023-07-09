from news_viewer.models import Comment, Story
from rest_framework import serializers

class CommentSerializer(serializers.ModelSerializer):
    updated_at = serializers.DateTimeField(write_only = True)
    class Meta:
        model = Comment
        fields = "__all__"


class CreateCommentSerializer(serializers.Serializer):
    text = serializers.CharField(required = True)
    parent_id = serializers.IntegerField(required = True)
    parent_type = serializers.CharField(required = True)
    url = serializers.URLField()

    def create(self, validated_data):
        parent_id = validated_data.get("parent_id", None)
        parent_type = validated_data.get("parent_type", None)

        if parent_type is None:
            raise serializers.ValidationError("parent_type is required")

        comment = None
        parent = None

        if parent_type == "story":
            try:
                parent = Story.objects.get(pk=parent_id)
            except:
                raise serializers.ValidationError("Parent entity does not exist")

            comment = Comment.objects.create(
                item_type = "comment",
                origin = True,
                text = validated_data.get("text", None),
                url = validated_data.get("url", None),
                parent_post = parent,
            )
        elif parent_type == "comment":
            try:
                parent = Comment.objects.get(pk=parent_id)
            except:
                raise serializers.ValidationError("Parent entity does not exist")

            comment = Comment.objects.create(
                item_type = "comment",
                origin = True,
                text = validated_data.get("text", None),
                url = validated_data.get("url", None),
                parent_post = parent.parent_post,
                parent_comment = parent
            )
            
            # icrement parent_comment direct_descendant count
            comment.parent_comment.direct_comment_count += 1
        else: 
            raise serializers.ValidationError("Invalid parent type")

        # increment parent_post total count
        comment.parent_post.comment_count += 1
        # icrement parent_post direct_descendant count
        comment.parent_post.direct_comment_count += 1

        comment.source_id = f"origin_{comment.id}"
        comment.source_created_at = comment.created_at
        comment.save(force_update=True)
        return comment
   

class UpdateCommentSerializer(serializers.ModelSerializer):

    text = serializers.CharField(required=False)
    url  = serializers.URLField(required=False)

    class Meta:
        model = Comment
        fields = ["text", "url"]
        
    def update(self, instance, validated_data):
        instance.text = validated_data.get("text", instance.text)
        instance.url = validated_data.get("url", instance.url)
        instance.save()
        return instance