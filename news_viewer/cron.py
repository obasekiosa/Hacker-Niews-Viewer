from datetime import datetime
import logging

from django.utils.timezone import make_aware
from django_cron import CronJobBase, Schedule

from .hn_api.api import HackerNewsApi
from .hn_api.items import HNStory, HNComment
from .models import Story, Comment, HNFetchState


logging.basicConfig()

class HNApiScraper(CronJobBase):

    RUN_EVERY_MINS = 5 # every 5 minutes
    RETRY_AFTER_FAILURE_MINS = 1
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS, retry_after_failure_mins=RETRY_AFTER_FAILURE_MINS)
    code = 'get_news.my_cron_job'

    def do(self):
        self.log.info("Starting get_items cron")
        self.save_latests_posts()
        self.log.info("Completed get_items cron")

    def __init__(self):
        self.api = HackerNewsApi()
        self.log = logging.getLogger("HN_API_Scrapper")
        self.log.setLevel(logging.DEBUG)


    def to_canonical_id(self, id):
        return f"hn_{id}"
    

    def save_single_story(self, story: HNStory, size_limit = None):
        item = None
        try:
            item = Story.objects.get(source_id = self.to_canonical_id(story.id))
        except:
            item = Story()
            item.source_id = story.id
            item.origin = False
            item.source_creator_id = story.by
            item.source_id = self.to_canonical_id(story.id)
            item.source_created_at = make_aware(datetime.fromtimestamp(story.time))
            item.direct_comment_count = len(story.kids) if story.kids else 0
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
        kids_size = len(comment.kids) if comment.kids else 0
        try:
            item = Comment.objects.get(source_id = self.to_canonical_id(comment.id))
        except:
            if isinstance(parent, Story):
                item = Comment(
                    source_id = self.to_canonical_id(comment.id),
                    item_type = comment.type,
                    origin = False,
                    source_creator_id = comment.by,
                    source_created_at = make_aware(datetime.fromtimestamp(comment.time)),
                    text = comment.text,
                    parent_post = parent,
                    direct_comment_count = kids_size,
                )
            elif isinstance(parent, Comment):
                item = Comment(
                    source_id = self.to_canonical_id(comment.id),
                    item_type = comment.type,
                    origin = False,
                    source_creator_id = comment.by,
                    source_created_at = make_aware(datetime.fromtimestamp(comment.time)),
                    text = comment.text,
                    parent_post = parent.parent_post,
                    parent_comment = parent,
                    direct_comment_count = kids_size,
                )
            else:
                raise Exception("Invalid parent object type", type(parent), parent, comment)
            
            item.save()

        self.process_comments(comment.kids, parent=item, size_limit=size_limit)
        return item


    def save_latests_posts(self, size_limit = 100, comment_limit = None):
        last_fetch_state = HNFetchState.objects.first()
        stop_id = None if last_fetch_state is None else int(last_fetch_state.last_id)
        stories = self.api.get_latest_stories(size_limit, stop_id, desc=False)

        self.log.info("Saving posts...")

        completed_count = 0
        for story in stories:
            hn_story = HNStory(**story)

            self.save_single_story(hn_story, size_limit=comment_limit)

            if last_fetch_state is not None:
                last_fetch_state.last_id = hn_story.id
                last_fetch_state.save(force_update=True)
            else:
                last_fetch_state = HNFetchState(last_id = hn_story.id)
                last_fetch_state.save()
            completed_count += 1

        self.log.info(f"Saved {completed_count} new stories to database")
        
        self.log.info("Done saving posts")


    def process_comments(self, comments, parent, size_limit = None):
        if comments is None or len(comments) == 0:
            return
        if size_limit is not None:
            comments = comments[:size_limit]
        self.save_comments(comments, parent) 


    def save_comments(self, comment_ids, parent):
        completed_comments_for_parent = 0
        for id in comment_ids:
            comment = self.api.get_item_by_id(id)
            comment = HNComment(**comment)
            self.save_single_comment(comment, parent)
            completed_comments_for_parent += 1
        
        self.log.info(f"Saved {completed_comments_for_parent} new Sub comments for {type(parent).__name__} with id {parent.id}")