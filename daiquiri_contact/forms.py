from django import forms

class ContactForm(forms.Form):
    contact_name = forms.CharField(required=True)
    contact_email = forms.EmailField(required=True)
    contact_subject = forms.CharField(required=True)
    contact_message = forms.CharField(
        required=True,
        widget=forms.Textarea
    )

    def __init__(self, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)
        self.fields['contact_name'].label = "Your name:"
        self.fields['contact_email'].label = "Your email:"
        self.fields['contact_subject'].label = "Subject:"
        self.fields['contact_message'].label = "Message:"

    def clean(self):
        if (self.cleaned_data.get('email') !=
            self.cleaned_data.get('confirm_email')):

            raise ValidationError("Email addresses do not match.")

        return self.cleaned_data

