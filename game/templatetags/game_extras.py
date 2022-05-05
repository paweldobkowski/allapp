from django import template

register = template.Library()

@register.filter(name='sub')
def sub(x, y):
    return x - y

@register.filter(name='recovery_cost')
def recovery_cost(player_coins, player_injury):
    try:
        cost = round(player_coins*player_injury)

    except:
        cost = 0  

    return cost