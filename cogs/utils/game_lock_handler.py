import asyncio
import collections

from discord.ext import commands


class GameLockHandler(object):

    locks = collections.defaultdict(asyncio.Lock)

    @classmethod
    async def lock(cls, ctx):
        current_lock = cls.locks[(ctx.guild.id, ctx.author.id,)]
        if current_lock.locked:
            raise commands.CheckFailure("You can't bet multiple times at once!")
        await current_lock.lock()

    @classmethod
    async def unlock(cls, ctx):
        current_lock = cls.locks[(ctx.guild.id, ctx.author.id,)]
        await current_lock.unlock()

