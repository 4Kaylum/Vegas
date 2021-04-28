from discord.ext import commands
import voxelbotutils as utils

from cogs import utils as localutils


class BaccuratDeck(localutils.Deck):

    @classmethod
    def create_deck(cls, *args, **kwargs):
        """
        Like a normal deck but the values of 10, Jack, Queen, and King are all 0.
        """

        created = super().create_deck(*args, **kwargs)
        for card in created._cards:
            if card._value == 1:
                card._value_override = [1]
            elif card._value in [10, 11, 12, 13]:
                card._value_override = [0]
        return created


class BaccuratHand(localutils.Hand):

    def get_values(self, *args, **kwargs):
        """
        Like a normal get_values but it cuts off the tens units.
        """

        values = super().get_values(*args, **kwargs)
        return list(set([i % 10 for i in values]))[0]


class BaccuratCommands(localutils.GamblingCog):

    @utils.command()
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    @commands.guild_only()
    async def baccurat(self, ctx: utils.Context, bet_location: str, *, bet: localutils.BetAmount = None):
        """
        Plays you a game of baccurat.
        """

        """
        If either the player or banker is dealt a total of eight or nine, both the player and banker stand.
        If the player's total is five or less, then the player will receive another card. Otherwise, the player will stand.
        If the player stands, then the banker hits on a total of 5 or less.
        The final betting option, a tie, pays out 8-to-1.
        """

        # Make sure they set a valid bet location
        bet_location = bet_location.lower()[0]
        if bet_location not in ["player", "dealer", "tie", "p", "d", "t"]:
            return await ctx.send('Your bet location needs to be one of "player", "dealer", and "tie".')

        # Create the deck and hands used for the game
        deck: BaccuratDeck = BaccuratDeck.create_deck(shuffle=True)
        dealer_hand: BaccuratHand = BaccuratHand(deck)
        dealer_hand.draw(2)
        user_hand: BaccuratHand = BaccuratHand(deck)
        user_hand.draw(2)
        bet = bet or localutils.CurrencyAmount()

        # Play the game
        while True:
            if dealer_hand.get_values() in [8, 9] or user_hand.get_values() in [8, 9]:
                break
            if user_hand.get_values() <= 5:
                user_hand.draw()
            else:
                if dealer_hand.get_values() <= 5:
                    dealer_hand.draw()
                else:
                    break

        # Make the initial embed
        embed = utils.Embed()
        embed.add_field("Dealer Hand", f"{dealer_hand.display()} ({dealer_hand.get_values()[0]})", inline=True)
        embed.add_field("Your Hand", f"{user_hand.display()} ({user_hand.get_values()[0]})", inline=True)

        # See if they tied
        if dealer_hand.get_values() == user_hand.get_values():
            if bet_location == "t":
                self.bot.dispatch("transaction", ctx.author, bet.currency, bet.amount * 8, "BACCURAT", True)
                embed.colour = discord.Colour.green()
                if bet.amount:
                    embed.add_field("Result", f"You tied! Added **{bet.amount * 8:,}** to your account! :D", inline=False)
                else:
                    embed.add_field("Result", "You tied!", inline=False)
                return await ctx.reply(embed=embed)
            else:
                self.bot.dispatch("transaction", ctx.author, bet.currency, -bet.amount, "BACCURAT", False)
                embed.colour = discord.Colour.red()
                if bet.amount:
                    embed.add_field("Result", f"You tied, removed **{bet.amount:,}** from your account! :c", inline=False)
                else:
                    embed.add_field("Result", "You tied :c", inline=False)
                return await ctx.reply(embed=embed)

        # See if the dealer won
        if dealer_hand.get_values() > user_hand.get_values():
            if bet_location == "d":
                self.bot.dispatch("transaction", ctx.author, bet.currency, bet.amount, "BACCURAT", True)
                embed.colour = discord.Colour.green()
                if bet.amount:
                    embed.add_field("Result", f"The dealer won! Added **{bet.amount:,}** to your account! :D", inline=False)
                else:
                    embed.add_field("Result", "The dealer won!", inline=False)
                return await ctx.reply(embed=embed)
            else:
                self.bot.dispatch("transaction", ctx.author, bet.currency, -bet.amount, "BACCURAT", False)
                embed.colour = discord.Colour.red()
                if bet.amount:
                    embed.add_field("Result", f"The dealer won, removed **{bet.amount:,}** from your account! :c", inline=False)
                else:
                    embed.add_field("Result", "The dealer won :c", inline=False)
                return await ctx.reply(embed=embed)

        # See if the player won
        if dealer_hand.get_values() < user_hand.get_values():
            if bet_location == "p":
                self.bot.dispatch("transaction", ctx.author, bet.currency, bet.amount, "BACCURAT", True)
                embed.colour = discord.Colour.green()
                if bet.amount:
                    embed.add_field("Result", f"You won! Added **{bet.amount:,}** to your account! :D", inline=False)
                else:
                    embed.add_field("Result", "You won!", inline=False)
                return await ctx.reply(embed=embed)
            else:
                self.bot.dispatch("transaction", ctx.author, bet.currency, -bet.amount, "BACCURAT", False)
                embed.colour = discord.Colour.red()
                if bet.amount:
                    embed.add_field("Result", f"You won, removed **{bet.amount:,}** from your account! :c", inline=False)
                else:
                    embed.add_field("Result", "You won :c", inline=False)
                return await ctx.reply(embed=embed)
