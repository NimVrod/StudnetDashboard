from django.http import HttpResponse
from django.shortcuts import render

def home(request):
    courses = [
        {
            'title': 'Elementy Elektroniczne EiT 23/24',
            'category': 'Elektronika i Telekomunikacja',
            'progress': 11,
            'image_url': '/static/images/course1.jpg',
        },
        # Add more course data as needed
    ]
    return render(request, 'home.html', {'courses': courses})