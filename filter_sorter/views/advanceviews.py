from django.conf import settings
from django.views.generic.list import  BaseListView

class AdvanceListView(BaseListView):
    template_name_suffix = "_list" 

    paginate_by = getattr(settings, "DJANGO_FILTER_SORT_PAGINATE_BY", None)
    sort_kwarg = getattr(settings, "DJANGO_FILTER_SORT_SORT_KWARG", "sort")

    def get_ordering(self):
        """Return the field or fields to use for ordering the queryset."""
        if self.sort_kwarg in self.kwargs:
            return self.kwargs[self.sort_kwarg]
        else:
            self.ordering