from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings

import google.generativeai as genai

from api.executor import PipelineExecutor
from api.functions import Execute
from api.models import Pipeline, PipelineStep


# Configure Gemini client
genai.configure(api_key=settings.GEMINI_API_KEY)

@api_view(['POST'])
def summarize_view(request):
    text = request.data.get('text')
    pipeline_id = 40
    result = Execute(pipeline_id).summarize_text(text)
    return Response({'Result': result})

@api_view(['POST'])
def scrape_view(request):
    url = request.data.get('url')
    pipeline_id = 40
    if not url:
        return Response({'Error': 'No url found'})
    
    result = Execute(pipeline_id).scrape_website(url)
    return Response({'Result': result})



@api_view(['POST'])
def run_step(request):
    step_type = request.data.get("step_type")
    input_text = request.data.get("input_text")

    if not step_type or not input_text:
        return Response(
            {"error": "step_type and input_text are required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if step_type == "SUMMARIZE":
        try:
            result = Execute().summarize_text(input_text)
            return Response({"result": result}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
        
    if step_type == "SCRAPE":
        try:
            result = Execute().scrape_website(input_text)
            return Response({"result": result}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    return Response(
        {"error": f"Unknown step type: {step_type}"},
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['POST'])
def create_pipeline(request):
    steps = request.data.get('steps')
    pipeline = Pipeline.objects.create()

    order = 1
    for i in steps:
        step_type = i['step_type']
        input_data = i['input_data']

        if order == 1:
            PipelineStep.objects.create(
                pipeline=pipeline,
                step_type=step_type,
                order=order,
                input_data=input_data
            )
        else:
            PipelineStep.objects.create(
                pipeline=pipeline,
                step_type=step_type,
                order=order,
                input_data=input_data
            )
        order+=1

    return Response({"pipeline_id": pipeline.id})


@api_view(['POST'])
def run_pipeline_api(request, pipeline_id):
    executor = PipelineExecutor(pipeline_id)
    result = executor.execute_pipeline()
    return Response({
        "message": "Pipeline executed successfully",
        "status": "COMPLETED",
        "result": result
    })
