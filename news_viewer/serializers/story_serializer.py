from news_viewer.models import Story
from rest_framework import serializers

class StroySerializer(serializers.ModelSerializer):
    updated_at = serializers.DateTimeField(write_only = True)
    class Meta:
        model = Story
        fields = "__all__"


class CreateStorySerializer(serializers.ModelSerializer):

    text = serializers.CharField(required = True)
    title = serializers.CharField(required = True, max_length = 600)
    url = serializers.URLField(required = True)

    class Meta:
        model = Story
        fields = ["text", "title", "url"]

    def create(self, validated_data):
        story = Story.objects.create(
            item_type = "story",
            origin = True,
            **validated_data
        )

        story.source_id = f"origin_{story.id}"
        story.source_created_at = story.created_at
        story.save(force_update=True)
        return story
   

class UpdateStorySerializer(serializers.ModelSerializer):

    text = serializers.CharField(required=False)
    title = serializers.CharField(required=False)
    url  = serializers.URLField(required=False)

    class Meta:
        model = Story
        fields = ["text", "title", "url"]
        
    def update(self, instance, validated_data):
        instance.text = validated_data.get("text", instance.text)
        instance.url = validated_data.get("url", instance.url)
        instance.title = validated_data.get("title", instance.title)
        instance.save()
        return instance

