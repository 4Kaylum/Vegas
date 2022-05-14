import asyncio
import random
from datetime import datetime as dt, timedelta
from typing import Optional

import discord
from discord.ext import commands, vbu

from cogs import utils


class CurrencyCommands(vbu.Cog):

    MAX_GUILD_CURRENCIES = 3
    DAILY_COMMAND_TIMEOUT = timedelta(days=1)

    @commands.command(
        aliases=["pay", "give"],
        application_command_meta=commands.ApplicationCommandMeta(
            options=[
                discord.ApplicationCommandOption(
                    name="user",
                    type=discord.ApplicationCommandOptionType.user,
                    description="The user you want to transfer money to.",
                ),
                discord.ApplicationCommandOption(
                    name="amount",
                    type=discord.ApplicationCommandOptionType.string,
                    description="The amount that you want to transfer.",
                ),
            ],
            guild_only=True,
        ),
    )
    @commands.guild_only()
    async def transfer(self, ctx: vbu.Context, user: discord.Member, amount: utils.BetAmount):
        """
        Transfers money from the author's account to another user's account.
        """

        async with self.bot.database() as db:
            await db.start_transaction()
            await db(
                """INSERT INTO user_money (user_id, guild_id, currency_name, money_amount) VALUES ($1, $2, $3, $4)
                ON CONFLICT (user_id, guild_id, currency_name) DO UPDATE SET
                money_amount=user_money.money_amount+excluded.money_amount""",
                user.id, ctx.guild.id, amount.currency, amount.amount,
            )
            await db(
                """INSERT INTO user_money (user_id, guild_id, currency_name, money_amount) VALUES ($1, $2, $3, $4)
                ON CONFLICT (user_id, guild_id, currency_name) DO UPDATE SET
                money_amount=user_money.money_amount+excluded.money_amount""",
                ctx.author.id, ctx.guild.id, amount.currency, -amount.amount,
            )
            await db.commit_transaction()
        await ctx.okay()

    @commands.command(
        aliases=['bal', 'coins'],
        application_command_meta=commands.ApplicationCommandMeta(
            options=[
                discord.ApplicationCommandOption(
                    name="user",
                    type=discord.ApplicationCommandOptionType.user,
                    description="The user you want to check the balance of.",
                    required=False,
                ),
            ],
            guild_only=True,
        ),
    )
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    @commands.guild_only()
    async def balance(self, ctx: vbu.Context, user: Optional[discord.Member] = None):
        """
        Shows you how many coins you have.
        """

        user = user or ctx.author  # type: ignore
        async with self.bot.database() as db:
            rows = await db(
                """SELECT guild_currencies.currency_name, um.money_amount FROM guild_currencies LEFT OUTER JOIN
                (SELECT * FROM user_money WHERE user_money.guild_id=$1 AND user_money.user_id=$2) AS um ON
                guild_currencies.currency_name=um.currency_name WHERE guild_currencies.guild_id=$1""",
                ctx.guild.id, user.id,
            )
        embed = vbu.Embed(use_random_colour=True)
        for row in rows:
            name = row['currency_name']
            currency_name = name.title() if name.lower() == name else name
            embed.add_field(currency_name, format(row['money_amount'] or 0, ","))
        await ctx.send(embed=embed)

    # @commands.group(aliases=['currencies'], invoke_without_command=False)
    # @commands.bot_has_permissions(send_messages=True, embed_links=True)
    # @commands.guild_only()
    # async def currency(self, ctx: vbu.Context):
    #     """
    #     The parent command to set up the currencies on your guild.
    #     """

    #     if ctx.invoked_subcommand is not None:
    #         return
    #     async with self.bot.database() as db:
    #         currency_rows = await db(
    #             """SELECT * FROM guild_currencies WHERE guild_id=$1 ORDER BY UPPER(currency_name) ASC""",
    #             ctx.guild.id,
    #         )
    #     if not currency_rows:
    #         return await ctx.send(f"There are no currencies set up for this guild! Use the `{ctx.clean_prefix}currency create` command to add a new one.")
    #     embed = vbu.Embed(colour=0x1)
    #     embed.set_footer(f"Add new currencies with \"{ctx.clean_prefix}currency create\"")
    #     currencies = []
    #     for row in currency_rows:
    #         name = row['currency_name']
    #         currency_name = name.title() if name.lower() == name else name
    #         currencies.append(f"* {currency_name}")
    #     embed.description = "\n".join(currencies)
    #     return await ctx.send(embed=embed)

    # @currency.command(name="create", aliases=['make', 'new'])
    # @commands.has_guild_permissions(manage_guild=True)
    # @commands.bot_has_permissions(send_messages=True, add_reactions=True)
    # @commands.guild_only()
    # async def currency_create(self, ctx: vbu.Context):
    #     """
    #     Add a new currency to your guild.
    #     """

    #     # Make sure they only have 3 currencies already
    #     async with self.bot.database() as db:
    #         currency_rows = await db("""SELECT * FROM guild_currencies WHERE guild_id=$1""", ctx.guild.id)
    #     if len(currency_rows) >= self.MAX_GUILD_CURRENCIES:
    #         return await ctx.send(f"You can only have **{self.MAX_GUILD_CURRENCIES}** currencies per guild.")
    #     boolean_emojis = ["\N{HEAVY CHECK MARK}", "\N{HEAVY MULTIPLICATION X}"]

    #     # Set up the wait_for check here because we're gonna use it multiple times
    #     def check(message):
    #         return all([
    #             message.channel.id == ctx.channel.id,
    #             message.author.id == ctx.author.id,
    #         ])

    #     def reaction_check(message):
    #         def wrapper(payload):
    #             return all([
    #                 payload.message_id == message.id,
    #                 payload.user_id == ctx.author.id,
    #                 str(payload.emoji) in boolean_emojis,
    #             ])
    #         return wrapper

    #     # Ask what they want the name of the currency to be
    #     await ctx.send("""What do you want the _name_ of the currency to be? Examples: "dollars", "pounds", "krona", etc.""")
    #     for _ in range(3):
    #         currency_name_message = None
    #         try:
    #             currency_name_message = await self.bot.wait_for("message", check=check, timeout=60)
    #             assert currency_name_message.content
    #         except asyncio.TimeoutError:
    #             return await ctx.send("Timed out on adding a new currency to the guild.")
    #         except AssertionError:
    #             await currency_name_message.reply("This isn't a valid currency name - please provide another one.")
    #             continue

    #         # Check that their provided name is valid
    #         async with self.bot.database() as db:
    #             check_rows = await db(
    #                 """SELECT * FROM guild_currencies WHERE guild_id=$1 AND LOWER(currency_name)=LOWER($2)""",
    #                 ctx.guild.id, currency_name_message.content,
    #             )
    #         if check_rows:
    #             await currency_name_message.reply(
    #                 f"You're already using a currency with the name **{currency_name_message.content}** - please provide another one.",
    #                 allowed_mentions=discord.AllowedMentions.none(),
    #             )
    #             continue
    #         break
    #     else:
    #         return await ctx.send("You failed giving a valid currency name too many times - please try again later.")

    #     # Ask what they want the short form of the currency to be
    #     await ctx.send("""What do you want the _short form_ of the currency to be? Examples: "USD", "GBP", "RS3", etc.""")
    #     for _ in range(3):
    #         try:
    #             currency_short_message = await self.bot.wait_for("message", check=check, timeout=60)
    #             assert currency_short_message.content
    #             break
    #         except asyncio.TimeoutError:
    #             return await ctx.send("Timed out on adding a new currency to the guild.")
    #         except AssertionError:
    #             await currency_short_message.reply("This isn't a valid currency name - please provide another one.")

    #         # Check that their provided name is valid
    #         async with self.bot.database() as db:
    #             check_rows = await db(
    #                 """SELECT * FROM guild_currencies WHERE guild_id=$1 AND LOWER(short_form)=LOWER($2)""",
    #                 ctx.guild.id, currency_short_message.content,
    #             )
    #         if check_rows:
    #             await currency_name_message.reply(
    #                 f"You're already using a currency with the short name **{currency_name_message.content}** - please provide another one.",
    #                 allowed_mentions=discord.AllowedMentions.none(),
    #             )
    #             continue
    #         break
    #     else:
    #         return await ctx.send("You failed giving a valid currency short name too many times - please try again later.")

    #     # Ask if we should add a daily command
    #     m = await ctx.send("""Do you want there to be a "daily" command available for this currency, where users can get between 9k and 13k every day?""")
    #     for e in boolean_emojis:
    #         self.bot.loop.create_task(m.add_reaction(e))
    #     try:
    #         currency_daily_payload = await self.bot.wait_for("raw_reaction_add", check=reaction_check(m), timeout=60)
    #     except asyncio.TimeoutError:
    #         return await ctx.send("Timed out on adding a new currency to the guild.")

    #     # Add the new currency to the server
    #     async with ctx.typing():
    #         async with self.bot.database() as db:
    #             await db(
    #                 """INSERT INTO guild_currencies (guild_id, currency_name, short_form, allow_daily_command)
    #                 VALUES ($1, $2, $3, $4)""",
    #                 ctx.guild.id, currency_name_message.content, currency_short_message.content,
    #                 str(currency_daily_payload.emoji) == "\N{HEAVY CHECK MARK}",
    #             )
    #     return await ctx.send("Added a new currency to your server!")

    # @currency.command(name="add")
    # @commands.has_guild_permissions(manage_guild=True)
    # @commands.bot_has_permissions(add_reactions=True)
    # @commands.guild_only()
    # async def currency_add(self, ctx: vbu.Context, user: discord.Member, *, amount: utils.CurrencyAmount):
    #     """
    #     Give some currency to a user.
    #     """

    #     async with self.bot.database() as db:
    #         await db(
    #             """INSERT INTO user_money (user_id, guild_id, currency_name, money_amount) VALUES ($1, $2, $3, $4)
    #             ON CONFLICT (user_id, guild_id, currency_name) DO UPDATE SET
    #             money_amount=user_money.money_amount+excluded.money_amount""",
    #             user.id, ctx.guild.id, amount.currency, amount.amount,
    #         )
    #     self.bot.dispatch("transaction", user, amount.currency, amount.amount, "MODERATOR_INTERVENTION")
    #     await ctx.okay()

    # @currency.command(name="remove")
    # @commands.has_guild_permissions(manage_guild=True)
    # @commands.bot_has_permissions(add_reactions=True)
    # @commands.guild_only()
    # async def currency_remove(self, ctx: vbu.Context, user: discord.Member, *, amount: utils.CurrencyAmount):
    #     """
    #     Remove some currency from a user.
    #     """

    #     async with self.bot.database() as db:
    #         await db(
    #             """INSERT INTO user_money (user_id, guild_id, currency_name, money_amount) VALUES ($1, $2, $3, $4)
    #             ON CONFLICT (user_id, guild_id, currency_name) DO UPDATE SET
    #             money_amount=user_money.money_amount+excluded.money_amount""",
    #             user.id, ctx.guild.id, amount.currency, -amount.amount,
    #         )
    #     self.bot.dispatch("transaction", user, amount.currency, -amount.amount, "MODERATOR_INTERVENTION")
    #     await ctx.okay()

    @commands.command()
    async def daily(self, ctx: vbu.Context):
        """
        Get money on the daily.
        """

        async with self.bot.database() as db:

            # See which currencies allow faily command
            all_guild_currencies = await db(
                """SELECT currency_name FROM guild_currencies WHERE guild_id=$1 AND allow_daily_command=true""",
                ctx.guild.id,
            )

            # Check out last run commands
            allowed_daily_currencies = await db(
                """SELECT currency_name, last_daily_command FROM user_money WHERE user_money.guild_id=$1 AND
                user_money.user_id=$2 AND currency_name=ANY($3::TEXT[])""",
                ctx.guild.id, ctx.author.id, [i['currency_name'] for i in all_guild_currencies],
            )

            # Work out when each thing was last run
            allowed_daily_dict = {}
            for row in all_guild_currencies:
                allowed_daily_dict[row['currency_name']] = dt(2000, 1, 1)
            for row in allowed_daily_currencies:
                allowed_daily_dict[row['currency_name']] = row['last_daily_command']
            if not allowed_daily_dict:
                return await ctx.send("There's nothing available for use with the daily command right now.")

            # Work out how much we're adding
            changed_daily = {}
            for currency_name, last_run_time in allowed_daily_dict.items():
                if last_run_time > dt.utcnow() - self.DAILY_COMMAND_TIMEOUT:
                    continue
                amount = random.randint(9_000, 13_000)
                await db(
                    """INSERT INTO user_money (user_id, guild_id, currency_name, money_amount, last_daily_command)
                    VALUES ($1, $2, $3, $4, $5) ON CONFLICT (user_id, guild_id, currency_name) DO UPDATE SET
                    money_amount=user_money.money_amount+excluded.money_amount, last_daily_command=excluded.last_daily_command""",
                    ctx.author.id, ctx.guild.id, currency_name, amount, ctx.message.created_at,
                )
                self.bot.dispatch("transaction", ctx.author, currency_name, amount, "DAILY_COMMAND")
                changed_daily[row['currency_name']] = amount

        # Make them into an embed
        if not changed_daily:
            soonest_allow_daily = max(allowed_daily_dict.values())
            soonest_tv = vbu.TimeValue((soonest_allow_daily - (dt.utcnow() - self.DAILY_COMMAND_TIMEOUT)).total_seconds())
            return await ctx.send(f"You can't get anything with the daily command for another **{soonest_tv.clean_full}**.")
        embed = vbu.Embed(use_random_colour=True)
        description_list = []
        for currency, amount in changed_daily.items():
            currency_name = currency.title() if currency.lower() == currency else currency
            description_list.append(f"**{currency_name}** - {amount}")
        embed.description = "\n".join(description_list)
        return await ctx.send(embed=embed)


def setup(bot: vbu.Bot):
    x = CurrencyCommands(bot)
    bot.add_cog(x)
