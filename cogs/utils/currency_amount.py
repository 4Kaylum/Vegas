from typing import Optional

import discord
from discord.ext import commands, vbu


class CurrencyAmount(object):

    SLASH_COMMAND_ARG_TYPE = discord.ApplicationCommandOptionType.string

    def __init__(self, amount: int = 0, currency: Optional[str] = None):
        self.amount = amount
        self.currency = currency

    @classmethod
    async def convert(cls, ctx: commands.Context, value: str):
        """
        Grab the amount of money that the user wants to bet.
        """

        # Work out if they gave an amount and a currency
        try:
            amount_str, currency_str = value.split(" ", 1)
        except ValueError:
            amount_str, currency_str = value, None
        amount = await vbu.converters.NumberConverter.convert(ctx, amount_str)
        if amount == 0:
            return cls(0, None)

        # Work out which currency they want to bet
        async with ctx.bot.database() as db:
            if currency_str:
                rows = await db(
                    "SELECT * FROM guild_currencies WHERE guild_id=$1 AND (currency_name=$2 OR short_form=$2)",
                    ctx.guild.id, currency_str,
                )
                try:
                    row = rows[0]
                except KeyError:
                    raise commands.BadArgument("The currency you gave isn't available on this guild.")
            else:
                rows = await db(
                    "SELECT * FROM guild_currencies WHERE guild_id=$1",
                    ctx.guild.id,
                )
                if len(rows) > 1:
                    raise commands.BadArgument(
                        "There are multiple currencies on this guild - you need to specify which you're using.",
                    )
                elif not rows:
                    raise commands.BadArgument(
                        "There aren't any currencies set up on this guild - you can't bet if there isn't any money available.",
                    )
                row = rows[0]

        # And return an object
        return cls(amount, row['currency_name'])


class BetAmount(CurrencyAmount):

    @classmethod
    async def convert(cls, ctx, value):
        """
        Grab the amount of money that the user wants to bet.
        """

        new = await super().convert(ctx, value)
        if new.amount <= 0 or new.currency is None:
            return new
        async with ctx.bot.database() as db:
            rows = await db(
                """SELECT * FROM user_money WHERE user_id=$1 AND guild_id=$2 AND currency_name=$3""",
                ctx.author.id, ctx.guild.id, new.currency,
            )
        if not rows or rows[0]['money_amount'] < new.amount:
            raise commands.BadArgument("You don't have enough money to make that bet.")
        return new
