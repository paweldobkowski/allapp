from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User

def start(request):
    if request.method == "POST":
        try:
            user_input = request.POST['username']
            u = User.objects.get(username=user_input)
        except:
            messages.info(request, f'Użytkownik {user_input} nie istnieje!')
            return redirect('start')

        if u.check_password(request.POST.get('password')):

            request.session['is_logged'] = True
            request.session['user_id'] = u.id
            request.session['username'] = u.username
            request.session['show_all'] = 'checked'
            
            return redirect('start')

        else:
            messages.info(request, f'Błędne hasło dla użytkownika {u.username}')
            return redirect('start')

    else:

        context = {
            'start': 'active',
            'is_logged': request.session.get("is_logged"),
            'username': request.session.get("username")
        }

        return render(request, 'index.html', context=context)
