import random

import discord
from discord.ext import commands
import voxelbotutils as utils


class DiceCommands(utils.Cog):

    async def roll_dice(self, ctx: utils.Context, dice_limit: int, multiplier: int, bet: localutils.CurrencyAmount):
        """
        Roll the dice on the user's bet.
        """

        # Work out what the user's rolled
        rolled_number = random.randint(1, 100)
        user_won = rolled_number > dice_limit

        # Work out what to say to the user
        embed = utils.Embed(title=f"\N{GAME DIE} {rolled_number}")
        if user_won:
            embed.colour = discord.Colour.green()
            embed.description = "You won! :D"
            if bet.amount:
                embed.description = f"You won! Added **{bet.amount * (multiplier - 1):,}** to your account! :D"
            win_amount = bet.amount * (multiplier - 1)
        else:
            embed.colour = discord.Colour.red()
            embed.description = "You lost :c"
            if bet.amount:
                embed.description = f"You lost, removed **{bet.amount:,}** from your account :c"
            win_amount = -bet.amount

        # Tell the user all is well
        self.bot.dispatch("transaction", ctx.author, bet.currency, win_amount, ctx.command.name.upper(), user_won)
        return await ctx.send(embed=embed)

    @utils.command(name="55x2")
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    @commands.guild_only()
    async def dice_55x2(self, ctx: utils.Context, *, bet: localutils.CurrencyAmount = None):
        """
        Place a bet on a dice roll - any number rolled that's higher than 55 will multiply your bet x2.
        """

        await self.roll_dice(ctx, 55, 2, bet or localutils.CurrencyAmount())

    @utils.command(name="75x3")
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    @commands.guild_only()
    async def dice_75x3(self, ctx: utils.Context, *, bet: localutils.CurrencyAmount = None):
        """
        Place a bet on a dice roll - any number rolled that's higher than 75 will multiply your bet x3.
        """

        await self.roll_dice(ctx, 75, 3, bet or localutils.CurrencyAmount())

    @utils.command(name="95x5")
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    @commands.guild_only()
    async def dice_95x5(self, ctx: utils.Context, *, bet: localutils.CurrencyAmount = None):
        """
        Place a bet on a dice roll - any number rolled that's higher than 95 will multiply your bet x5.
        """

        await self.roll_dice(ctx, 95, 5, bet or localutils.CurrencyAmount())


def setup(bot: utils.Bot):
    x = DiceCommands(bot)
    bot.add_cog(x)
