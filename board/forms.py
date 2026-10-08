from django import forms
from .models import Post, Response
from django_ckeditor_5.widgets import CKEditor5Widget


class PostForm(forms.ModelForm):
    headline = forms.CharField(min_length=5, label='Заголовок')
    body = forms.CharField(widget=CKEditor5Widget, label='Текст')


    class Meta:
        model = Post
        fields = ['headline', 'body', 'category']


    def clean(self):
        cleaned_data = super().clean()
        headline = cleaned_data.get("headline")
        body = cleaned_data.get("body")

        if headline and body and headline == body:
            raise forms.ValidationError(
                "Заголовок и текст не должны быть идентичны."
            )

        return cleaned_data


class ResponseForm(forms.ModelForm):
    body = forms.CharField(widget=forms.Textarea, label='Текст отклика')

    class Meta:
        model = Response
        fields = ['body']


class VerificationForm(forms.Form):
    code = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={'class': 'form-control text-center fs-4 fw-bold', 'placeholder': 000000}),

    )

