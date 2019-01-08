from django.views.generic.base import TemplateResponseMixin

from filter_sorter.views.multiform.multiform_process import ProcessMultipleFormsView
from filter_sorter.views.multiform.multiform_mixin import MultiFormMixin


class BaseMultipleFormsView(MultiFormMixin, ProcessMultipleFormsView):
    """
    A base view for displaying several forms.
    """


class MultiFormsView(TemplateResponseMixin, BaseMultipleFormsView):
    """
    A view for displaying several forms, and rendering a template response.
    """