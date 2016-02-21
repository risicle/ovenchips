from django import forms
from django.contrib.auth import get_user_model

from crispy_forms_foundation.forms import FoundationForm, FoundationModelForm

from .models import Project, Ticket


class BaseTrackerForm(FoundationModelForm):
    def __init__(self, user=None, title=None, *args, **kwargs):
        self.title = title
        self.user = user

        super(BaseTrackerForm, self).__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs['placeholder'] = field.label

    def save(self, *args, **kwargs):
        commit = kwargs.pop('commit', True)
        instance = super(BaseTrackerForm, self).save(
            commit=False, *args, **kwargs)

        self.pre_save(instance)

        if commit:
            instance.save()

        return instance

    def pre_save(self, instance):
        pass


class ProjectForm(BaseTrackerForm):
    class Meta:
        model = Project
        fields = ('title',)

    def pre_save(self, instance):
        instance.created_by = self.user

class AssigneeMultipleChoiceField(forms.ModelMultipleChoiceField):
    def __init__(self, **kwargs):
        kwargs["widget"] = kwargs.get("widget") or forms.SelectMultiple(attrs={"class":"chosen-select"})
        super(AssigneeMultipleChoiceField, self).__init__(**kwargs)
        # django 1.7 still has this stupid behaviour with ModelMultipleChoiceField and its automatic
        # help_text which needs to be overridden in this rather nasty way
        self.help_text = ""

    def label_from_instance(self, instance):
        return instance.email

class TicketForm(BaseTrackerForm):
    assignees = AssigneeMultipleChoiceField(queryset=None, required=False)

    class Meta:
        model = Ticket
        fields = ('title', 'description', 'assignees',)

    def __init__(self, project=None, *args, **kwargs):
        # if we have no project specified we must at least have a pre-existing instance
        self.project = project or kwargs["instance"].project
        super(TicketForm, self).__init__(*args, **kwargs)
        self.fields['assignees'].queryset = get_user_model().objects.all()

    def pre_save(self, instance):
        instance.created_by = self.user
        instance.project = self.project

class DeleteTicketDummyForm(FoundationForm):
    # this is a "dummy" form with no fields that we use to let crispy render our "form"
    # for us (particularly the submit button) in the same style as on other pages
    submit = "Delete"
    
    def __init__(self, title=None, *args, **kwargs):
        if title is not None:
            self.title = title
        super(DeleteTicketDummyForm, self).__init__(self, *args, **kwargs)
