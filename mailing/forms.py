from django import forms
from PIL import Image
from bootstrap_datepicker_plus.widgets import DatePickerInput, DateTimePickerInput


from .models import Message, Recipients, Mailing


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        exclude = ["created_at", "updated_at", "author"]

    def __init__(self, *args, **kwargs):

        super(MessageForm, self).__init__(*args, **kwargs)

        self.fields["title"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Тема",
            }
        )
        self.fields["content"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Сообщение",
            }
        )

class RecipientForm(forms.ModelForm):

    class Meta:
        model = Recipients
        exclude = ["mailer"]

    def __init__(self, *args, **kwargs):

        super(RecipientForm, self).__init__(*args, **kwargs)

        self.fields["email"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "почта",
            }
        )
        self.fields["full_name"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "полное имя",
            }
        )
        self.fields["comment"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "комментарии",
            }
        )

class MailingForm(forms.ModelForm):

    class Meta:
        model = Mailing
        exclude = ["status", "recipients"]
        widgets = {
            "start_at": DateTimePickerInput(
                options={"format": "DD/MM/YYYY, HH:mm", "showTodayButton": True},
                attrs={'class': 'form-control'}
            ),
            "end_at": DateTimePickerInput(
                options={"format": "DD/MM/YYYY, HH:mm", "showTodayButton": True},
                attrs={'class': 'form-control'}
            ),
        }


    def __init__(self, *args, **kwargs):

        super(MailingForm, self).__init__(*args, **kwargs)

        self.fields["message"].widget.attrs.update(
            {
                "class": "form-select",
                "placeholder": "Выберите тему сообщения",
            }
        )

        # self.fields["start_at"].widget.attrs.update(
        #     {
        #         'type': 'date',
        #     }
        # )


