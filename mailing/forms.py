from django import forms
from PIL import Image

from .models import Message


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