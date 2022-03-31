from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone as dtz
from datetime import datetime, timezone, timedelta
from . import models
from datetime import date

# Create your views here.

def add_note(request):
    if request.session.get("is_logged") != True:
        return redirect('start')

    if request.method == 'POST':

        note_content = request.POST.get('content')
        note_deadline = request.POST.get('deadline')
        user_id = request.session.get('user_id')

        if request.POST.get('deadline') != '':
            note_deadline = datetime.strptime(note_deadline, '%Y-%m-%d').date()
            new_note = models.Note(content = note_content, deadline = note_deadline, user_id=user_id)
        else:
            new_note = models.Note(content = note_content, user_id=user_id)

        new_note.save()

        return redirect(reverse('noter:add_note'))

    else:

        today = dtz.localdate() #- timedelta(days=1)
        week = timedelta(weeks=1)
        week_before_today = today - week

        if request.session.get('show_all') == 'checked':
            notes_to_show = models.Note.objects.filter(deadline__gte=week_before_today, user_id=request.session.get('user_id')).order_by('is_done', 'deadline')
        
        elif request.session.get('only_done') == 'checked':
            notes_to_show = models.Note.objects.filter(deadline__gte=week_before_today, user_id=request.session.get('user_id')).order_by('is_done', 'deadline')
            notes_to_show = notes_to_show.filter(is_done=True)

        else:
            notes_to_show = models.Note.objects.filter(deadline__gte=week_before_today, user_id=request.session.get('user_id')).order_by('is_done', 'deadline')
            notes_to_show = notes_to_show.filter(is_done=False)

        context = {
            'today': today,
            'notes_to_show': notes_to_show,
            'noter': 'active',
            'is_logged': request.session.get('is_logged'),
        }

        return render(request, 'noter/add_note.html', context=context)

def clear_all_notes(request):

    models.Note.objects.all().delete()

    return redirect(reverse('noter:add_note'))

def note_is_done(request, id):
    if request.session.get("is_logged") != True:
        return redirect('start')

    note_to_update = models.Note.objects.get(id=id)
    note_to_update.is_done = True

    note_to_update.save()

    return redirect(reverse('noter:add_note'))

def delete_note(request, id):
    if request.session.get("is_logged") != True:
        return redirect('start')

    note_to_update = models.Note.objects.get(id=id)
    note_to_update.delete()

    return redirect(reverse('noter:add_note'))

def show_all_radio(request):
    if request.session.get("is_logged") != True:
        return redirect('start')

    request.session['show_all'] = 'checked'
    request.session['only_done'] = ''
    request.session['only_pending'] = ''

    return redirect(reverse('noter:add_note'))

def only_done_radio(request):
    if request.session.get("is_logged") != True:
        return redirect('start')

    request.session['show_all'] = ''
    request.session['only_done'] = 'checked'
    request.session['only_pending'] = ''

    return redirect(reverse('noter:add_note'))

def only_pending_radio(request):
    if request.session.get("is_logged") != True:
        return redirect('start')

    request.session['show_all'] = ''
    request.session['only_done'] = ''
    request.session['only_pending'] = 'checked'

    return redirect(reverse('noter:add_note'))
