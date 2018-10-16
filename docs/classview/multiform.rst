*********
Multiform
*********

A view that displays any number of forms. On error, redisplays the form with validation errors; on success, redirects to a new URL.

ClassView
---------

Example myapp/forms.py::

    from django import forms

    class SaleContactForm(forms.Form):
        name = forms.CharField()
        message = forms.CharField(widget=forms.Textarea)

        def send_email(self):
            # send email using the self.cleaned_data dictionary
            pass

    class SupportContactForm(forms.Form):
        name = forms.CharField()
        message = forms.CharField(widget=forms.Textarea)

        def send_email(self):
            # send email using the self.cleaned_data dictionary
            pass

Now for use them in one ClassView you need to create::

    class SignupLoginView(MultiFormsView):
    template_name = 'public/my_login_signup_template.html'
    form_classes = {'sale': SaleContactForm,
                    'support': SupportContactForm}
    success_url = 'my/success/url'

    def get_sale_initial(self):
        return {'name':'Jhon Smith'}

    def get_support_initial(self):
        return {'name':'Jhon Smith'}


    def sale_form_valid(self, form):
        return form.sale(self.request, redirect_url=self.get_success_url())

    def support_form_valid(self, form):
        form.send_email()
        return form.support(self.request,  redirect_url=self.get_success_url())


Themplate
---------

Example for the themplate:: 

    <form class="sale" method="POST" action="{% url 'my_view' %}">
        {% csrf_token %}
        {{ forms.sale.as_p }}

        <button name='action' value='sale' type="submit">Send Sale</button>
    </form>

    <form class="support" method="POST" action="{% url 'my_view' %}">
        {% csrf_token %}
        {{ forms.support.as_p }}

        <button name='action' value='support' type="submit">Send Support</button>
    </form>

**N.B.** You need to use the forms' "names" as attribute set to "action" and their 'value' attribute must match the name given to the form in the 'form_classes' dict.
If you don't do it, the post will be all the forms of the page