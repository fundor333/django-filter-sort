from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.http import Http404
from django.shortcuts import render
from django.views.generic import ListView
from django_filters.views import FilterMixin


class FilterListView(ListView, FilterMixin):
    template_name_suffix = "_filter"

    def get(self, request, *args, **kwargs):
        filterset_class = self.get_filterset_class()
        self.filterset = self.get_filterset(filterset_class)
        queryset = self.filterset.qs

        self.object_list = queryset
        allow_empty = self.get_allow_empty()

        if not allow_empty:
            if self.get_paginate_by(self.object_list) is not None and hasattr(
                self.object_list, "exists"
            ):
                is_empty = not self.object_list.exists()
            else:
                is_empty = not self.object_list
            if is_empty:
                raise Http404(
                    _("Empty list and '%(class_name)s.allow_empty' is False.")
                    % {"class_name": self.__class__.__name__}
                )

        context = self.get_context_data(
            filter=self.filterset, object_list=self.object_list
        )
        return self.render_to_response(context)
