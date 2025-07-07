from django import forms
from .models import Blogs
from tinymce.widgets import TinyMCE
from learners.models import *
# from django_ckeditor_5.widgets import CKEditor5Widget

class BlogsForm(forms.ModelForm):
    # content = forms.CharField(widget=CKEditor5Widget())
    # content = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30}))

    class Meta:
        model = Blogs
        fields = ['blog_author', 'blog_title', 'blog_topic','description', 'content']
    
    blog_topic = forms.ModelChoiceField(
        queryset=Topics.objects.all(),  # Select all Topics
        empty_label="Select a Topic",  # Optional: Placeholder text
        widget=forms.Select(attrs={'class': 'form-control'})
    )