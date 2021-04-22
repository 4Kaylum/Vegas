import asyncio

import discord
from discord.ext import commands
import voxelbotutils as utils

from cogs import utils as localutils


class BlackjackCommands(utils.Cog):

    @utils.command(aliases=['bj'])
    @commands.bot_has_permissions(send_messages=True, embed_links=True, external_emojis=True, add_reactions=True)
    async def blackjack(self, ctx: utils.Context, bet_amount: int = 0):
        """
        Lets you play a blackjack game against the bot.
        """

        # Create the deck and hands used for the game
        deck: localutils.Deck = localutils.Deck.create_deck(shuffle=True)
        dealer_hand: localutils.Hand = localutils.Hand(deck)
        dealer_hand.draw(2)
        user_hand: localutils.Hand = localutils.Hand(deck)
        user_hand.draw(2)
        valid_emojis = ["\N{HEAVY PLUS SIGN}", "\N{HEAVY CHECK MARK}"]

        # Ask the user if they want to hit or stand
        message = None
        while True:

            # See if the user went bust
            if min(user_hand.get_values()) > 21:
                embed = utils.Embed(colour=discord.Colour.red())
                embed.add_field("Dealer Hand", f"{dealer_hand.display(show_cards=1)} (??)", inline=True)
                embed.add_field("Your Hand", f"{user_hand.display()} ({user_hand.get_values()[-1]} - bust)", inline=True)
                embed.add_field("Result", "You lost :c", inline=False)
                self.bot.loop.create_task(message.clear_reactions())
                return await message.edit(embed=embed)
            if max(user_hand.get_values(max_value=21)) == 21:
                break

            # Output the hands to be used
            embed = utils.Embed(colour=0xfffffe)
            embed.add_field("Dealer Hand", f"{dealer_hand.display(show_cards=1)} (??)", inline=True)
            embed.add_field("Your Hand", f"{user_hand.display()} ({', '.join(user_hand.get_values(cast=str, max_value=21))})", inline=True)
            embed.set_footer(f"{valid_emojis[0]} Hit | {valid_emojis[1]} Stand")
            if message is None:
                message = await ctx.reply(embed=embed)
                for e in valid_emojis:
                    await message.add_reaction(e)
            else:
                await message.edit(embed=embed)

            # See what the user wants to do
            def check(payload):
                return all([
                    payload.user_id == ctx.author.id,
                    payload.message_id == message.id,
                    str(payload.emoji) in valid_emojis,
                ])
            done, pending = await asyncio.wait(
                [
                    self.bot.wait_for("raw_reaction_add", check=check),
                    self.bot.wait_for("raw_reaction_remove", check=check),
                ],
                timeout=120,
                return_when=asyncio.FIRST_COMPLETED,
            )
            if not done:
                for i in pending:
                    i.cancel()
                return await ctx.reply("Timed out waiting for your response.", ignore_error=True)

            # See if they want to stand
            done = done.pop().result()
            changed_emoji = str(done.emoji)
            if changed_emoji == valid_emojis[1]:
                break

            # See if they want to hit
            user_hand.draw()
            await asyncio.sleep(0.2)

        # Let's draw until we get higher than the user
        user_max_value = max(user_hand.get_values(max_value=21))
        user_has_won = None
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
            self.bot.loop.create_task(message.clear_reactions())
        else:
            send_method = ctx.send

        # Output something for the user winning
        if user_has_won:
            embed = utils.Embed(colour=discord.Colour.green())
            if min(dealer_hand.get_values()) > 21:
                embed.add_field("Dealer Hand", f"{dealer_hand.display()} ({dealer_hand.get_values()[-1]} - bust)", inline=True)
            else:
                embed.add_field("Dealer Hand", f"{dealer_hand.display()} ({dealer_hand.get_values()[0]})", inline=True)
            embed.add_field("Your Hand", f"{user_hand.display()} ({user_hand.get_values(max_value=21)[0]})", inline=True)
            embed.add_field("Result", "You won! :D", inline=False)
            return await send_method(embed=embed)

        # Output something for the dealer winning
        embed = utils.Embed(colour=discord.Colour.red())
        embed.add_field("Dealer Hand", f"{dealer_hand.display()} ({dealer_hand.get_values(max_value=21)[0]})", inline=True)
        embed.add_field("Your Hand", f"{user_hand.display()} ({user_hand.get_values(max_value=21)[0]})", inline=True)
        embed.add_field("Result", "You lost :c", inline=False)
        return await send_method(embed=embed)


def setup(bot: utils.Bot):
    x = BlackjackCommands(bot)
    bot.add_cog(x)
