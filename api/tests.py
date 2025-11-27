from django.test import TestCase

from api.functions import Execute

# Create your tests here.
class TestSummarizer(TestCase):
    def setUp(self):
        self.execute = Execute()

    def test_summarizer(self):
        input_data = '''Hello, everyone! Really nice to meet you. Today seems to be a really bright day. Let's go out and have some fun.'''
        response = self.execute.summarize_text(input_data)
        print(response)
        self.assertIsNotNone(response)


class TestWebScraping(TestCase):
    def setUp(self):
        self.execute = Execute(41)

    def test_web_scrape(self):
        # url = 'https://stackoverflow.com/questions/46038496/gradle-received-status-code-403-from-server-forbidden'
        url = 'https://www.merriam-webster.com/dictionary/response'
        response = self.execute.scrape_website(url)

        self.assertIn('html', response)
        self.assertIn('text', response)


class TestCreatePipeline(TestCase):

    def test_create_pipeline(self):
        url = "/api/create-pipeline/"

        payload = {
            "steps": [
            {
                "step_type": "TRANSLATE",
                "input_data": {
                    "input_text": "Hello, World!",
                    "target_lang": "Hindi"
                }
            },
            {
                'step_type': "SUMMARIZE",
                'input_data': {
                    'input_text': 'Hello World'
                }
            }
            ]
        }
        response = self.client.post(url, payload, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertIn("pipeline_id", response.data)


class TestTranslateText(TestCase):
    def setUp(self):
        self.execute = Execute(1)

    def test_translate_text(self):
        text = 'Hello, world!'
        target_lang = 'hi'
        data = {
            'text' : text,
            'lang' : target_lang
        }
        response = self.execute.translate_text(data)
        self.assertIsNotNone(response)


class TestCreatePipelineWithUIInput(TestCase):
    def test_create_pipeline(self):
        url = '/api/create-pipeline/'
        payload = {
            'steps': [
                {
                    'step_type': 'SCRAPE',
                    'input_data': {
                        'input_text': 'https://stackoverflow.com/questions/46038496/gradle-received-status-code-403-from-server-forbidden'
                    }
                },
                {
                    'step_type': 'SUMMARIZE',
                    'input_data': {
                        'input_text': 'Hello_world, how is the weather?'
                    }
                },
                {
                    'step_type': 'TRANSLATE',
                    'input_data': {
                        'input_text': 'Hello, world!',
                        'target_lang': 'Hindi'
                    }
                }
            ]
        }

        response = self.client.post(url, payload, content_type="application/json")

        self.assertIsNotNone(response)
