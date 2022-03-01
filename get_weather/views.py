from django.shortcuts import render, redirect
import requests
from time import sleep
from lxml import html

# Create your views here.


def before_display(request):
    if request.session.get("is_logged") != True:
        return redirect('start')    

    context = {
        'weather_app': 'active',
        'is_logged': request.session.get('is_logged'),
    }
    return render(request, 'get_weather/before_display.html', context=context)

def get_weather(request):
    if request.session.get("is_logged") != True:
        return redirect('start')    

    if request.method == "POST":   
        city = request.POST.get('city')
        site = 'https://www.meteoprog.pl/pl/weather/'
        
        #  usuwanie znaków diakrytycznych
        strange='łŁśŚćĆńŃęĘąĄźŹ'
        ascii_replacements='llssccnneeaazz'
        translator = str.maketrans(strange, ascii_replacements)
        city_corrected = city.translate(translator)
        #  koniec usuwania

        url = site + city_corrected
        page = requests.get(url)
        structured = html.fromstring(page.content)
             
        temp = structured.xpath('/html/body/div[3]/main/article/section[1]/div/div/div/text()')[0].strip()                      
        temp_sensed = structured.xpath('/html/body/div[3]/main/article/section[1]/div/span/b/text()')[0].strip()
        time = structured.xpath('/html/body/div[3]/main/article/section[1]/div/h2/text()')[0].strip()

        context = {
            'last_search': city,
            'weather_app': 'active',
            'temp': temp, 
            'time': time, 
            'temp_sensed': temp_sensed,
            'is_logged': request.session.get('is_logged'),
        }

        return render(request, 'get_weather/display_data.html', context=context)
    else:
        return render(request, 'get_weather/before_display.html')
