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
            Whether or not they won the game that they are transacting for. Could be null in the case of a trade.
        """

        async with vbu.Database() as db:
            await db(
                """INSERT INTO transactions (user_id, guild_id, currency_name, amount_transferred, reason, win)
                VALUES ($1, $2, $3, $4, $5, $6)""",
                member.id, member.guild.id, currency, amount or None, reason, win,
            )
            if amount and currency:
                await db.call(
                    """INSERT INTO user_money (user_id, guild_id, currency_name, money_amount) VALUES ($1, $2, $3, $4)
                    ON CONFLICT (user_id, guild_id, currency_name) DO UPDATE SET
                    money_amount=user_money.money_amount+excluded.money_amount""",
                    member.id, member.guild.id, currency, amount,
                )


def setup(bot: vbu.Bot):
    x = TransactionHandler(bot)
    bot.add_cog(x)
