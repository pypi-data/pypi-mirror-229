from django.http import JsonResponse, HttpResponseRedirect
import requests

from django.urls import reverse

from djasa.conf import djasa_settings

from djasa.utils.rasa_helpers import generate_training_data


def send_training_data():
    training_data_yaml = generate_training_data()
    headers = {"Content-Type": "application/x-yaml"}  # Specify the content type for YAML data
    response = requests.post(djasa_settings.RASA_TRAINING_ENDPOINT, data=training_data_yaml, headers=headers)
    if response.status_code == 200:
        model_name = response.headers.get("filename")
        model_file_path = f"models/{model_name}"  # Adjust the path based on your Rasa setup
        replace_model_response = requests.put(djasa_settings.RASA_MODEL_ENDPOINT, json={"model_file": model_file_path})
        if replace_model_response.status_code == 204:
            return JsonResponse({"status": "success", "message": "Model trained and replaced successfully!"})
        else:
            return JsonResponse({"status": "error",
                                 "message": f"Failed to replace the model. Status code: {replace_model_response.status_code}, Response: {replace_model_response.text}"})
    else:
        return JsonResponse({"status": "error",
                             "message": f"Failed to train the model. Status code: {response.status_code}, Response: {response.text}"})


def send_training_data_to_rasa(request):
    send_training_data()  # This function will handle sending the training data to Rasa
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('admin:index')))
