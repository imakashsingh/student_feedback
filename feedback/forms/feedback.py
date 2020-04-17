from django import forms

class SubmitFeedback(forms.Form):
    class Meta:
        widgets = {
            'system_no' : forms.NumberInput(),
            'gender' : forms.CharField(),
            'rating1' : forms.NumberInput(),
            'fd1': forms.Textarea(),
            'rating2' : forms.NumberInput(),
            'fd2': forms.Textarea(),
            'rating3' : forms.NumberInput(),
            'fd3': forms.Textarea(),
            'rating4' : forms.NumberInput(),
            'fd4': forms.Textarea(),
        }

class AddSubject(forms.Form):
    class Meta:
        widgets = {
            'subject_name' : forms.TextInput(),
        }

class Login_form(forms.Form):
    class Meta:
        widgets = {
            'username' : forms.TextInput(),
            'password' : forms.PasswordInput(),
        }