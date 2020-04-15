import os

import oauth2client
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.urls import reverse
from django.views.decorators.http import require_http_methods
import logging
from dashboard.models import MailAccount, MailAccountUser, Machines, MachineStates
from dashboard.agent import GROUP_ADMIN, GROUP_USERA, GROUP_USERB, SKEY_AGENT
from .forms import MachineForm, DummyDataForm
import time
import datetime
from .agent import Agent

from django.contrib import messages
from django.conf import settings
from django.db import connection
import json, csv
import re
# Matplot Chat
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import pylab
from pylab import *

from io import BytesIO
import base64
import pandas as pd
import random

#Email Send
import smtplib

#PDF File
from fpdf import FPDF

log = logging.getLogger('django')

def query_to_dicts(query_string, *query_args):

    #log.debug(str(dir(connection)))
    cursor = connection.cursor()
    #log.debug(str(dir(cursor)))
    cursor.execute(query_string, query_args)
    #log.debug(cursor.rowcount)log
    col_names = [desc[0] for desc in cursor.description]
    #log.debug(str(col_names))

    while True:
        row = cursor.fetchone()
        if row is None:
            return None

        row_dict = dict(zip(col_names, row))
        yield row_dict

    return row_dict

@login_required
def index(request):
    return redirect('machines_list')

@login_required
def accounts(request):
    return render(request, "dashboard.html")


@login_required
def agent_users(request):
    """
    Show the users list for the agent login

    :param request:
    :return: Boolean
    """
    if Agent.has_agent_permission(request):
        print('Has permission')
    else:
        return redirect('index')

    users = User.objects.filter(groups__name=GROUP_USERB, is_active=True).all()
    context = {
        'users': users
    }
    print(users)
    print(users[0].first_name)
    return render(request, 'agent_users.html', context)


@login_required
def agent_login(request, username):
    if not Agent.has_agent_permission(request):
        return redirect('index')

    agent = User.objects.filter(username=username).first()
    if not agent:
        messages.info(request, "User '%' doesn't exist" % username)
        return redirect('agent_users')

    messages.success(request, "You logged in as '%s (%s %s)'" % (agent.username, agent.first_name, agent.last_name))

    Agent.store_agent_in_session(request, agent)
    request.session['selected_email'] = None
    return redirect('index')


@login_required
def agent_logout(request):
    if not Agent.has_agent_permission(request):
        return redirect('index')

    request.session[SKEY_AGENT] = None
    request.session['selected_email'] = None
    messages.success(request, "You logged out from agent user")
    return redirect('index')

@login_required
def machine_add(request):
    """
    Add a new Mahcine.

    :param request:
    :return:
    """
    if not Agent.is_site_superuser(request):
        messages.error(request, 'Invalid permission')
        return redirect('machines_list')

    machine_form = MachineForm()

    if request.method == 'POST':
        machine_form = MachineForm(request.POST)

        if machine_form.is_valid():
            manager = machine_form.cleaned_data['manager']
            name = machine_form.cleaned_data['name']
            description = machine_form.cleaned_data['description']
            ip_address = machine_form.cleaned_data['ip_address']

            try:
                machine = Machines.objects.create(name=name, manager=manager,
                                                  description=description, ip_address=ip_address)
                messages.success(request, "Machine '%s' is Add Successfully." % name)
            except Exception as e:
                messages.error(request, "Machine '%s' Add Failed." % name)
                log.error(e)


    return render(request, "machine_add.html", {'form': machine_form})

@login_required
def machines_list(request):
    """
    Show the machines list.

    :param request:
    :return:
    """
    # Search keyword
    search = request.session.get('search')
    if not search:
        search = {}

    if request.method == 'POST':
        if request.POST.get('search[keyword]'):
            search['keyword'] = request.POST.get('search[keyword]')
        else:
            search['keyword'] = None
        request.session['search'] = search
        return redirect('machines_list')

    query = "select * from machines_list as ml, auth_user as au where " + \
            "ml.manager_id = au.id"

    if search.get('keyword'):
        #machines = machines.filter(name__contains=search.get('keyword'))
        query = "select * from machines_list as ml, auth_user as au where " + \
                "ml.manager_id = au.id and name like '%%%s%%'" % search.get('keyword')
    machines = query_to_dicts(query)

    return render(request, "machines_list.html", {
        'machines': machines,
        'search': search
    })

@login_required
def machine_delete(request, id):
    """
    Delete the registered machine by primary key 'id'

    :param request:
    :param id:
    :return:
    """
    if not Agent.is_site_superuser(request):
        messages.error(request, 'Invalid permission')
        return redirect('machines_list')

    machine = Machines.objects.filter(id=id).first()

    if machine:
        machine.delete()
        messages.success(request, "Deleted '%s' successfully." % machine.name)
    else:
        messages.error(request, "There is no machine with ID '%s'." % id)
    return redirect('machines_list')

@login_required
def dummy_add(request):
    """
    Add a new dummy data

    :param request:
    :param:
    :return:
    """
    if not Agent.is_site_superuser(request):
        messages.error(request, 'Invalid permission')
        return redirect('mail_accounts')

    dummy_form = DummyDataForm()

    if request.method == 'POST':
        dummy_form = DummyDataForm(request.POST)

        if dummy_form.is_valid():
            machine_id = dummy_form.cleaned_data['machine_id']
            status = dummy_form.cleaned_data['status']
            machine_time = dummy_form.cleaned_data['machine_time']


            try:
                machine_status = MachineStates.objects.create(machine_id=machine_id, status=status, machine_time=machine_time)
                messages.success(request, "Machine Status is Add Successfully.")
            except Exception as e:
                messages.error(request, "Machine Status Add Failed.")
                log.error(e)


    return render(request, "dummy_add.html", {'form': dummy_form})

@login_required
def machine_status_list(request):
    """
    Show the machines status list.

    :param request:
    :return:
    """

    query = "select ms.id, ms.status, ms.machine_time, ms.created_at, ms.updated_at, ml.name " + \
            "from machines_state as ms, machines_list as ml where " + \
            "ml.id = ms.machine_id"

    machines_status = query_to_dicts(query)

    return render(request, "machine_status_list.html", {
        'machines_status': machines_status,
    })

@login_required
def machine_status_delete(request, id):
    """
    Delete the registered machine status by primary key 'id'

    :param request:
    :param id:
    :return:
    """
    if not Agent.is_site_superuser(request):
        messages.error(request, 'Invalid permission')
        return redirect('machine_status_list')

    machine_status = MachineStates.objects.filter(id=id).first()

    if machine_status:
        machine_status.delete()
        messages.success(request, "Deleted Status successfully.")
    else:
        messages.error(request, "There is no machine status with ID '%s'." % id)
    return redirect('machine_status_list')

@login_required
def status_chart(request):
    """
    Show the staus chart.

    :param request:
    :return:
    """
    image_base64 = ''
    if request.method == 'POST':
        machines = request.POST['machines']
        start_timestamp = request.POST['start_timestamp']
        end_timestamp = request.POST['end_timestamp']
        email = request.POST['email']
        mail_send = request.POST['mail_send']
        if machines == '' or start_timestamp == '' or end_timestamp == '':
            messages.error(request, 'Input Chat Machine List and Period')
        else:
            print(machines)
            machine_list = machines.split(',')

            for i in range(len(machine_list)):
                label = ''
                query = "select ml.name, ms.* from machines_list as ml, machines_state as ms " + \
                        "where ml.id in(%s) and ml.id = ms.machine_id " % machine_list[i] + \
                        "and ml.created_at > '%s' and ml.created_at < '%s'" % (start_timestamp, end_timestamp)
                print(start_timestamp)
                print(end_timestamp)
                print(query)
                data = query_to_dicts(query)
                x_data = []
                y_data = []
                for item in data:
                    x_data.append(item['created_at'])
                    y_data.append(item['status'])
                    label = item['name']

                if label == '':
                    machine = Machines.objects.get(id=machine_list[i])
                    label = machine.name

                plt.plot(x_data, y_data, marker='o', markerfacecolor=[round(random.uniform(0, 1), 1), round(random.uniform(0, 1), 1), round(random.uniform(0, 1), 1)],
                         markersize=12, color=[round(random.uniform(0, 1), 1), round(random.uniform(0, 1), 1), round(random.uniform(0, 1), 1)],
                         linewidth=4, label=label)
                grid(True)
            #plt.xlim(start_timestamp, end_timestamp)
            plt.legend()
            #plt.show()
            buf = BytesIO()
            plt.savefig(buf, format='png', dpi=300)
            plt.savefig(os.path.join(os.getcwd(), 'pdfs', 'chart.png'), dpi=300)
            image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8').replace('\n', '')
            buf.close()
            plt.clf()
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Machine Static", ln=1, align="C")
            pdf.cell(200, 10, txt="Start Time:"+start_timestamp, ln=1, align="L")
            pdf.cell(200, 10, txt="End Time:"+end_timestamp, ln=1, align="L")

            pdf.image(os.path.join(os.getcwd(), 'pdfs', 'chart.png'), x=60, y=60, w=100)
            pdf.set_font("Arial", size=12)
            pdf.ln(85)  # move 85 down
            pdf.cell(200, 8, txt="{}".format('Status Chart'), ln=3, align='C')
            pdf.output(os.path.join(os.getcwd(), 'pdfs', "simple_demo.pdf"))
            # if mail_send != '':
            #     print(email)
            #     regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
            #     print(re.search(regex, email))
            #     if email != '' and re.search(regex, email):
            #         to = [email]
            #         subject = settings.EMAIL_TPLS['mat_graph'][0]
            #         email_body = settings.EMAIL_TPLS['mat_graph'][1] % ('test')
            #             #"<img src='data:image/png;base64,"+image_base64+"' alt='some text to display to your users when the image does not show correctly' width=500 height=auto />")
            #
            #         DataHelper.send_email(to, subject, email_body)
            #     else:
            #         messages.error(request, 'Input Email.')


    machines = Machines.objects.all()

    return render(request, "status_chart.html", {
        "machines": machines,
        "image_base64": image_base64
    })

class DataHelper:

    # --------------------------------------------------------  #
    # Send an email through google                              #
    # --------------------------------------------------------  #
    @staticmethod
    def send_email(to, subject, body):
        email_text = settings.EMAIL_TPL_BODY % (settings.EMAIL_HOST_USER, ", ".join(to), subject, body)
        print(email_text)
        # return

        try:
            server = smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT)

            server.ehlo()
            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            server.sendmail(settings.EMAIL_HOST_USER, ", ".join(to), email_text)
            server.close()

            print('Email sent!')
        except:
            print('Have got a problem in smtp.')
