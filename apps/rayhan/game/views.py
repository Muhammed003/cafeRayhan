from django.shortcuts import render
from django.views.generic import TemplateView


# Create your views here.
class GameStartView(TemplateView):
    template_name = "rayhan/game/index.html"