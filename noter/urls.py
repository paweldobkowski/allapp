from django.urls import path
from . import views

app_name = 'noter'

urlpatterns = [
    path('', views.add_note, name='add_note'),
    path('is_done/<int:id>', views.note_is_done, name='note_is_done'),
    path('delete/<int:id>', views.delete_note, name='delete_note'),
    path('only_done/', views.only_done_radio, name="only_done_radio"),
    path('show_all/', views.show_all_radio, name="show_all_radio"),
    path('only_pedning/', views.only_pending_radio, name="only_pending_radio"),
    path('c/', views.clear_all_notes, name='clear_all_notes'),
]