from django.db import models
from django.conf import settings
from django.db.models import Q


class MailAccount(models.Model):
    email = models.CharField(max_length=50)
    sender_name = models.CharField(max_length=70, blank=True)
    user_id = models.CharField(max_length=50, blank=True)
    access_token = models.CharField(max_length=250, blank=True)

    detail = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @staticmethod
    def get_active_mail_accounts(user):
        if user.is_superuser:
            accounts = MailAccount.objects.exclude(Q(user_id__isnull=True) | Q(user_id__exact=''))
        else:
            accounts = MailAccount.objects.exclude(Q(user_id__isnull=True) | Q(user_id__exact='')).filter(mailaccountuser__user_id=user.id)

        return accounts.all()

    def __str__(self):
        str = self.email
        if self.user_id:
            str = str + " | " + self.user_id
        return str

    def username(self):
        au = MailAccountUser.objects.filter(mail_account_id=self.id).first()
        if au:
            return au.user.username
        return ""

    class Meta:
        db_table = 'mail_account'
        unique_together = ('email',)
        verbose_name = 'Email'
        verbose_name_plural = 'Emails'


class MailAccountUser(models.Model):
    """ Mail Account to User map
    
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=False, on_delete=models.CASCADE)
    mail_account = models.OneToOneField(MailAccount, null=False, on_delete=models.CASCADE)

    class Meta:
        db_table = 'mail_account_user'

        unique_together = (
            'mail_account',
        )

        verbose_name = 'Assigned Email'
        verbose_name_plural = 'Assigned Emails'

class FakeModel(object):
    class _meta:
        app_label = 'dashboard'  # This is the app that the form will exist under
        model_name = 'custom-form'  # This is what will be used in the link url
        verbose_name_plural = 'Add Emails'  # This is the name used in the link text
        object_name = 'ObjectName'

        swapped = False
        abstract = False

class Machines(models.Model):
    name = models.CharField(max_length=50)
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, null=False, on_delete=models.CASCADE)
    description = models.CharField(max_length=120, blank=True, default= '')
    ip_address = models.CharField(max_length=90)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    class Meta:
        db_table = 'machines_list'

        verbose_name = 'Machines'
        verbose_name_plural = 'Machines List'

class MachineStates(models.Model):
    machine = models.ForeignKey(Machines, on_delete=models.CASCADE, null=False)

    status = models.FloatField()
    machine_time = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'machines_state'

        verbose_name = 'Machines Status'
        verbose_name_plural = 'Machines Status List'
