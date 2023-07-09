from typing import Any, Dict
from django.shortcuts import render, get_object_or_404
from django.http import QueryDict
from django.urls import reverse
from django.views.generic import ListView, DetailView
from url_filter.filtersets import ModelFilterSet

from .models import Story


class IndexView(ListView):
    template_name = "news_viewer/index.html"
    context_object_name = "latest_stories_list"

    paginate_by = 25
    model = Story

    def get_queryset(self):
        query = self.remove_key_if_empty()
        fs = StoryFilterSet(data=query, queryset=super().get_queryset().order_by("-source_created_at"))
        return fs.filter()
    
    def remove_key_if_empty(self):
        """
        Copies self.request.GET into a querydickt discarding all keys with None values or empty string values
        """
        query_params = self.request.GET.copy()

        for k, v in self.request.GET.items():
            if v is None or len(v.strip()) == 0:
                query_params.pop(k)
        
        return query_params

        
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        query_params = self.request.GET.copy()
        if query_params.get("page"):
            query_params.pop("page")
        context_data = super().get_context_data(**kwargs)
        context_data["mod_query_params"] = query_params
        return context_data
    
    
    def query_params_to_query_dict(self, query_params):
        """
        Takes a dictionary of key value pairs and returns a QueryDict equivalent
        """

        return QueryDict("&".join(map(lambda item: f"{item[0]}={item[1]}", query_params.items())))
    
    def remap_query_params(self):
        """
        Converts self.request.GET into a dictionary with more appropriate keys for filtering
        also discards all keys with None values or empty string values
        """

        def add_to_map_as(new_map, old_map, key, new_key):
            if old_map.get(key) and not_empty(old_map.get(key)):
                new_map[new_key] = old_map.get(key)

        def not_empty(s):
            return len(s.strip()) > 0
        
        q_params = dict()
        params = self.request.GET

        add_to_map_as(q_params, params, 'search', 'title__icontains')
        add_to_map_as(q_params, params, 'origin', 'source_id__icontains')
        add_to_map_as(q_params, params, 'type', 'item_type')

        return q_params
    
class StoryDetailView(DetailView):
    model = Story
    template_name = "news_viewer/story_detail.html"


class StoryFilterSet(ModelFilterSet):
    class Meta(object):
        model = Story
