import asyncio
import collections

from discord.ext import commands


class GameLockHandler(object):

    locks = collections.defaultdict(lambda: (asyncio.Lock(), None))

    @classmethod
    async def lock(cls, _, ctx):
        current_lock, bet_message = cls.locks[(ctx.guild.id, ctx.author.id,)]
        if current_lock.locked():
            raise commands.CheckFailure(f"You can't bet multiple times at once - finish your current game first! (<{bet_message.jump_url}>)")
        await current_lock.lock()
        cls.locks[(ctx.guild.id, ctx.author.id,)] = (current_lock, ctx.message,)

    @classmethod
    async def unlock(cls, _, ctx):
        current_lock, bet_message = cls.locks[(ctx.guild.id, ctx.author.id,)]
        await current_lock.unlock()

