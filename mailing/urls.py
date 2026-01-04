from django.urls import path

from . import views

app_name = "mailing"

urlpatterns = [
    path("home/", views.HomeView.as_view(), name="home"),
    path("message/", views.MessageListView.as_view(), name="message_list"),
    path("message/create/", views.MessageCreateView.as_view(), name="message_create"),
    path("message/<int:pk>/", views.MessageDetailView.as_view(), name="message_detail"),
    path("message/<int:pk>/update/", views.MessageUpdateView.as_view(), name="message_update"),
    path("message/<int:pk>/delete/", views.MessageDeleteView.as_view(), name="message_delete"),
    path("recipients/", views.RecipientsListView.as_view(), name="recipients_list"),
    path("recipients/create/", views.RecipientCreateView.as_view(), name="recipient_create"),
    path("recipients/<int:pk>/", views.RecipientDetailView.as_view(), name="recipient_detail"),
    path("recipients/<int:pk>/update/", views.RecipientUpdateView.as_view(), name="recipient_update"),
    path("recipients/<int:pk>/delete/", views.RecipientDeleteView.as_view(), name="recipient_delete"),
    path("mailing/", views.MailingListView.as_view(), name="mailing_list"),
    path("mailing/create/", views.MailingCreateView.as_view(), name="mailing_create"),
    path("mailing/<int:pk>/", views.MailingDetailView.as_view(), name="mailing_detail"),
    path("mailing/<int:pk>/update/", views.MailingUpdateView.as_view(), name="mailing_update"),
    path("mailing/<int:pk>/delete/", views.MailingDeleteView.as_view(), name="mailing_delete"),
    path("mailing/<int:pk>/disable/", views.MailingDisableView.as_view(), name="mailing_disable"),
    path("statistics/", views.StatisticsView.as_view(), name="statistics"),
    path("mailing_attempt/", views.MailingAttemptView.as_view(), name="mailing_attempt"),
    path("mailing_attempt/success/", views.MailingAttemptSuccessView.as_view(), name="mailing_attempt_success"),
    path("mailing_attempt/failed/", views.MailingAttemptFailedView.as_view(), name="mailing_attempt_failed"),
]
