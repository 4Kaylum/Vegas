import discord
import voxelbotutils as utils


class TransactionHandler(utils.Cog):

    @utils.Cog.listener()
    async def on_transaction(self, member: discord.Member, currency: str, amount: int, reason: str, win: bool = None):
        """
        Adds a transaction log to the database.
        """

        async with self.bot.database() as db:
            await db(
                """INSERT INTO transactions (user_id, guild_id, currency_name, amount_transferred, reason, win)
                VALUES ($1, $2, $3, $4, $5, $6)""",
                member.id, member.guild.id, currency, amount or None, reason, win,
            )
            if amount and currency:
                await db(
                    """INSERT INTO user_money (user_id, guild_id, currency_name, money_amount) VALUES ($1, $2, $3, $4)
                    ON CONFLICT (user_id, guild_id, currency_name) DO UPDATE SET
                    money_amount=user_money.money_amount+excluded.money_amount""",
                    member.id, member.guild.id, currency, amount,
                )


def setup(bot: utils.Bot):
    x = TransactionHandler(bot)
    bot.add_cog(x)
