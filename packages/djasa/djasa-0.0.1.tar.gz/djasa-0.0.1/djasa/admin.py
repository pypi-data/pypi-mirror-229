import requests
from django.contrib import admin
from django.apps import apps
from django.shortcuts import render
from django.urls import path

from djasa.conf import djasa_settings
from djasa.views import send_training_data_to_rasa
from djasa.models import ChatHistory


class DjasaEntityAdmin(admin.ModelAdmin):
    change_list_template = 'change_list.html'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('send_training_data/', self.admin_site.admin_view(send_training_data_to_rasa),
                 name='send_training_data_to_rasa'),
        ]
        return custom_urls + urls


class DjasaAdminSite(admin.AdminSite):
    def register(self, model_or_iterable, admin_class=None, **options):
        # Apply Djasa's custom behavior if the model is in DJASA_ENTITIES
        if model_or_iterable in djasa_settings.DJASA_ENTITIES:
            admin_class = type('Combined' + model_or_iterable.__name__ + 'Admin',
                               (DjasaEntityAdmin, admin_class or admin.ModelAdmin),
                               {})
        super().register(model_or_iterable, admin_class, **options)


# Replace the default admin site with DjasaAdminSite
admin.site = DjasaAdminSite()


def register_admin():
    for entity_model in djasa_settings.DJASA_ENTITIES:
        if not admin.site.is_registered(entity_model):
            admin.site.register(entity_model)


register_admin()


class ChatHistoryAdmin(admin.ModelAdmin):
    change_form_template = 'change_form.html'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('chat_interface/', self.admin_site.admin_view(self.chat_interface), name='chat_interface'),
        ]
        return custom_urls + urls

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_chat_interface'] = True
        return super().change_view(
            request, object_id, form_url, extra_context=extra_context,
        )

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_continue'] = False
        extra_context['show_save_and_add_another'] = False
        extra_context['show_save'] = False
        return super().changeform_view(request, object_id, form_url, extra_context=extra_context)

    def chat_interface(self, request):
        if request.method == "POST":
            user_message = request.POST.get('user_message')
            response = requests.post(djasa_settings.RASA_WEBHOOK_ENDPOINT, json={"message": user_message})
            bot_response = response.json()
            if bot_response:
                bot_response_text = bot_response[0]['text']
            else:
                bot_response_text = "Sorry, I couldn't process that request."

            # Optionally save to ChatHistory
            ChatHistory.objects.create(user_message=user_message, bot_response=bot_response_text)

            context = {
                'user_message': user_message,
                'bot_response': bot_response_text
            }
            return render(request, 'chat_interface.html', context)

        return render(request, 'chat_interface.html')


admin.site.register(ChatHistory, ChatHistoryAdmin)
