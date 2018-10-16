*********
Multiform
*********

A view that displays any number of forms. On error, redisplays the form with validation errors; on success, redirects to a new URL.

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

Now for use it