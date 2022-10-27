from django import forms

from .models import Project


class ProjectForm(forms.ModelForm):
    images = forms.ImageField()

    class Meta:
        model = Project
        fields = ("title", "details", "category", "total_target", "tags", "start_date", "end_date", "images")
