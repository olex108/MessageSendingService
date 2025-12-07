from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from .models import Mailing, Recipients


class HomeView(TemplateView):
    template_name = "mailing/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["Recipients_count"] = Recipients.objects.all().count()
        context["Mailings_count"] = Mailing.objects.all().count()
        context["Mailings_active_count"] = Mailing.objects.all().filter(status="LAUNCHED").count()
        return context
