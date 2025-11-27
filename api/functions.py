# from api.views import run_summarizer
import google.generativeai as genai
from bs4 import BeautifulSoup
import requests
from api.models import Pipeline, PipelineStep
from twilio.rest import Client
from django.conf import settings

class Execute:
    """Execute the given task."""
    def __init__(self, pipeline):
        self.pipeline=pipeline

    def summarize_text(self, input_text):
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(f"Summarize this text:\n{input_text}")
        return response.text if hasattr(response, "text") else ""

    def scrape_website(self, url) -> dict:
        """
            Scrapes a website and returns
            raw html
            scraped text
        """
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            }
            response = requests.get(url, timeout=10, headers=headers)

            if response.status_code != 200:
                return {
                    f'Error: An error occurred with status code {response.status_code}'
                }
            
            html = response.text
            soup = BeautifulSoup(html, "html.parser")
            text = soup.get_text(separator="\n")

            # storing input for the next step
            order = PipelineStep.objects.filter(pipeline=self.pipeline,step_type='SCRAPE').values_list('order', flat=True).first()
            order = order+1
            if PipelineStep.objects.filter(pipeline=self.pipeline,order=order):
                pipeline_input = PipelineStep.objects.get(pipeline=self.pipeline,order=order)
                pipeline_input.input_data['input_text'] = text
                pipeline_input.save()

            return {
                'html': html,
                'text': text.strip()
            }
        except Exception as e:
            return {
                'Error': str(e)
            }
    
    def translate_text(self, input_text, target_lang):
        """Translate the input text into the target language."""
        if not input_text or not target_lang:
            return f'No input text or target language was given to translate.'
        
        prompt = f'Translate the following text into the target language {target_lang} and only return the translated text.:\n\n{input_text}.'

        try:
            model=genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(prompt)
            return response.text if hasattr(response, "text") else ""
        except Exception as e:
            return f"Translation error {str(e)}"

    def send_notification(self, input_data):
        method = input_data['method']
        reciever = input_data['reciever']
        message = input_data['input_text']

        client = Client(settings.TWILIO_SID, settings.TWILIO_TOKEN)
        if method == 'WHATSAPP':
            client.messages.create(
                from_=settings.TWILIO_WHATSAPP_FROM,  # Twilio sandbox number
                body=message,
                to=f"whatsapp:{reciever}"
            )
        elif method == 'SMS':
            client.messages.create(
                from_=settings.TWILIO_FROM,  # your Twilio SMS number
                body=message,
                to=reciever
            )
    
    def custom_python(input_data):
        return 'Custom Python'
