from django.urls import path
from django.views.generic.base import TemplateView
from . import views

urlpatterns = [
    path('', views.index, name='index'),

    # ============= PLC Machine
    path('machine_add', views.machine_add, name='machine_add'),
    path('machines_list', views.machines_list, name='machines_list'),
    path('machine_delete/<int:id>', views.machine_delete, name='machine_delete'),
    # ============= PLC Status Data
    path('machine_status_list', views.machine_status_list, name='machine_status_list'),
    path('machine_status_delete/<int:id>', views.machine_status_delete, name='machine_status_delete'),
    path('dummy_add', views.dummy_add, name='dummy_add'),
    # ============= Status Chart
    path('status_chart', views.status_chart, name='status_chart'),
    # ============= User Agent Function
    path('agent_users', views.agent_users, name='agent_users'),
    path('agent_login/<username>', views.agent_login),
    path('agent_logout', views.agent_logout, name='agent_logout'),

]