from django.shortcuts import render
import request
from django.http import JsonResponse
from .models import Ratings,Movies
# Create your views here.

def movies(request,id):
    if request.method == 'POST':
        data = request.POST.get()
        Movies.save(data)
    elif request.method == 'GET':
        data = Movies.objects.filter(id=id).get()
        return JsonResponse(data)
    