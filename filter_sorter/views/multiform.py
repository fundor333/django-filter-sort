from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.views.generic.base import ContextMixin, TemplateResponseMixin
from django.views.generic.edit import ProcessFormView

# Taken from https://gist.github.com/jamesbrobb/748c47f46b9bd224b07f
# Example https://stackoverflow.com/questions/15497693/django-can-class-based-views-accept-two-forms-at-a-time/24011448#24011448


class MultiFormMixin(ContextMixin):
    form_classes = {}
    prefixes = {}
    success_urls = {}
    grouped_forms = {}

    initial = {}
    prefix = None
    success_url = None

    def get_form_classes(self):
        return self.form_classes

    def get_forms(self, form_classes, form_names=None, bind_all=False):
        return dict(
            [
                (
                    key,
                    self._create_form(
                        key, klass, (form_names and key in form_names) or bind_all
                    ),
                )
                for key, klass in form_classes.items()
            ]
        )

    def get_form_kwargs(self, form_name, bind_form=False):
        kwargs = {}
        kwargs.update({"initial": self.get_initial(form_name)})
        kwargs.update({"prefix": self.get_prefix(form_name)})

        if bind_form:
            kwargs.update(self._bind_form_data())
        if self.request.method in ("POST", "PUT"):
            kwargs.update({"data": self.request.POST, "files": self.request.FILES})
        return kwargs

    def get_success_urls(self, form_name=None):
        if form_name in self.success_urls:
            return self.success_urls[form_name]
        else:
            return self.get_success_url()

    def forms_valid(self, forms, form_name):
        form_valid_method = "%s_form_valid" % form_name

        if hasattr(self, form_valid_method):
            return getattr(self, form_valid_method)(forms[form_name])
        else:
            return HttpResponseRedirect(self.get_success_urls(form_name))

    def forms_invalid(self, forms):
        return self.render_to_response(self.get_context_data(forms=forms))

    def get_initial(self, form_name):
        initial_method = "get_%s_initial" % form_name
        if hasattr(self, initial_method):
            return getattr(self, initial_method)()
        else:
            return self.initial.copy()

    def get_prefix(self, form_name):
        return self.prefixes.get(form_name, self.prefix)

    def _create_form(self, form_name, klass, bind_form):
        form_kwargs = self.get_form_kwargs(form_name, bind_form)
        form_create_method = "create_%s_form" % form_name
        if hasattr(self, form_create_method):
            form = getattr(self, form_create_method)(**form_kwargs)
        else:
            form = klass(**form_kwargs)
        return form

    def _bind_form_data(self):
        if self.request.method in ("POST", "PUT"):
            return {"data": self.request.POST, "files": self.request.FILES}
        return {}

    def get_context_data(self, **kwargs):
        k = super().get_context_data()
        k["forms"] = self.get_forms(self.get_form_classes())
        return k


class ProcessMultipleFormsView(ProcessFormView):
    def post(self, request, *args, **kwargs):
        form_classes = self.get_form_classes()
        form_name = request.POST.get("action")
        if self._individual_exists(form_name):
            return self._process_individual_form(form_name, form_classes)
        else:
            return self._process_all_forms(form_classes)

    def _individual_exists(self, form_name):
        return form_name in self.form_classes

    def _process_individual_form(self, form_name, form_classes):
        forms = self.get_forms(form_classes, (form_name,))
        form = forms.get(form_name)
        if not form:
            return HttpResponseForbidden()
        elif form.is_valid():
            return self.forms_valid(forms, form_name)
        else:
            return self.forms_invalid(forms)

    def _process_all_forms(self, form_classes):
        forms = self.get_forms(form_classes, None, True)
        if all([form.is_valid() for form in forms.values()]):
            return self.forms_valid(forms)
        else:
            return self.forms_invalid(forms)


class BaseMultipleFormsView(MultiFormMixin, ProcessMultipleFormsView):
    """
    A base view for displaying several forms.
    """


class MultiFormsView(TemplateResponseMixin, BaseMultipleFormsView):
    """
    A view for displaying several forms, and rendering a template response.
    """
