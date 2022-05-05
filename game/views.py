from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse

import os.path
import random, json, pickle

from .models import FighterModel
from .fight_game import Fighter, Fight, Judge, Utilities, Doctor, Trainer

# Create your views here.

def main(request):
    if request.session.get('is_logged') != True:
        return redirect('start')
    
    if request.session.get('opponent_selected'):
        return redirect(reverse('game:fight'))

    user_id = request.session.get('user_id')
    
    if request.method == "POST": # WHEN USER CLAIMS THE FIGHTER
        player = Fighter(user_id, points=10)

        Utilities().put_thing_in_session(request, player, 'player') # putting player class instance in session

        new_fighter = FighterModel(
            user_id=player.user_id,
            name=player.name,

            life=player.life, 
            max_life=player.max_life,

            power=player.power, 
            max_power=player.max_power, 

            agility=player.agility,
            max_agility=player.max_agility,

            block=player.block,
            max_block=player.max_block,

            energy=player.energy,
            max_energy=player.max_energy,

            average=player.average,

            rarity=player.rarity,

            coins=player.coins,

            hexed_instance = Utilities().hex_data(player) # in order to be able to access class, not only model
            )
        
        new_fighter.save()

        return redirect(reverse('game:main'))

    power_disabled = ''
    agility_disabled = ''
    energy_disabled = ''
    block_disabled = ''

    point_cost = None

    try:
        player = FighterModel.objects.filter(user_id=user_id)
        player_instance = player[0].hexed_instance

        Utilities().put_thing_in_session(request, player_instance, 'player', False)

        player = Utilities().unhex_data(player[0].hexed_instance)
        point_cost = round((1.2**(player.average))*2)

        if player.coins < point_cost:
            power_disabled = 'disabled'
            agility_disabled = 'disabled'
            energy_disabled = 'disabled'
            block_disabled = 'disabled'

        if player.power >= 10:
            power_disabled = 'disabled'

        if player.agility >= 10:
            agility_disabled = 'disabled'

        if player.energy >= 5:
            energy_disabled = 'disabled'
        
        if player.block >= 5:
            block_disabled = 'disabled'

        player_injured_life = player.life - round(player.life*player.injury*2)

    except:
        player = None

    context = {
        'player': player,
        'player_injured_life': player_injured_life,
        'power_disabled': power_disabled,
        'agility_disabled': agility_disabled,
        'energy_disabled': energy_disabled,
        'block_disabled': block_disabled,
        'point_cost': point_cost,
        'game': 'active',
        'is_logged': request.session.get('is_logged'),
    }
    
    return render(request, 'game/main.html', context=context)

def introduction(request):
    if request.session.get('is_logged') != True:
        return redirect(reverse('game:main'))

    if request.session.get('opponent_selected'):
        return redirect(reverse('game:fight'))

    if request.method == "POST":
        Fight().pre_fight(request)

        return redirect(reverse('game:introduction'))

    else:
        hexed_player = request.session.get('player')

        if hexed_player:
            player = Utilities().unhex_data(hexed_player)

        if not request.session.get('game_state'):
            return redirect(reverse('game:main'))

        game_state = Utilities().get_thing_from_session(request, 'game_state')
        opponent = game_state['opponent']['instance']
        reward = game_state['opponent']['reward']

        context = {
            'player': player,
            'opponent': opponent,
            'reward': reward,
            'game': 'active',
            'is_logged': request.session.get('is_logged'),
        }
        
        return render(request, 'game/intro.html', context=context)

def fight(request):
    if request.session.get('is_logged') != True:
        return redirect('start')

    if request.method == 'POST':

        Utilities().put_thing_in_session(request, True, 'opponent_selected', False) # ENEMY IS SELECTED SO USER CANT GO BACK

        player_strategy = request.POST.get('decision') if request.POST.get('decision') else 'defend'
        game_state = Fight().round(request, player_strategy)
        
        return redirect(reverse('game:fight'))

    try:
        game_state = Utilities().get_thing_from_session(request, 'game_state')
    except:
        return redirect(reverse('game:main'))
    
    if game_state['is_over']:

        return redirect(reverse('game:summary'))

    else:
        if not request.session.get('game_state'):
            return redirect(reverse('game:main'))

        round_num = game_state['round_num']
        player = game_state['player']['instance']
        opponent = game_state['opponent']['instance']
        last_round_log = game_state['last_round_log']

        # values to mark the max value
        # opponent:
        olife_diff = opponent.max_life - opponent.life
        oenergy_diff = opponent.max_energy - opponent.energy
        opower_diff = opponent.max_power - opponent.power
        oagility_diff = opponent.max_agility - opponent.agility
        oblock_diff = opponent.max_block - opponent.block

        # player:
        plife_diff = player.max_life - player.life
        penergy_diff = player.max_energy - player.energy
        ppower_diff = player.max_power - player.power
        pagility_diff = player.max_agility - player.agility
        pblock_diff = player.max_block - player.block    

        context = {
            'olife_diff': olife_diff,
            'oenergy_diff': oenergy_diff,
            'opower_diff': opower_diff,
            'oagility_diff': oagility_diff,
            'plife_diff': plife_diff,
            'penergy_diff': penergy_diff,
            'ppower_diff': ppower_diff,
            'pagility_diff': pagility_diff,
            'round_num': round_num,
            'player': player,
            'opponent': opponent,
            'last_round_log': last_round_log,
            'game': 'active',
            'is_logged': request.session.get('is_logged'),
        }

        return render(request, 'game/fight.html', context=context)

def summary(request):
    if request.session.get('is_logged') != True:
        return redirect('start')

    if not request.session.get('game_state'):
        return redirect(reverse('game:main'))

    game_state = Utilities().get_thing_from_session(request, 'game_state')
    is_over = game_state['is_over']

    if is_over:
        Utilities().put_thing_in_session(request, False, 'opponent_selected', False) # FIGHT IS OVER SO WE CAN UNSELECT THE OPPONENT

        if request.method == 'POST':
            return redirect(reverse('game:summary'))

        player = game_state['player']['instance']
        player_score = game_state['total_score']['player_score']
        opponent_score = game_state['total_score']['opponent_score']
        reward = game_state['opponent']['reward']

        who_won = game_state['end_info']['who_won']
        won_by = game_state['end_info']['won_by']

        j1_score = {
            'p_s': int(player_score/3),
            'o_s': int(opponent_score/3),
        }

        j2_score = {
            'p_s': int(player_score/3),
            'o_s': int(opponent_score/3),
        }

        j3_score = {
            'p_s': int(player_score/3),
            'o_s': int(opponent_score/3),
        }

        context = {
            'j1_score': j1_score,
            'j2_score': j2_score,
            'j3_score': j3_score,
            'who_won': who_won,
            'won_by': won_by,
            'player': player,
            'reward': reward,
            'game': 'active',
            'is_logged': request.session.get('is_logged'),
        }

        del request.session['game_state']
        del request.session['opponent_selected']

        return render(request, 'game/summary.html', context=context)

    elif request.session.get('opponent_selected'):
        return redirect(reverse('game:fight'))

def skip(request):
    Fight().pre_fight(request)

    return redirect(reverse('game:introduction'))

def recover_after_loss(request):
    if request.session.get('is_logged') != True:
        return redirect('start')

    if request.method == 'POST':
        user_id = request.session.get('user_id')
        request.POST.get('stat_to_buy')
        Doctor().recover_after_loss(request, user_id=user_id)

    return redirect(reverse('game:main'))

def buy_stat(request):
    if request.session.get('is_logged') != True:
        return redirect('start')

    if request.method == 'POST':
        stat_to_buy = request.POST.get('stat_to_buy')
        user_id = request.session.get('user_id')
        Trainer().add_one_point(request, user_id=user_id, stat=stat_to_buy)

    return redirect(reverse('game:main'))


def clear(request):
    FighterModel.objects.all().delete()

    try:
        del request.session['player']
        del request.session['opponent']
        del request.session['player_state']
        del request.session['opponent_state']
        del request.session['game_state']
    except:
        pass

    return redirect(reverse('game:main'))