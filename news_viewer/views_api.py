from threading import Thread

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import generics
from rest_framework import status
from rest_framework.decorators import action

from url_filter.integrations.drf import DjangoFilterBackend

from .serializers.story_serializer import StroySerializer, CreateStorySerializer, UpdateStorySerializer
from .serializers.comment_serializer import CommentSerializer, CreateCommentSerializer, UpdateCommentSerializer
from .models import Story, Comment
from .cron import forever_task

class TriggerCronViewSet(viewsets.ViewSet):
    basename = "cron_trigger"
    permission_classes = []

    THREADS = []

    @action(detail=False)
    def trigger(self, request):
        cls = self.__class__
        num_threads = len(cls.THREADS)
        if num_threads == 0:
            self.start_thread()
            return Response("success")
        elif num_threads == 1:
            thread = cls.THREADS[0]
            if thread.is_alive():
                return Response("already pulling")
            else:
                cls.THREADS = []
                self.start_thread()
                return Response("success, restarted")
        else:
            return Response(f"warning multiple pulls: thread count {num_threads}")

    def start_thread(self):
        thread = Thread(target=forever_task)
        thread.start()
        thread.is_alive()
        cls = self.__class__
        cls.THREADS.append(thread)

class StoryViewSet(viewsets.ModelViewSet):
    queryset = Story.objects.order_by("-source_created_at")
    serializer_class = StroySerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]
    filter_fields = ["id", "text", "title", "url", "origin"]
    
    def create(self, request, *args, **kwargs):
        serializer = CreateStorySerializer(data=request.data)
        if serializer.is_valid():
            story = serializer.save()
            return Response(StroySerializer(story).data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def update(self, request, *args, **kwargs):
        story = self.get_object()
        if story.origin:
            serializer = UpdateStorySerializer(story, data=request.data)
            if serializer.is_valid():
                saved_story = serializer.save()
                return Response(StroySerializer(saved_story).data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": {"message":"Can not modify external Entity"}}, status=status.HTTP_403_FORBIDDEN)
        
    def destroy(self, request, *args, **kwargs):
        story = self.get_object()
        if story.origin:
            return super().destroy(request, *args, **kwargs)
        else:
            return Response({"error": {"message":"Can not modify external Entity"}}, status=status.HTTP_403_FORBIDDEN)
    
    @action(detail=True)
    def comments(self, request, pk=None):
        comment_set = self.get_object().comment_set.filter(parent_comment_id=None)
        serializer = CommentSerializer(comment_set, many=True)
        return Response(serializer.data)


class CommentViewSet(viewsets.GenericViewSet, generics.RetrieveAPIView, generics.CreateAPIView):

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.AllowAny]

    @action(detail=True)
    def sub_comments(self, request, pk=None):
        comment_set = self.get_object().comment_set.all()
        serializer = CommentSerializer(comment_set, many=True)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        serializer = CreateCommentSerializer(data=request.data)
        if serializer.is_valid():
            comment = serializer.save()
            return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.origin:
            serializer = UpdateCommentSerializer(comment, data=request.data)
            if serializer.is_valid():
                saved_comment = serializer.save()
                return Response(CommentSerializer(saved_comment).data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": {"message":"Can not modify external Entity"}}, status=status.HTTP_403_FORBIDDEN)
    

        
       
