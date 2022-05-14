import asyncio
import random
from datetime import datetime as dt, timedelta
from typing import List, Optional

import discord
from discord.ext import commands, vbu

from cogs import utils


class CurrencyCommands(vbu.Cog[vbu.Bot]):

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
    async def transfer(
            self,
            ctx: vbu.SlashContext,
            user: discord.Member,
            bet: int,
            currency: str):
        """
        Transfers money from the author's account to another user's account.
        """

        # Make sure the user and the author are different
        if ctx.author == user:
            return await ctx.interaction.followup.send("You can't transfer money to yourself.")

        # Make sure they have enough money
        ba = utils.BetAmount(bet, currency)
        await ba.validate(ctx)

        # Transfer
        self.bot.dispatch(
            "transaction",
            ctx.author,
            ba.currency,
            -ba.amount,
            f"TRANSFER TO {user.id}",
        )
        self.bot.dispatch(
            "transaction",
            user,
            ba.currency,
            ba.amount,
            f"TRANSFER FROM {ctx.interaction.user.id}",
        )

        # And done
        return await ctx.interaction.followup.send("Money transferred :)")

        # todo add confirm button

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
    @commands.defer()
    async def balance(self, ctx: vbu.SlashContext, user: Optional[discord.Member] = None):
        """
        Shows you how many coins you have.
        """

        # Get our data
        user = user or ctx.author  # type: ignore
        assert user
        async with vbu.Database() as db:
            rows = await db.call(
                """SELECT SUM(amount_transferred), currency_name FROM transactions
                WHERE guild_id=$1 AND user_id=$2 GROUP BY currency_name""",
                ctx.guild.id, user.id,
            )
            all_currencies = await db.call(
                """SELECT currency_name FROM guild_currencies WHERE guild_id=$1""",
                ctx.guild.id,
            )

        # Format into an embed
        embed = vbu.Embed(use_random_colour=True)
        added_currencies = set()
        for row in rows:
            name = row['currency_name']
            added_currencies.add(name)
            currency_name = name.title() if name.lower() == name else name
            embed.add_field(
                name=currency_name,
                value=format(int(row['sum'] or 0), ","),
            )
        for row in all_currencies:
            name = row['currency_name']
            if name in added_currencies:
                continue
            currency_name = name.title() if name.lower() == name else name
            embed.add_field(
                name=currency_name,
                value=format(0, ","),
            )

        # Default case
        if not all_currencies:
            embed.description = "This guild has no currencies created."

        # And send
        await ctx.interaction.followup.send(embed=embed)

    @commands.group(
        aliases=['currencies'],
        invoke_without_command=False,
        application_command_meta=commands.ApplicationCommandMeta(
            guild_only=True,
        ),
    )
    async def currency(self, _: vbu.Context):
        """
        The parent command to set up the currencies on your guild.
        """

        ...

    @currency.command(
        name="create",
        aliases=['make', 'new'],
        application_command_meta=commands.ApplicationCommandMeta(
            options=[
                discord.ApplicationCommandOption(
                    name="name",
                    type=discord.ApplicationCommandOptionType.string,
                    description="The name of the currency that you want to add.",
                ),
                discord.ApplicationCommandOption(
                    name="short_form",
                    type=discord.ApplicationCommandOptionType.string,
                    description="The short form of the currency's name (eg USD, GBP, RS3, etc).",
                ),
                discord.ApplicationCommandOption(
                    name="daily_command",
                    type=discord.ApplicationCommandOptionType.boolean,
                    description="Whether or not you want to add a daily command.",
                ),
            ],
            guild_only=True,
        ),
    )
    @commands.defer()
    async def currency_create(
            self,
            ctx: vbu.SlashContext,
            name: str,
            short_form: str,
            daily_command: bool):
        """
        Add a new currency to your guild.
        """

        # Make sure they only have 3 currencies already
        async with vbu.Database() as db:
            currency_rows = await db(
                """SELECT * FROM guild_currencies WHERE guild_id=$1""",
                ctx.guild.id,
            )
        if len(currency_rows) >= self.MAX_GUILD_CURRENCIES:
            return await ctx.interaction.followup.send(f"You can only have **{self.MAX_GUILD_CURRENCIES}** currencies per guild.")

        # See if any of the names are in use
        for i in currency_rows:
            if i['name'].lower() == name.lower():
                return await ctx.interaction.followup.send(f"You're already using a command with that name.")
            if i['short_form'].lower() == short_form.lower():
                return await ctx.interaction.followup.send(f"You're already using a command with that short form.")

        # And save
        async with vbu.Database() as db:
            currency_rows = await db(
                """INSERT INTO guild_currencies (guild_id, currency_name, short_form, allow_daily_command)
                VALUES ($1, $2, $3, $4)""",
                ctx.guild.id, name, short_form, daily_command,
            )
        return await ctx.interaction.followup.send("Your currency has been created!")

    @commands.command(
        application_command_meta=commands.ApplicationCommandMeta()
    )
    @commands.defer()
    async def daily(self, ctx: vbu.SlashContext):
        """
        Get money on the daily.
        """

        # Open db connection
        async with vbu.Database() as db:

            # See what currencies we can daily
            all_valid_currencies = await db.call(
                """SELECT currency_name FROM guild_currencies WHERE guild_id=$1 AND allow_daily_command=true""",
                ctx.guild.id,
            )

            # See what currencies they called in the last day
            disallowed_currencies = await db.call(
                """SELECT currency_name FROM transactions WHERE guild_id=$1 AND
                user_id=$2 AND currency_name=ANY($3::TEXT[]) AND timestamp >
                (TIMEZONE('UTC', NOW()) - INTERVAL '1 day') AND reason='DAILY_COMMAND'""",
                ctx.guild.id, ctx.author.id, [i['currency_name'] for i in all_valid_currencies],
            )

        # Work out how much we're adding
        changed_daily_items = {}
        disallowed: List[str] = [r['currency_name'] for r in disallowed_currencies]
        for row in all_valid_currencies:
            if row['currency_name'] in disallowed:
                continue
            changed_daily_items[row['currency_name']] = random.randint(9_000, 13_000)

        # Add it to them
        for currency_name, amount in changed_daily_items.items():
            self.bot.dispatch("transaction", ctx.author, currency_name, amount, "DAILY_COMMAND")

        # If they can't run the command say when they next can
        if not changed_daily_items:
            last_run_daily = min([i['timestamp'] for i in disallowed_currencies])
            next_run_daily = last_run_daily + self.DAILY_COMMAND_TIMEOUT
            formatted = discord.utils.format_dt(next_run_daily, style='R')
            return await ctx.interaction.followup.send(f"You can't get anything with the daily command for another **{formatted}**.")

        # They ran the command
        embed = vbu.Embed(use_random_colour=True)
        description_list = []
        for currency, amount in changed_daily_items.items():
            currency_name = currency.title() if currency.lower() == currency else currency
            description_list.append(f"**{currency_name}** - {amount}")
        embed.description = "\n".join(description_list)
        return await ctx.interaction.followup.send(embed=embed)


def setup(bot: vbu.Bot):
    x = CurrencyCommands(bot)
    bot.add_cog(x)
