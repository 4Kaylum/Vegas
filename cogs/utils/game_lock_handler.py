import asyncio
import collections

from discord.ext import commands


class GameLockHandler(object):

    locks = {}

    @classmethod
    async def lock(cls, _, ctx):
        current_lock, bet_message = cls.locks.get((ctx.guild.id, ctx.author.id,), (asyncio.Lock(), None,))
        if current_lock.locked():
            if bet_message:
                raise commands.CheckFailure(f"You can't bet multiple times at once - finish your current game first! (<{bet_message.jump_url}>)")
            raise commands.CheckFailure(f"You can't bet multiple times at once - finish your current game first! (could not find message)")
        await current_lock.acquire()
        cls.locks[(ctx.guild.id, ctx.author.id,)] = (current_lock, ctx.message,)

    @classmethod
    async def unlock(cls, _, ctx):
        current_lock, bet_message = cls.locks.get((ctx.guild.id, ctx.author.id,), (asyncio.Lock(), None,))
        current_lock.release()
        cls.locks[(ctx.guild.id, ctx.author.id,)] = (current_lock, None,)
