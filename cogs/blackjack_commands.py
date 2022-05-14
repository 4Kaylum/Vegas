import asyncio

import discord
from discord.ext import commands, vbu

from cogs import utils


class BlackjackCommands(utils.GamblingCog):

    @commands.command(
        aliases=['bj'],
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
                    autocomplete=True,
                ),
            ],
            guild_only=True,
        ),
    )
    @commands.defer()
    async def blackjack(
            self,
            ctx: vbu.SlashContext,
            bet: int,
            currency: str):
        """
        Lets you play a blackjack game against the bot.
        """

        # Fix the bet amount into an object
        ba = utils.BetAmount(bet, currency)
        await ba.validate(ctx)

        # Create the deck and hands used for the game
        deck: utils.Deck = utils.Deck.create_deck(shuffle=True)
        dealer_hand: utils.Hand = utils.Hand(deck)
        dealer_hand.draw(2)
        user_hand: utils.Hand = utils.Hand(deck)
        user_hand.draw(2)

        # Make some components
        components = discord.ui.MessageComponents(
            discord.ui.ActionRow(
                discord.ui.Button(label="HIT", custom_id="HIT"),
                discord.ui.Button(label="STAND", custom_id="STAND"),
            ),
        )

        # Ask the user if they want to hit or stand
        message = None
        while True:

            # See if the user went bust
            if min(user_hand.get_values()) > 21:
                embed = vbu.Embed(colour=discord.Colour.red())
                embed.add_field("Dealer Hand", f"{dealer_hand.display(show_cards=1)} (??)", inline=True)
                embed.add_field("Your Hand", f"{user_hand.display()} ({user_hand.get_values()[-1]} - bust)", inline=True)
                if ba.amount:
                    embed.add_field("Result", f"You lost, removed **{ba.amount:,}** from your account :c", inline=False)
                else:
                    embed.add_field("Result", "You lost :c", inline=False)
                self.bot.dispatch("transaction", ctx.author, ba.currency, -ba.amount, "GAME blackjack", False)
                assert message
                return await message.edit(embed=embed, components=components.disable_components())
            if max(user_hand.get_values(max_value=21)) == 21:
                break

            # Output the hands to be used
            embed = vbu.Embed(colour=0xfffffe)
            embed.add_field("Dealer Hand", f"{dealer_hand.display(show_cards=1)} (??)", inline=True)
            embed.add_field("Your Hand", f"{user_hand.display()} ({', '.join(user_hand.get_values(cast=str, max_value=21))})", inline=True)
            if message is None:
                message = await ctx.send(embed=embed, components=components)
            else:
                await message.edit(embed=embed)

            # See what the user wants to do
            def check(interaction):
                return all([
                    interaction.message.id == message.id,
                    interaction.user.id == ctx.author.id,
                ])
            try:
                interaction = await self.bot.wait_for("component_interaction", check=check, timeout=120)
                await interaction.response.defer_update()
            except asyncio.TimeoutError:
                return await ctx.send("Timed out waiting for your response.")

            # See if they want to stand
            if interaction.custom_id == "STAND":
                break

            # See if they want to hit
            user_hand.draw()
            await asyncio.sleep(0.2)

        # Let's draw until we get higher than the user
        user_max_value = max(user_hand.get_values(max_value=21))
        user_has_won = None
        max_dealer_value = 0
        while True:
            try:
                max_dealer_value = max(dealer_hand.get_values(max_value=21))
                if max_dealer_value >= user_max_value:
                    user_has_won = False  # Dealer wins
                    break
            except ValueError:
                user_has_won = True  # Dealer went bust
                break
            dealer_hand.draw()

        # Make sure we got a value and I didn't mess anything up
        if user_has_won is None:
            raise Exception("Failed to run the command properly.")

        # Don't error if the user got a blackjack
        if message:
            send_method = message.edit
            components = components.disable_components()
        else:
            send_method = ctx.send
            components = None

        # Output something for the user winning
        if user_has_won:
            embed = vbu.Embed(colour=discord.Colour.green())
            if min(dealer_hand.get_values()) > 21:
                embed.add_field("Dealer Hand", f"{dealer_hand.display()} ({dealer_hand.get_values()[-1]} - bust)", inline=True)
            else:
                embed.add_field("Dealer Hand", f"{dealer_hand.display()} ({dealer_hand.get_values()[0]})", inline=True)
            embed.add_field("Your Hand", f"{user_hand.display()} ({user_hand.get_values(max_value=21)[0]})", inline=True)
            if ba.amount:
                embed.add_field("Result", f"You won! Added **{ba.amount:,}** to your account! :D", inline=False)
            else:
                embed.add_field("Result", "You won! :D", inline=False)
            self.bot.dispatch("transaction", ctx.author, ba.currency, ba.amount, "GAME blackjack", True)
            return await send_method(embed=embed, components=components)  # type: ignore

        # Output something for the dealer winning
        embed = vbu.Embed(colour=discord.Colour.red())
        embed.add_field("Dealer Hand", f"{dealer_hand.display()} ({dealer_hand.get_values(max_value=21)[0]})", inline=True)
        embed.add_field("Your Hand", f"{user_hand.display()} ({user_hand.get_values(max_value=21)[0]})", inline=True)
        if max_dealer_value > user_max_value:
            if ba.amount:
                embed.add_field("Result", f"You lost, removed **{ba.amount:,}** from your account :c", inline=False)
            else:
                embed.add_field("Result", "You lost :c", inline=False)
        else:
            if ba.amount:
                embed.add_field("Result", f"You tied, returned **{ba.amount:,}** to your account :<", inline=False)
            else:
                embed.add_field("Result", "You tied :<", inline=False)
        if max_dealer_value > user_max_value:
            self.bot.dispatch("transaction", ctx.author, ba.currency, -ba.amount, "GAME blackjack", False)
        else:
            self.bot.dispatch("transaction", ctx.author, ba.currency, 0, "GAME blackjack", False)
        return await send_method(embed=embed, components=components)  # type: ignore

    blackjack.autocomplete(utils.autocomplete.currency_name_autocomplete)


def setup(bot: vbu.Bot):
    x = BlackjackCommands(bot)
    bot.add_cog(x)
