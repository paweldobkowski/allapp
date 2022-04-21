from math import ceil
import random, os.path, pickle

from django.shortcuts import redirect

from .models import FighterModel

class Dice:
    def roll_one(self):
        return random.randint(1, 6)

    def roll_two(self):
        first = self.roll_one()
        second = self.roll_one()

        return first + second

class Fighter:
    def get_name(self):
        file_dir = os.path.dirname(os.path.abspath(__file__))

        with open(os.path.join(file_dir, "ani.txt"), "r") as ani, open(os.path.join(file_dir, "adj.txt"), "r") as adj:
            adjective = random.choice(adj.readlines())        
            animal = random.choice(ani.readlines())

            name = str(f'{adjective} {animal}')

        return name

    def __init__(self, user_id='999999999'):
        self.user_id = user_id
        self.name = self.get_name()

        self.life = random.randint(100, 200)
        self.max_life = self.life

        self.power = random.randint(1, 10)
        self.max_power = self.power

        self.agility = random.randint(1, 10)
        self.max_agility = self.agility

        self.block = random.randint(1, 5)
        self.max_block = self.block

        self.block_factor = 0

        self.energy = random.randint(3, 5)
        self.max_energy = self.energy

        rarity = None

        life_percent = (self.life/200)*100
        energy_percent = (self.energy/5)*100
        power_percent = (self.power/10)*100
        agility_percent = (self.agility/10)*100
        block_percent = (self.block/5)*100

        max_percent = (life_percent + energy_percent + power_percent + agility_percent + block_percent)/5

        # 0 - 70: COMMON
        # 70 - 80: RARE
        # 80 - 95: EPIC
        # 95 - 100: LEGENDARY

        if max_percent <= 70:
            rarity = 'COMMON'
        elif max_percent <= 80:
            rarity = 'RARE'
        elif max_percent <= 90:
            rarity = 'EPIC'
        else:
            rarity = 'LEGENDARY'  

        self.rarity = rarity

        self.wins = 0
        self.ko = 0
        self.losses = 0
        self.draws = 0

    def punch(self, who):
        # check how the punch connects
        player_agility = self.agility + Dice().roll_two()
        opponent_agility = who.agility + Dice().roll_two()

        if player_agility < opponent_agility: # if opponent is faster player does only half of damage
            damage = self.power * Dice().roll_two()
            opponent_block_value = damage * who.block_factor
            damage = ceil((damage - opponent_block_value)/2)

            if who.life - damage <= 0:
                who.life = 0
            else:
                who.life -= damage

            if self.energy <= 0:
                self.energy = 0

            else:
                self.energy -= 1

                x = 0.5/self.max_energy

                decrease_value_power = self.max_power*x
                decrease_value_agility = self.max_agility*x

                self.power = self.power - decrease_value_power
                self.agility = self.agility - decrease_value_agility

            return damage

        else: # if opponent is slower player does full damage
            damage = self.power * Dice().roll_two()
            opponent_block_value = damage * who.block_factor
            damage = ceil(damage - opponent_block_value)

            if who.life - damage <= 0:
                who.life = 0
            else:
                who.life -= damage

            if self.energy <= 0:
                self.energy = 0

            else:
                self.energy -= 1

                x = 0.5/self.max_energy

                decrease_value_power = self.max_power*x
                decrease_value_agility = self.max_agility*x

                self.power = self.power - decrease_value_power
                self.agility = self.agility - decrease_value_agility
            
            return damage

    def guard(self):
        damage = 0 # when player guards he does 0 damage

        block_effectiveness = self.block + Dice().roll_two()
        block_factor = 1 if block_effectiveness >= 10 else 0.2
        self.block_factor = block_factor

        if self.block <= 0:
            self.block = 0
        else:
            self.block -= 1

        return damage

    def recover(self):
        life_recovery_val = 20

        if self.life + life_recovery_val >= self.max_life:
            self.life = self.max_life
        else:
            self.life += life_recovery_val
        
        if self.energy >= self.max_energy:
            self.energy = self.max_energy
        else:
            self.energy += 1

        x = 0.5/self.max_energy

        decrease_value_power = self.max_power*x
        decrease_value_agility = self.max_agility*x

        if self.power >= self.max_power:
            self.power = self.max_power
        else:
            self.power = self.power + decrease_value_power

        if self.agility >= self.max_agility:
            self.agility = self.max_agility
        else:
            self.agility = self.agility + decrease_value_agility
        
        self.block_factor = 0

class Utilities:
    def hex_data(self, data):
        hexed_data = pickle.dumps(data).hex()

        return hexed_data

    def unhex_data(self, hexed_data):
        unhexed_data = pickle.loads(bytes.fromhex(hexed_data))

        return unhexed_data
    
    def put_thing_in_session(self, request, thing, name_of_thing, hex_it=True):
        if hex_it:
            thing = Utilities().hex_data(thing)

        request.session[name_of_thing] = thing

    def get_thing_from_session(self, request, things_name):
        hexed_thing = request.session.get(things_name)
        thing = Utilities().unhex_data(hexed_thing)
        
        return thing

class Referee:
    def check_for_knockout(self, request, game_state, player, opponent):
        if player.life == 0:
            player_score = game_state['total_score']['player_score']
            opponent_score = game_state['total_score']['opponent_score']
            round_num = game_state['round_num']

            game_state['is_over'] = True
            game_state['end_info']['who_won'] = 'opponent'
            game_state['end_info']['won_by'] = f'KNOCK OUT IN ROUND NUMBER {round_num}'

            Utilities().put_thing_in_session(request, game_state, 'game_state')

            return game_state
        
        elif opponent.life == 0:
            player_score = game_state['total_score']['player_score']
            opponent_score = game_state['total_score']['opponent_score']
            round_num = game_state['round_num']

            game_state['is_over'] = True
            game_state['end_info']['who_won'] = 'player'
            game_state['end_info']['won_by'] = f'KNOCK OUT IN ROUND NUMBER {round_num}'

            Utilities().put_thing_in_session(request, game_state, 'game_state')

            return game_state
        
class Judge:
    def score_round(self, player_performance, opponent_performance):
        if player_performance == opponent_performance:
            player_score = 10
            opponent_score = 10
        
        elif player_performance > opponent_performance:
            player_score = 10
            opponent_score = 9

        else:
            player_score = 9
            opponent_score = 10

        score = {
            'player_score': player_score,
            'opponent_score': opponent_score,
        }

        return score

    def total(self, j1, j2, j3, previous_total):
        total_score = {k: j1.get(k) + j2.get(k) + j3.get(k) + previous_total.get(k) for k in j1}
        
        return total_score

    def player_record_update(self, request, user_id, win=None, by_ko=False):
        player = FighterModel.objects.filter(user_id=user_id)
        player = player[0]

        hexed_player_instance = player.hexed_instance
        player_instance = Utilities().unhex_data(hexed_player_instance)

        if win:
            player.wins += 1
            player_instance.wins += 1

            if by_ko:
                player.ko += 1
                player_instance.ko += 1

        elif win == False:
            player.losses += 1
            player_instance.losses += 1

        elif win == None:
            player.draws += 1
            player_instance.draws += 1

        Utilities().put_thing_in_session(request, player_instance, 'player')

        player.hexed_instance = Utilities().hex_data(player_instance)        
        player.save()

class Fight:
    def opponent_logic(self):
        strategies = ['attack', 'defend']
        opponent_s = random.choice(strategies)

        return opponent_s

    def pre_fight(self, request):

        # pre_fight method has three objectives:
        # create opponent
        # put opponent and player in the 'game_state' object, hex it and store it in the session (so we avoid querying the database)
        # put 'game_is': 'on' in session so we know player is playing

        player = Utilities().get_thing_from_session(request, 'player')
        opponent = Fighter()

        game_state = {
            'round_num': 0,
            'is_over': False,

            'last_round_log': {
                'opponent_strategy': '',
                'player_strategy': '',

                'opponent_dmg_taken': '',
                'player_dmg_taken': '',

                'opponent_agility': '',
                'player_agility': '',
            },

            'end_info': {
                'who_won': None,
                'won_by': None,
            },

            'total_score': {
                'player_score': 0,
                'opponent_score': 0,
            },

            'player': {
                'instance': player,
                'knocked_down': 0,
            },

            'opponent': {
                'instance': opponent,
                'knocked_down': 0,
            },
        }

        Utilities().put_thing_in_session(request, game_state, 'game_state')

# GAME %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% GAME

    def round(self, request, player_strategy):
        game_state = Utilities().get_thing_from_session(request, 'game_state')
        round_num = game_state['round_num']
        
        #START
        if round_num == 0: # FIRST ROUND
            game_state['round_num'] = 1

            Utilities().put_thing_in_session(request, game_state, 'game_state')

            return game_state

        elif round_num in range(1,13):
            player_strategy = player_strategy
            opponent_strategy = self.opponent_logic()

            # getting player and opponent class instances ready
            # FOR PLAYER:
            player = game_state['player']['instance']

            # FOR OPPONENT:
            opponent = game_state['opponent']['instance']

            player_performance = 0 # WE SET BOTH PERFORMANCES TO 0 TO RESET EVERYTIME AND IN CASE A KNOCKOUT
            opponent_performance = 0

            life_before_round_player = player.life
            life_before_round_opponent = opponent.life

            if player_strategy == 'attack' and opponent_strategy == 'attack':

                # agility and two dice roll (total) determines who attacks first
                player_total = 0
                opponent_total = 0

                while player_total == opponent_total: # reroll until someone wins
                    player_dice_roll = Dice().roll_two()
                    opponent_dice_roll = Dice().roll_two()

                    player_total = player.agility + player_dice_roll
                    opponent_total = opponent.agility + opponent_dice_roll



                if player_total > opponent_total:                       # player hits first
                    player_performance = player.punch(opponent)
                    knock_out = Referee().check_for_knockout(request, game_state, player, opponent)
                    if knock_out:

                        user_id = request.session.get('user_id')
                        Judge().player_record_update(user_id=user_id, request=request, win=True, by_ko=True)
                        return knock_out

                    opponent_performance = opponent.punch(player)
                    knock_out = Referee().check_for_knockout(request, game_state, player, opponent)
                    if knock_out:
                        
                        user_id = request.session.get('user_id')
                        Judge().player_record_update(user_id=user_id, request=request, win=False)
                        return knock_out

                else:                                                   # opponent hits first
                    opponent_performance = opponent.punch(player)
                    knock_out = Referee().check_for_knockout(request, game_state, player, opponent)
                    if knock_out:
                        
                        user_id = request.session.get('user_id')
                        Judge().player_record_update(user_id=user_id, request=request, win=False)
                        return knock_out

                    player_performance = player.punch(opponent)
                    knock_out = Referee().check_for_knockout(request, game_state, player, opponent)
                    if knock_out:

                        user_id = request.session.get('user_id')
                        Judge().player_record_update(user_id=user_id, request=request, win=True, by_ko=True)
                        return knock_out

            elif player_strategy == 'defend' and opponent_strategy == 'defend':
                print(game_state['total_score']['player_score'])
                player_performance = player.guard()
                player.recover()

                opponent_performance = opponent.guard()
                opponent.recover()

            elif player_strategy == 'defend' and opponent_strategy == 'attack':
                player_performance = player.guard()
                opponent_performance = opponent.punch(player)
                knock_out = Referee().check_for_knockout(request, game_state, player, opponent)
                if knock_out:
                    
                    user_id = request.session.get('user_id')
                    Judge().player_record_update(user_id=user_id, request=request, win=False)
                    return knock_out

                player.recover()

            elif player_strategy == 'attack' and opponent_strategy == 'defend':
                opponent_performance = opponent.guard()
                player_performance = player.punch(opponent)
                knock_out = Referee().check_for_knockout(request, game_state, player, opponent)
                if knock_out:

                    user_id = request.session.get('user_id')
                    Judge().player_record_update(user_id=user_id, request=request, win=True, by_ko=True)
                    return knock_out

                opponent.recover()

            life_after_round_player = player.life
            life_after_round_opponent = opponent.life

            player_life_change = life_after_round_player - life_before_round_player
            opponent_life_change = life_after_round_opponent - life_before_round_opponent

            player_block = 'all' if opponent_strategy == 'attack' and opponent_performance == 0 else 'some'
            opponent_block = 'all' if player_strategy == 'attack' and player_performance == 0 else 'some'

            # LAST ROUND LOG
            last_round_log = {
                'opponent_strategy': opponent_strategy,
                'player_strategy': player_strategy,

                'opponent_dmg_done': opponent_performance,
                'player_dmg_done': player_performance,

                'opponent_life_change': opponent_life_change,
                'player_life_change': player_life_change,
            }

            # UPDATE THE GAME STATE ---------------------------------------------------------------------------------------------------------
            # SCORE THE ROUND:
            game_state = Utilities().get_thing_from_session(request, 'game_state')

            game_state['last_round_log'] = last_round_log

            j1 = Judge().score_round(player_performance, opponent_performance)
            j2 = Judge().score_round(player_performance, opponent_performance)
            j3 = Judge().score_round(player_performance, opponent_performance)

            previous_total = game_state['total_score']

            # SCORES:
            new_total_score = Judge().total(j1, j2, j3, previous_total)
            game_state['total_score'] = new_total_score

            # OPPONENT:
            game_state['opponent']['instance'] = opponent

            # FOR PLAYER:
            game_state['player']['instance'] = player

            # INCREASE ROUND COUNT
            round_num += 1
            game_state['round_num'] = round_num

            # HEX THE NEW GAME STATE AND STORE IT IN SESSION
            Utilities().put_thing_in_session(request, game_state, 'game_state')

            # END OF UPDATING THE STATE -----------------------------------------------------------------------------------------------------

        elif round_num == 13: # DECISION
            game_state['is_over'] = True

            user_id = request.session.get('user_id') # get logged user_id
            player = FighterModel.objects.get(user_id=user_id) # query the database for the fighter

            player_score = game_state['total_score']['player_score']
            opponent_score = game_state['total_score']['opponent_score']

            if player_score > opponent_score:
                game_state['end_info']['who_won'] = 'player'
                game_state['end_info']['won_by'] = 'UNANIMOUS DECISION'

                Judge().player_record_update(user_id=user_id, request=request, win=True)

                Utilities().put_thing_in_session(request, game_state, 'game_state')

                return game_state

            elif player_score < opponent_score:
                game_state['end_info']['who_won'] = 'opponent'
                game_state['end_info']['won_by'] = 'UNANIMOUS DECISION'

                Judge().player_record_update(user_id=user_id, request=request, win=False)

                Utilities().put_thing_in_session(request, game_state, 'game_state')

                return game_state
                
            else:
                game_state['end_info']['who_won'] = None
                game_state['end_info']['won_by'] = 'UNANIMOUS DECISION'

                Judge().player_record_update(user_id=user_id, request=request)

                Utilities().put_thing_in_session(request, game_state, 'game_state')

                return game_state
