import requests


class HackerNewsApi:
    
    def __init__(self):
        self.BASE_URL = "https://hacker-news.firebaseio.com/v0"
        

    def get_top_stories_ids(self):
        result = requests.get(f"{self.BASE_URL}/topstories.json")
        return result.json()
    
    
    def get_new_stories_id(self):
        result = requests.get(f"{self.BASE_URL}/newstories.json")
        return result.json()
    
    
    def get_top_stories(self, size = None):
        if size is not None:
            return list(map(self.get_item_by_id, self.get_top_stories_id()[:size]))
        else:
            return list(map(self.get_item_by_id, self.get_top_stories_id()))
        
    
    def get_latest_stories(self, size = None, stop_id = None, desc = True):
        story_ids = self.get_new_stories_id()
        if size is not None:
            story_ids = story_ids[:size]

        if not desc:
            story_ids.reverse() # puts the id's in ascending order
        
        for id in story_ids:
            if stop_id is not None and id <= stop_id:
                if desc:
                    return
                else:
                    continue
            yield self.get_item_by_id(id)
    

    def get_item_by_id(self, id):
        result = requests.get(f"{self.BASE_URL}/item/{id}.json")
        return result.json()
    

    def top_jobs(self):
        result = requests.get(f"{self.BASE_URL}/jobstories.json")
        return result.json()
    

    def get_user_by_id(self, id):
        result = requests.get(f"{self.BASE_URL}/user/{id}.json")
        return result.json()


    def get_max_item_id(self):
        result = requests.get(f"{self.BASE_URL}/maxitem.json")
        return result.json()
    

    def get_items_starting_from_max(self, size = 10):
        max_item_id = self.get_max_item_id()
        for i in range(size):
            curr_id = max_item_id - i
            yield self.get_item_by_id(curr_id)