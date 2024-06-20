from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.predict_image, name='predict_image'),
]
