import random
from typing import Optional, Union

import discord
from discord.ext import commands, vbu

from cogs import utils


class DiceCommands(utils.GamblingCog):

    async def roll_dice(
            self,
            ctx: vbu.SlashContext,
            reason: str,
            dice_limit: int,
            multiplier: int,
            bet: utils.BetAmount) -> None:
        """
        Roll the dice on the user's bet.

        Parameters
        ----------
        ctx : vbu.Context
            The context for the interaction.
        dice_limit : int
            The number that the user bet on.
        multiplier : int
            The multiplier if the user should win.
        bet : utils.BetAmount
            The user's bet amount.
        """

        # Work out what the user's rolled
        rolled_number = random.randint(1, 100)
        user_won = rolled_number > dice_limit

        # Work out what to say to the user
        embed = vbu.Embed(title=f"\N{GAME DIE} {rolled_number}")
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
        self.bot.dispatch(
            "transaction",
            ctx.author,
            bet.currency,
            win_amount,
            f"GAME {reason}",  # type: ignore
            user_won,
        )
        await ctx.send(embed=embed)

    @commands.group(
        application_command_meta=commands.ApplicationCommandMeta(
            guild_only=True,
        ),
    )
    async def dice(self, _: vbu.SlashContext):
        ...

    @dice.command(
        name="55x2",
        application_command_meta=commands.ApplicationCommandMeta(
            options=[
                discord.ApplicationCommandOption(
                    name="bet",
                    type=discord.ApplicationCommandOptionType.integer,
                    description="The amount that you want to bet.",
                    min_value=0,
                ),
                discord.ApplicationCommandOption(
                    name="currency",
                    type=discord.ApplicationCommandOptionType.string,
                    description="The currency that you want to bet in.",
                ),
            ],
            guild_only=True,
        ),
    )
    @commands.defer()
    async def dice_55x2(
            self,
            ctx: vbu.SlashContext,
            bet: int,
            currency: str):
        """
        Place a bet on a dice roll - any number rolled that's higher than 55 will multiply your bet x2.
        """

        ba = utils.BetAmount(bet, currency)
        await ba.validate(ctx)
        await self.roll_dice(ctx, "55x2", 55, 2, ba)

    @dice.command(
        name="75x3",
        application_command_meta=commands.ApplicationCommandMeta(
            options=[
                discord.ApplicationCommandOption(
                    name="bet",
                    type=discord.ApplicationCommandOptionType.integer,
                    description="The amount that you want to bet.",
                    min_value=0,
                ),
                discord.ApplicationCommandOption(
                    name="currency",
                    type=discord.ApplicationCommandOptionType.string,
                    description="The currency that you want to bet in.",
                ),
            ],
            guild_only=True,
        ),
    )
    @commands.defer()
    async def dice_75x3(
            self,
            ctx: vbu.SlashContext,
            bet: int,
            currency: str):
        """
        Place a bet on a dice roll - any number rolled that's higher than 75 will multiply your bet x3.
        """

        ba = utils.BetAmount(bet, currency)
        await ba.validate(ctx)
        await self.roll_dice(ctx, "75x3", 75, 3, ba)

    @dice.command(
        name="95x5",
        application_command_meta=commands.ApplicationCommandMeta(
            options=[
                discord.ApplicationCommandOption(
                    name="bet",
                    type=discord.ApplicationCommandOptionType.integer,
                    description="The amount that you want to bet.",
                    min_value=0,
                ),
                discord.ApplicationCommandOption(
                    name="currency",
                    type=discord.ApplicationCommandOptionType.string,
                    description="The currency that you want to bet in.",
                ),
            ],
            guild_only=True,
        ),
    )
    @commands.defer()
    async def dice_95x5(
            self,
            ctx: vbu.SlashContext,
            bet: int,
            currency: str):
        """
        Place a bet on a dice roll - any number rolled that's higher than 95 will multiply your bet x5.
        """

        ba = utils.BetAmount(bet, currency)
        await ba.validate(ctx)
        await self.roll_dice(ctx, "95x5", 95, 5, ba)


def setup(bot: vbu.Bot):
    x = DiceCommands(bot)
    bot.add_cog(x)
