from django.shortcuts import render
from .models import Incident
def incident_list(request):
    # Извлекаем данные из базы
    incidents = Incident.objects.all()
    # Передаем данные в шаблон
    return render(request, 'main/incident_list.html', {'incidents': incidents})

def map(request):
    return render(request,'main/map.html')

