from discord.ext import vbu

from . import autocomplete
from .cards import Card, Deck, Hand
from .currency_amount import CurrencyAmount, BetAmount
from .game_lock_handler import GameLockHandler


class GamblingCog(vbu.Cog[vbu.Bot]):

    def __init__(self, bot: vbu.Bot):
        super().__init__(bot)
        for command in self.walk_commands():
            command.before_invoke(GameLockHandler.lock)
            command.after_invoke(GameLockHandler.unlock)
