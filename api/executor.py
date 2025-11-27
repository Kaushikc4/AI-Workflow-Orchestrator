from .models import Pipeline
from api.functions import Execute


class PipelineExecutor:

    def __init__(self, pipeline_id):
        self.pipeline = Pipeline.objects.get(id=pipeline_id)

    def execute_pipeline(self):
        """Executes the pipeline sequentially."""
        self.pipeline.status = "RUNNING"
        self.pipeline.save()

        steps = self.pipeline.steps.order_by("order")

        previous_output = None
        for i_step in steps:
            if previous_output:
                i_step.input_data['input_text'] = previous_output
                i_step.save()

            step_input = i_step.input_data
            step_result = self.run_step(i_step.step_type, step_input)

            i_step.result = step_result
            i_step.save()

            previous_output = step_result

        self.pipeline.status = "COMPLETED"
        self.pipeline.save()

        return previous_output

    def run_step(self, step_type, input_data):
        if step_type == 'SUMMARIZE':
            return Execute(self.pipeline).summarize_text(input_data["input_text"])
        elif step_type == 'SCRAPE':
            return Execute(self.pipeline).scrape_website(input_data["input_text"])
        elif step_type == 'TRANSLATE':
            return Execute(self.pipeline).translate_text(input_data["input_text"], input_data["target_lang"])
        elif step_type == 'NOTIFY':
            return Execute(self.pipeline).send_notification(input_data)
        elif step_type == 'CUSTOM':
            return Execute(self.pipeline).custom_python(input_data["input_text"])
        else:
            raise ValueError(f'Unknown step-type {step_type}.')