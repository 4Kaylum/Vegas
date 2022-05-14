from typing import Optional

import discord
from discord.ext import vbu


class TransactionHandler(vbu.Cog[vbu.Bot]):

    @vbu.Cog.listener()
    async def on_transaction(
            self,
            member: discord.Member,
            currency: str,
            amount: int,
            reason: str,
            win: Optional[bool] = None):
        """
        Adds a transaction log to the database.

        Parameters
        ----------
        member : discord.Member
            The member who performed the transaction
        currency : str
            The currency that they performed the transaction in.
        amount : int
            The amount of money that they are moving.
        reason : str
            The reason they are moving the money.
        win : Optional[bool]
            Whether or not they won the game that they are transacting for. Could be null in the case of a trade,
            a daily command, etc.
        """

        if amount and currency:
            async with vbu.Database() as db:
                await db(
                    """INSERT INTO transactions (user_id, guild_id, currency_name, amount_transferred, reason, win)
                    VALUES ($1, $2, $3, $4, $5, $6)""",
                    member.id, member.guild.id, currency, amount or None, reason, win,
                )


def setup(bot: vbu.Bot):
    x = TransactionHandler(bot)
    bot.add_cog(x)
