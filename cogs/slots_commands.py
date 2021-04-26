import random

from discord.ext import commands
import voxelbotutils as utils

from cogs import utils as localutils


class SlotsCommands(utils.Cog):

    SLOT_EMOJIS = {
        "LEMON": "\N{LEMON}",
        "CHERRY": "\N{CHERRIES}",
        "ORANGE": "\U0001f7e0",  # Orange circle emoji
        "PLUM": "\U0001f7e3",  # Purple circle emoji
        "BELL": "\N{BELL}",
        "BAR": "\N{CHOCOLATE BAR}",
    }  # Set up the emojis to use for the slots

    SLOT_SCORES = {
        ((SLOT_EMOJIS["LEMON"], 3,),): 60,
        ((SLOT_EMOJIS["CHERRY"], 3,),): 60,
        ((SLOT_EMOJIS["ORANGE"], 3,),): 60,
        ((SLOT_EMOJIS["PLUM"], 3,),): 60,
        ((SLOT_EMOJIS["BELL"], 3,),): 60,
        ((SLOT_EMOJIS["BAR"], 3,),): 200,
    }  # Set up the scores for each combination

    SLOT_ITEMS = [
        [
            *(SLOT_EMOJIS["LEMON"],) * 3, *(SLOT_EMOJIS["CHERRY"],) * 6, *(SLOT_EMOJIS["ORANGE"],) * 6,
            *(SLOT_EMOJIS["PLUM"],) * 1, *(SLOT_EMOJIS["BELL"],) * 3, *(SLOT_EMOJIS["BAR"],) * 1,
        ],
        [
            *(SLOT_EMOJIS["LEMON"],) * 6, *(SLOT_EMOJIS["CHERRY"],) * 1, *(SLOT_EMOJIS["ORANGE"],) * 5,
            *(SLOT_EMOJIS["PLUM"],) * 6, *(SLOT_EMOJIS["BELL"],) * 1, *(SLOT_EMOJIS["BAR"],) * 1,
        ],
        [
            *(SLOT_EMOJIS["LEMON"],) * 1, *(SLOT_EMOJIS["CHERRY"],) * 3, *(SLOT_EMOJIS["ORANGE"],) * 1,
            *(SLOT_EMOJIS["PLUM"],) * 3, *(SLOT_EMOJIS["BELL"],) * 6, *(SLOT_EMOJIS["BAR"],) * 6,
        ],
    ]
    r = random.Random(1.0)
    for i in SLOT_ITEMS:
        r.shuffle(i)

    @classmethod
    def get_slots_score(cls, line) -> int:
        """
        Get the score of a line given three emojis.
        """

        for check, multiplier in cls.SLOT_SCORES.items():
            check_counter = 0
            for emoji, count in check:
                if line.count(emoji) == count:
                    check_counter += 1
            if len(check) == check_counter:
                return multiplier
        return 0

    @utils.command(aliases=['slot'])
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    @commands.guild_only()
    async def slots(self, ctx: utils.Context, *, bet: localutils.BetAmount = None):
        """
        Runs a slot machine.
        """

        # See where our reels ended up
        bet = bet or localutils.CurrencyAmount()
        slot_indexes = [
            random.randint(0, len(self.SLOT_ITEMS[0]) - 1),
            random.randint(0, len(self.SLOT_ITEMS[1]) - 1),
            random.randint(0, len(self.SLOT_ITEMS[2]) - 1),
        ]

        # See what our output for the reels is
        untransposed_lines = []
        for reel_index in range(0, 3):
            line = []
            for offset_index in range(-1, 2):
                try:
                    line.append(self.SLOT_ITEMS[reel_index][slot_indexes[reel_index] + offset_index])
                except IndexError:
                    line.append(self.SLOT_ITEMS[reel_index][-1])
            untransposed_lines.append(line)

        # Transpose the fruit
        transposed_lines = []
        for reel_index in range(0, 3):
            line = []
            for fruit_index in range(0, 3):
                line.append(untransposed_lines[fruit_index][reel_index])
            transposed_lines.append(line)

        # Join together the lines
        joined_lines = []
        for line in transposed_lines:
            joined_lines.append("".join(line))

        # Work out what to output
        multiplier = self.get_slots_score(joined_lines[1])
        embed = utils.Embed(use_random_colour=True).add_field("Roll", "\n".join(joined_lines))
        if bet.amount:
            if multiplier == 0:
                embed.add_field("Result", f"You lost, removed **{bet.amount:,}** from your account :c", inline=False)
            elif multiplier > 0:
                embed.add_field("Result", f"You won! Added **{bet.amount * multiplier:,}** to your account! :D", inline=False)
        else:
            if multiplier == 0:
                embed.add_field("Result", "You lost :c", inline=False)
            elif multiplier > 0:
                embed.add_field("Result", "You won! :D", inline=False)
        self.bot.dispatch("transaction", ctx.author, bet.currency, -bet.amount, "BLACKJACK", multiplier != 0)
        return await ctx.send(embed=embed)


def setup(bot: utils.Bot):
    x = SlotsCommands(bot)
    bot.add_cog(x)
