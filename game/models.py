from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class FighterModel(models.Model):
    user = models.ForeignKey(User, editable=False, on_delete=models.CASCADE)

    name = models.TextField(max_length=40)

    life = models.IntegerField()
    max_life = models.IntegerField()

    power = models.IntegerField()
    max_power = models.IntegerField()

    agility = models.IntegerField()
    max_agility = models.IntegerField()

    block = models.IntegerField()
    max_block = models.IntegerField()

    block_factor = models.IntegerField(default=0)

    energy = models.IntegerField()
    max_energy = models.IntegerField()

    rarity = models.TextField()
    wins = models.IntegerField(default=0)
    ko = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    draws = models.IntegerField(default=0)

    average = models.IntegerField()
    coins = models.IntegerField(default=0)

    hexed_instance = models.TextField()

    def __str__(self):
        return self.name