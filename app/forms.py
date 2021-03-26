import io
from django import forms
from django.contrib import admin
from django.contrib.auth.models import User
from common.dash_validator import DashValidator
from django.core.files import File
from .models import PlotlyDashApp
from guardian.admin import GuardedModelAdmin

import zipfile

class PlotlyDashAppForm(forms.ModelForm):
    creator = forms.ModelChoiceField(
        queryset=User.objects.all(),
        empty_label="(Nothing)",
        widget=forms.Select(
            attrs={
                "class": "form-control",
            }
        ))
    title = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder" : "Title",                
                "class": "form-control"
            }
        ))
    dash_file = forms.FileField(
        widget=forms.FileInput(
            attrs={           
                "class": "custom-file-input"
            }
        ))

    class Meta:
        model = PlotlyDashApp
        fields = ('title', 'creator', 'dash_file')

    def clean_dash_file(self):
        dash_file = self.cleaned_data['dash_file']

        ext = self.cleaned_data['dash_file'].name.split('.')[-1]
        if ext != 'py':
            # TODO It's better to check mimetype using first chunk of the file
            raise forms.ValidationError("Dash should be a python file")

        validatior = DashValidator(dash_file)

        if not validatior.has_app_module():
            raise forms.ValidationError("Invalid Dash File")

        if not validatior.is_executeable():
            raise forms.ValidationError("Dash File Is Not Executable")

        return dash_file

    def save(self, commit=True):
        obj = super(PlotlyDashAppForm, self).save(commit=False)
        obj.dash_orginal_name = self.cleaned_data['dash_file'].name
        obj.save()
        return obj

class PlotlyDashMultipleAppForm(forms.Form): # New
    creator = forms.ModelChoiceField(
        queryset=User.objects.all(),
        empty_label="(Nothing)",
        widget=forms.Select(
            attrs={
                "class": "form-control",
            }
        ))
    zip_file = forms.FileField(
        widget=forms.FileInput(
            attrs={           
                "class": "custom-file-input"
            }
        ))

    class Meta:
        fields = ('creator', 'zip_file')

    def clean_zip_file(self):
        zip_file = self.cleaned_data['zip_file']

        ext = zip_file.name.split('.')[-1]
        if ext != 'zip':
            # TODO It's better to check mimetype using first chunk of the file
            raise forms.ValidationError("File Should Be In Zip Format")

        dash_files = []

        with zipfile.ZipFile(zip_file) as zip_ref:
            for name in zip_ref.namelist():
                if name.split('.')[-1] != 'py':
                    raise forms.ValidationError("All Files Inside The Zip Should Be In Python Format")

                file_obj = io.BytesIO(zip_ref.read(name))
                file_obj.name = name

                validatior = DashValidator(file_obj)

                if not validatior.has_app_module():
                    raise forms.ValidationError("There Is One Or More Invalid Dash File Inside The Zip")

                if not validatior.is_executeable():
                    raise forms.ValidationError("There Is One Or More Non-Executable File Inside The Zip")
                
                dash_files.append(File(file_obj))
                    
        return dash_files
        


class PlotlyDashAppAdmin(GuardedModelAdmin):
    list_display = ('unique_id', 'title', 'creator', 'dash_orginal_name', 'dash_file')
    form = PlotlyDashAppForm


    