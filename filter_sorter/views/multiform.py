from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.views.generic.base import ContextMixin, TemplateResponseMixin
from django.views.generic.edit import ProcessFormView

# Taken from https://gist.github.com/jamesbrobb/748c47f46b9bd224b07f
# Example https://stackoverflow.com/questions/15497693/django-can-class-based-views-accept-two-forms-at-a-time/24011448#24011448


class MultiFormMixin(ContextMixin):
    """
    This is an example usage

    class SignupLoginView(MultiFormsView):
        template_name = 'public/my_login_signup_template.html'
        form_classes = {'login': LoginForm,
                        'signup': SignupForm}
        success_url = 'my/success/url'

        def get_login_initial(self):
            return {'email':'dave@dave.com'}

        def get_signup_initial(self):
            return {'email':'dave@dave.com'}

        def get_context_data(self, **kwargs):
            context = super(SignupLoginView, self).get_context_data(**kwargs)
            context.update({"some_context_value": 'blah blah blah',
                            "some_other_context_value": 'blah'})
            return context

        def login_form_valid(self, form):
            return form.login(self.request, redirect_url=self.get_success_url())

        def signup_form_valid(self, form):
            user = form.save(self.request)
            return form.signup(self.request, user, self.get_success_url())

    and the template looks like this

    <form class="login" method="POST" action="{% url 'my_view' %}">
        {% csrf_token %}
        {{ forms.login.as_p }}

        <button name='action' value='login' type="submit">Sign in</button>
    </form>

    <form class="signup" method="POST" action="{% url 'my_view' %}">
        {% csrf_token %}
        {{ forms.signup.as_p }}

        <button name='action' value='signup' type="submit">Sign up</button>
    </form>
    """
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

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['forms'] = self.get_forms(form_classes=self.form_classes)
        return super().get_context_data(**kwargs)


    def get_form_kwargs(self, form_name, bind_form=False):
        kwargs = {}
        kwargs.update({"initial": self.get_initial(form_name)})
        kwargs.update({"prefix": self.get_prefix(form_name)})

        if bind_form:
            kwargs.update(self._bind_form_data())

        return kwargs

    def forms_valid(self, forms, form_name):
        form_valid_method = "%s_form_valid" % form_name
        if hasattr(self, form_valid_method):
            return getattr(self, form_valid_method)(forms[form_name])
        else:
            return HttpResponseRedirect(self.get_success_url(form_name))

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

    def get_success_url(self, form_name=None):
        return self.success_urls.get(form_name, self.success_url)

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


class ProcessMultipleFormsView(ProcessFormView):
    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        form_classes = self.get_form_classes()
        form_name = request.POST.get("action")
        if self._individual_exists(form_name):
            return self._process_individual_form(form_name, form_classes)
        elif self._group_exists(form_name):
            return self._process_grouped_forms(form_name, form_classes)
        else:
            return self._process_all_forms(form_classes)

    def _individual_exists(self, form_name):
        return form_name in self.form_classes

    def _group_exists(self, group_name):
        return group_name in self.grouped_forms

    def _process_individual_form(self, form_name, form_classes):
        forms = self.get_forms(form_classes, (form_name,))
        form = forms.get(form_name)
        if not form:
            return HttpResponseForbidden()
        elif form.is_valid():
            return self.forms_valid(forms, form_name)
        else:
            return self.forms_invalid(forms)

    def _process_grouped_forms(self, group_name, form_classes):
        form_names = self.grouped_forms[group_name]
        forms = self.get_forms(form_classes, form_names)
        if all([forms.get(form_name).is_valid() for form_name in form_names.values()]):
            return self.forms_valid(forms)
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
