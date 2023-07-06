from datetime import datetime

from django.utils.timezone import make_aware

from .hn_api.api import HackerNewsApi
from .hn_api.items import HNStory, HNComment
from .models import Story, Comment, HNFetchState


class HNApiScraper:
    def __init__(self):
        self.api = HackerNewsApi()

    
    def save_single_story(self, story: HNStory, size_limit = None):
        item = Story()
        item.source_id = story.id
        item.origin = False
        item.source_creator_id = story.by
        item.source_id = story.id
        item.source_created_at = make_aware(datetime.fromtimestamp(story.time))

        item.item_type = story.type

        item.comment_count = story.descendants
        item.text = story.text
        item.url = story.url
        item.title = story.title
        item.score = story.score

        item.save()
        
        self.process_comments(story.kids, parent=item, size_limit = size_limit)

        return item

    def save_single_comment(self, comment: HNComment, parent, size_limit = None):
        item = None

        if isinstance(parent, Story):
            item = Comment(
                source_id = comment.id,
                item_type = comment.type,
                origin = False,
                source_creator_id = comment.by,
                source_created_at = make_aware(datetime.fromtimestamp(comment.time)),
                text = comment.text,
                parent_post = parent
            )

        elif isinstance(parent, Comment):
            item = Comment(
                source_id = comment.id,
                item_type = comment.type,
                origin = False,
                source_creator_id = comment.by,
                source_created_at = make_aware(datetime.fromtimestamp(comment.time)),
                text = comment.text,
                parent_post = parent.parent_post,
                parent_comment = parent
            )
        else:
            raise Exception("Invalid parent object type", type(parent), parent, comment)
        
        item.save()

        self.process_comments(comment.kids, parent=item, size_limit=size_limit)
        return item


    def save_latests_posts(self, size_limit = 100, comment_limit = None):
        last_fetch_state = HNFetchState.objects.first()
        stop_id = None if last_fetch_state is None else int(last_fetch_state.last_id)
        stories = self.api.get_latest_stories(size_limit, stop_id)

        latest_story = None
        for story in stories:
            hn_story = HNStory(**story)
            if latest_story is None:
                latest_story = hn_story

            self.save_single_story(hn_story, size_limit=comment_limit)
        
        if latest_story is not None:
            if last_fetch_state is not None:
                last_fetch_state.last_id = latest_story.id
                last_fetch_state.save(force_update=True)
            else:
                last_fetch_state = HNFetchState(last_id = latest_story.id)
                last_fetch_state.save()


    def process_comments(self, comments, parent, size_limit = None):
        if comments is None or len(comments) == 0:
            return
        if size_limit is not None:
            comments = comments[:size_limit]
        self.save_comments(comments, parent) 


    def save_comments(self, comment_ids, parent):
        for id in comment_ids:
            comment = self.api.get_item_by_id(id)
            comment = HNComment(**comment)
            self.save_single_comment(comment, parent)
