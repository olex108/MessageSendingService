from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, UpdateView
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from .forms import MailingForm, MessageForm, RecipientForm
from .models import Mailing, Message, Recipients, MailingAttempt

from .services import MailingServices


class HomeView(TemplateView):
    """CBV for home page"""

    template_name = "mailing/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            context = MailingServices.get_homa_page_data(context, self.request.user)
        except TypeError:
            pass

        return context


class MessageListView(LoginRequiredMixin, ListView):
    """CBV for message list"""

    model = Message
    template_name = "mailing/message_list.html"
    context_object_name = "messages"

    def get_queryset(self):
        return Message.objects.all().filter(author=self.request.user.id).order_by("-updated_at")


class MessageDetailView(LoginRequiredMixin, DetailView):
    """CBV for message detail"""

    model = Message
    template_name = "mailing/message_detail.html"
    context_object_name = "message"


class MessageCreateView(LoginRequiredMixin, CreateView):
    """CBV for message creation"""

    model = Message
    form_class = MessageForm
    template_name = "mailing/message_form.html"
    success_url = reverse_lazy("mailing:message_list")

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    """CBV for message update"""

    model = Message
    form_class = MessageForm
    template_name = "mailing/message_form.html"
    success_url = reverse_lazy("mailing:message_list")


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    """CBV for message deletion"""

    model = Message
    template_name = "mailing/message_delete.html"
    success_url = reverse_lazy("mailing:message_list")


class RecipientsListView(LoginRequiredMixin, ListView):
    """CBV for recipient list"""

    model = Recipients
    template_name = "mailing/recipients_list.html"
    context_object_name = "recipients"

    def get_queryset(self):
        return Recipients.objects.all().filter(mailer=self.request.user.id).order_by("-full_name")


class RecipientDetailView(LoginRequiredMixin, DetailView):
    """CBV for recipient detail"""

    model = Recipients
    template_name = "mailing/recipient_detail.html"
    context_object_name = "recipient"


class RecipientCreateView(LoginRequiredMixin, CreateView):
    """CBV for recipient creation"""

    model = Recipients
    form_class = RecipientForm
    template_name = "mailing/recipient_form.html"
    success_url = reverse_lazy("mailing:recipients_list")

    def form_valid(self, form):
        form.instance.mailer = self.request.user
        return super().form_valid(form)


class RecipientUpdateView(LoginRequiredMixin, UpdateView):
    """CBV for recipient update"""

    model = Recipients
    form_class = RecipientForm
    template_name = "mailing/recipient_form.html"
    success_url = reverse_lazy("mailing:recipients_list")


class RecipientDeleteView(LoginRequiredMixin, DeleteView):
    """CBV for recipient deletion"""

    model = Recipients
    template_name = "mailing/recipient_delete.html"
    success_url = reverse_lazy("mailing:recipients_list")


class MailingListView(LoginRequiredMixin, ListView):
    """CBV for mailing list"""

    model = Mailing
    template_name = "mailing/mailing_list.html"
    context_object_name = "mailings"

    def get_queryset(self):
        """Method to get user mailing list. and update satus of user mailings"""

        mailings = Mailing.objects.all().filter(message__author=self.request.user).order_by("-start_at")
        for mailing in mailings:
            mailing.update_status()
        return mailings


class MailingDetailView(LoginRequiredMixin, DetailView):
    """CBV for mailing detail"""

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
            status_message = MailingServices.start_mailing(mailing_item)
            return JsonResponse(
                {
                    "status": "success",
                    "message": status_message,
                }
            )
        else:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Нет права запускать рассылку",
                }
            )


class MailingCreateView(LoginRequiredMixin, CreateView):
    """CBV for mailing creation"""

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
    """CBV for mailing update"""

    model = Mailing
    form_class = MailingForm
    template_name = "mailing/mailing_form.html"
    success_url = reverse_lazy("mailing:mailing_list")

    def get_object(self, queryset=None):
        """
        Method update to change status of mailing
        """

        obj = super().get_object(queryset)
        obj.update_status()
        return obj

    def form_valid(self, form):
        """
        Update field status of model
        """

        self.object.status = Mailing.CREATED
        self.object.update_status()
        self.object.save()

        return super().form_valid(form)


class MailingDeleteView(LoginRequiredMixin, DeleteView):
    """CBV for mailing delete"""

    model = Mailing
    template_name = "mailing/mailing_delete.html"
    success_url = reverse_lazy("mailing:mailing_list")


class StatisticsView(LoginRequiredMixin, TemplateView):
    """CBV for mailing statistics"""

    template_name = "mailing/statistics.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = MailingServices.get_statistics(context, user=self.request.user)
        return context


class StatisticsSuccessView(LoginRequiredMixin, ListView):
    """CBV for mailing statistics"""

    model = MailingAttempt
    template_name = "mailing/statistics_success.html"
    context_object_name = "mailing_attempts"

    def get_queryset(self):
        return MailingAttempt.objects.all().filter(mailing__message__author=self.request.user,
                                                   status="SUCCESS").order_by("-attempt_at")


class StatisticsFailedView(LoginRequiredMixin, ListView):
    """CBV for mailing statistics"""

    model = MailingAttempt
    template_name = "mailing/statistics_failed.html"
    context_object_name = "mailing_attempts"

    def get_queryset(self):
        return MailingAttempt.objects.all().filter(mailing__message__author=self.request.user,
                                                   status="FAILED").order_by("-attempt_at")
