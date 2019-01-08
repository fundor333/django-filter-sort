from django.views.generic.base import TemplateResponseMixin

from filter_sorter import MultiFormMixin, ProcessMultipleFormsView


class BaseMultipleFormsView(MultiFormMixin, ProcessMultipleFormsView):
    """
    A base view for displaying several forms.
    """


class MultiFormsView(TemplateResponseMixin, BaseMultipleFormsView):
    """
    A view for displaying several forms, and rendering a template response.
    """