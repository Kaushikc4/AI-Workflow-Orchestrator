from django.urls import path
from .views import run_step, scrape_view, summarize_view, create_pipeline, run_pipeline_api

urlpatterns = [
    path('run-step/', run_step, name='run-step'),
    path('summarize/', summarize_view, name='summarize_view'),
    path('scrape/', scrape_view, name='scrape_view'),
    path('create-pipeline/', create_pipeline, name='create_pipeline'),
    path('run-pipeline-api/<int:pipeline_id>/', run_pipeline_api, name='run_pipeline_api')
]