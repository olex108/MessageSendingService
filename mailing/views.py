from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Mailing, Recipients, Message

from .forms import MessageForm, RecipientForm, MailingForm

from .src.mailing_handlers import SMTPMailingHandler


class HomeView(TemplateView):
    template_name = "mailing/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["Recipients_count"] = Recipients.objects.all().count()
        context["Mailings_count"] = Mailing.objects.all().count()
        context["Mailings_active_count"] = Mailing.objects.all().filter(status="LAUNCHED").count()
        return context


class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = "mailing/message_list.html"
    context_object_name = "messages"

    def get_queryset(self):
        return Message.objects.all().filter(author=self.request.user.id).order_by("-updated_at")


class MessageDetailView(LoginRequiredMixin, DetailView):
    model = Message
    template_name = "mailing/message_detail.html"
    context_object_name = "message"


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = "mailing/message_form.html"
    success_url = reverse_lazy("mailing:message_list")

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = "mailing/message_form.html"
    success_url = reverse_lazy("mailing:message_list")


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = Message
    template_name = "mailing/message_delete.html"
    success_url = reverse_lazy("mailing:message_list")


class RecipientsListView(LoginRequiredMixin, ListView):
    model = Recipients
    template_name = "mailing/recipients_list.html"
    context_object_name = "recipients"

    def get_queryset(self):
        return Recipients.objects.all().filter(mailer=self.request.user.id).order_by("-full_name")


class RecipientDetailView(LoginRequiredMixin, DetailView):
    model = Recipients
    template_name = "mailing/recipient_detail.html"
    context_object_name = "recipient"


class RecipientCreateView(LoginRequiredMixin, CreateView):
    model = Recipients
    form_class = RecipientForm
    template_name = "mailing/recipient_form.html"
    success_url = reverse_lazy("mailing:recipients_list")

    def form_valid(self, form):
        form.instance.mailer = self.request.user
        return super().form_valid(form)


class RecipientUpdateView(LoginRequiredMixin, UpdateView):
    model = Recipients
    form_class = RecipientForm
    template_name = "mailing/recipient_form.html"
    success_url = reverse_lazy("mailing:recipients_list")


class RecipientDeleteView(LoginRequiredMixin, DeleteView):
    model = Recipients
    template_name = "mailing/recipient_delete.html"
    success_url = reverse_lazy("mailing:recipients_list")


class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = "mailing/mailing_list.html"
    context_object_name = "mailings"

    def get_queryset(self):
        mailings = Mailing.objects.all().filter(message__author=self.request.user).order_by("-start_at")
        for mailing in mailings:
            mailing.update_status()
        return mailings


class MailingDetailView(LoginRequiredMixin, DetailView):
    model = Mailing
    template_name = "mailing/mailing_detail.html"
    context_object_name = "mailing"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.update_status()
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mailing_item = self.object
        if mailing_item.status == Mailing.LAUNCHED and mailing_item.message.author == self.request.user:
            context["start_mailing"] = True
        return context


    def post(self, request, *args, **kwargs):

        self.object = self.get_object()

        mailing_item = self.object

        if mailing_item.status == Mailing.LAUNCHED and mailing_item.message.author == self.request.user:
            mailing = self.object
            mailing_sending = SMTPMailingHandler(mailing)
            mailing_result = mailing_sending.send_mails()

            status_message = "Рассылка запущена успешно" if mailing_result else "Ошибка рассылки"

            return JsonResponse({
                "status": "success",
                "message": status_message,
            })
        else:
            return JsonResponse({
                "status": "error",
                "message": "Нет права запускать рассылку",
            })




class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailing/mailing_form.html"
    success_url = reverse_lazy("mailing:mailing_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["recipients"] = Recipients.objects.all().filter(mailer=self.request.user.id).order_by("-full_name")
        return context

    def form_valid(self, form):
        """Add data to field mailer - user and recipients - recipients of user"""

        form.instance.mailer = self.request.user
        response = super().form_valid(form)
        form.instance.recipients.set(
            Recipients.objects.all().filter(mailer=self.request.user.id).order_by("-full_name")
        )
        return response

    def form_invalid(self, form):

        print(form.errors)
        response = super().form_invalid(form)
        response.context_data["error_message"] = "Please correct the errors below."
        return response


class MailingUpdateView(LoginRequiredMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailing/mailing_form.html"
    success_url = reverse_lazy("mailing:mailing_list")

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.update_status()
        return obj

    def form_valid(self, form):
        """Update field status of model"""

        self.object.status = Mailing.CREATED
        self.object.update_status()
        self.object.save()

        return super().form_valid(form)


class MailingDeleteView(LoginRequiredMixin, DeleteView):
    model = Mailing
    template_name = "mailing/mailing_delete.html"
    success_url = reverse_lazy("mailing:mailing_list")
