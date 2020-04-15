from django import forms
from django.core.validators import validate_email
from django.contrib.auth.models import User

from .models import MailAccount, Machines, MachineStates


class MachineForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        cls = {
            'class': 'form-control'
        }
        self.fields['manager'].widget.attrs.update(cls)
        users = [(user.pk, "%s" % (user.username,)) for user in User.objects.filter(is_active=True)]
        self.fields['manager'].choices = users
        self.fields['name'].widget.attrs.update(cls)
        self.fields['description'].widget.attrs.update(cls)
        self.fields['ip_address'].widget.attrs.update(cls)
        self.fields['ip_address'].label = 'Machine IP'

    class Meta:
        model = Machines
        fields = (
            'manager',
            'name',
            'description',
            'ip_address',
        )

class DummyDataForm(forms.Form):
    machine_id = forms.ChoiceField(label='Machine Name', required=True)
    status = forms.FloatField(label='Status Value', required=True)
    machine_time = forms.DateTimeField(label='Machine Time', input_formats=['%Y-%m-%d %H:%M:%S'],
                                       required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        cls = {
            'class': 'form-control'
        }

        self.fields['machine_id'].widget.attrs.update(cls)
        machines = [(machine.id, "%s" % (machine.name,)) for machine in Machines.objects.all()]
        self.fields['machine_id'].choices = machines
        self.fields['status'].widget.attrs.update(cls)
        self.fields['machine_time'].widget.attrs.update(cls)