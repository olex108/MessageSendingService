from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, UpdateView
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView, View

from .forms import MailingForm, MessageForm, RecipientForm
from .models import Mailing, Message, Recipients, MailingAttempt

from mailing.src.queries import MailingAppQueries

from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect

from .src.mailing_handlers import SMTPMailingHandler


class HomeView(TemplateView):
    """CBV for home page"""

    template_name = "mailing/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user

        if user.is_authenticated:
            context = MailingAppQueries.get_homa_page_data(context, user)

        return context


class MessageListView(LoginRequiredMixin, ListView):
    """CBV for message list"""

    model = Message
    template_name = "mailing/message_list.html"
    context_object_name = "messages"

    def get_queryset(self):
        message_list = Message.objects.all().order_by("-updated_at")
        if self.request.user.has_perm("mailing.view_message"):
            return message_list
        else:
            return message_list.filter(author=self.request.user.id)


class MessageDetailView(LoginRequiredMixin, DetailView):
    """CBV for message detail"""

    model = Message
    template_name = "mailing/message_detail.html"
    context_object_name = "message"


class MessageCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """CBV for message creation"""

    model = Message
    form_class = MessageForm
    template_name = "mailing/message_form.html"
    success_url = reverse_lazy("mailing:message_list")

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        return self.request.user.has_perm("mailing.add_message")

    def handle_no_permission(self):
        return redirect("mailing:message_list")


class MessageUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """CBV for message update"""

    model = Message
    form_class = MessageForm
    template_name = "mailing/message_form.html"
    success_url = reverse_lazy("mailing:message_list")

    def test_func(self):
        return self.request.user == self.get_object().author

    def handle_no_permission(self):
        return redirect("mailing:message_detail", pk=self.kwargs["pk"])


class MessageDeleteView(LoginRequiredMixin,  UserPassesTestMixin, DeleteView):
    """CBV for message deletion"""

    model = Message
    template_name = "mailing/message_delete.html"
    success_url = reverse_lazy("mailing:message_list")

    def test_func(self):
        return self.request.user == self.get_object().author

    def handle_no_permission(self):
        return redirect("mailing:message_detail", pk=self.kwargs["pk"])


class RecipientsListView(LoginRequiredMixin, ListView):
    """CBV for recipient list"""

    model = Recipients
    template_name = "mailing/recipients_list.html"
    context_object_name = "recipients"

    def get_queryset(self):
        recipients_list = Recipients.objects.all().order_by("-full_name")
        if self.request.user.has_perm("mailing.view_recipients"):
            return recipients_list
        else:
            return recipients_list.filter(mailer=self.request.user.id)


class RecipientDetailView(LoginRequiredMixin, DetailView):
    """CBV for recipient detail"""

    model = Recipients
    template_name = "mailing/recipient_detail.html"
    context_object_name = "recipient"


class RecipientCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """CBV for recipient creation"""

    model = Recipients
    form_class = RecipientForm
    template_name = "mailing/recipient_form.html"
    success_url = reverse_lazy("mailing:recipients_list")

    def form_valid(self, form):
        form.instance.mailer = self.request.user
        return super().form_valid(form)

    def test_func(self):
        return self.request.user.has_perm("mailing.add_recipients")

    def handle_no_permission(self):
        return redirect("mailing:recipient_list")


class RecipientUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """CBV for recipient update"""

    model = Recipients
    form_class = RecipientForm
    template_name = "mailing/recipient_form.html"
    success_url = reverse_lazy("mailing:recipients_list")

    def test_func(self):
        return self.request.user == self.get_object().mailer

    def handle_no_permission(self):
        return redirect("mailing:recipient_detail", pk=self.kwargs["pk"])


class RecipientDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """CBV for recipient deletion"""

    model = Recipients
    template_name = "mailing/recipient_delete.html"
    success_url = reverse_lazy("mailing:recipients_list")

    def test_func(self):
        return self.request.user == self.get_object().mailer

    def handle_no_permission(self):
        return redirect("mailing:recipient_detail", pk=self.kwargs["pk"])


class MailingListView(LoginRequiredMixin, ListView):
    """CBV for mailing list"""

    model = Mailing
    template_name = "mailing/mailing_list.html"
    context_object_name = "mailings"

    def get_queryset(self):
        """Method to get user mailing list. and update satus of user mailings"""

        mailings_list = Mailing.objects.all().order_by("-start_at")

        if not self.request.user.has_perm("mailing.view_mailing"):
            mailings_list = mailings_list.filter(message__author=self.request.user)

        for mailing in mailings_list:
            mailing.update_status()

        return mailings_list


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
            # Use MailingServices start_mailing
            status_message = SMTPMailingHandler.start_mailing(mailing_item)

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


class MailingCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
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

    def test_func(self):
        return self.request.user.has_perm("mailing.add_mailing")

    def handle_no_permission(self):
        return redirect("mailing:mailing_list")


class MailingUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
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

    def test_func(self):
        return self.request.user == self.get_object().message.author

    def handle_no_permission(self):
        return redirect("mailing:mailing_detail", pk=self.kwargs["pk"])


class MailingDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """CBV for mailing delete"""

    model = Mailing
    template_name = "mailing/mailing_delete.html"
    success_url = reverse_lazy("mailing:mailing_list")

    def test_func(self):
        return self.request.user == self.get_object().message.author

    def handle_no_permission(self):
        return redirect("mailing:mailing_detail", pk=self.kwargs["pk"])


class MailingDisableView(LoginRequiredMixin, UserPassesTestMixin, View):
    """CBV for mailing disable"""

    def post(self, request, pk : int = None):
        mailing = get_object_or_404(Mailing, id=pk)

        if not request.user.has_perm('mailing.can_disabling_mailing'):
            return HttpResponseForbidden("У вас нет прав для блокировки рассылку")

        mailing.is_disabled = False if mailing.is_disabled else True
        mailing.save()

        return redirect('mailing:mailing_detail', pk=pk)

    def test_func(self):
        return self.request.user.has_perm("mailing.can_disabling_mailing")

    def handle_no_permission(self):
        return redirect("mailing:mailing_list")


class StatisticsView(LoginRequiredMixin, TemplateView):
    """CBV for mailing statistics"""

    template_name = "mailing/statistics.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = MailingAppQueries.get_statistics(context, user=self.request.user)
        return context


class MailingAttemptView(LoginRequiredMixin, ListView):
    """CBV for mailing attempt"""

    model = MailingAttempt
    template_name = "mailing/mailing_attempt.html"
    context_object_name = "mailing_attempts"

    def get_queryset(self):

        mailings_list = MailingAttempt.objects.all().order_by("-attempt_at")
        if self.request.user.has_perm("mailing.view_mailing"):
            return mailings_list
        else:
            return mailings_list.filter(mailing__message__author=self.request.user)


class MailingAttemptSuccessView(LoginRequiredMixin, ListView):
    """CBV for mailing statistics"""

    model = MailingAttempt
    template_name = "mailing/mailing_attempt_success.html"
    context_object_name = "mailing_attempts"

    def get_queryset(self):

        success_mailings_list = MailingAttempt.objects.all().filter(status="SUCCESS").order_by("-attempt_at")
        if self.request.user.has_perm("mailing.view_mailing"):
            return success_mailings_list
        else:
            return success_mailings_list.filter(mailing__message__author=self.request.user)


class MailingAttemptFailedView(LoginRequiredMixin, ListView):
    """CBV for mailing statistics"""

    model = MailingAttempt
    template_name = "mailing/mailing_attempt_failed.html"
    context_object_name = "mailing_attempts"

    def get_queryset(self):

        failed_mailings_list = MailingAttempt.objects.all().filter(status="FAILED").order_by("-attempt_at")
        if self.request.user.has_perm("mailing.view_mailing"):
            return failed_mailings_list
        else:
            return failed_mailings_list.filter(mailing__message__author=self.request.user)
