from django.conf import settings
from django.views.generic.list import BaseListView


class AdvanceListView(BaseListView):
    template_name_suffix = "_list"

    paginate_by = getattr(settings, "DJANGO_FILTER_SORT_PAGINATE_BY", None)
    sort_kwarg = getattr(settings, "DJANGO_FILTER_SORT_SORT_KWARG", "sort")

    def get_ordering(self):
        """Return the field or fields to use for ordering the queryset."""
        order = self.request.GET.get(self.sort_kwarg)
        if order:
            return order
        else:
            return self.ordering
