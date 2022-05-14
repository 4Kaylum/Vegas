import random
from typing import Optional

import discord
from discord.ext import commands, vbu

from cogs import utils


class SlotsCommands(utils.GamblingCog):

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
            *(SLOT_EMOJIS["LEMON"],) * 3, *(SLOT_EMOJIS["CHERRY"],) * 6,
            *(SLOT_EMOJIS["ORANGE"],) * 6, *(SLOT_EMOJIS["PLUM"],) * 1,
            *(SLOT_EMOJIS["BELL"],) * 3, *(SLOT_EMOJIS["BAR"],) * 1,
        ],
        [
            *(SLOT_EMOJIS["LEMON"],) * 6, *(SLOT_EMOJIS["CHERRY"],) * 1,
            *(SLOT_EMOJIS["ORANGE"],) * 5, *(SLOT_EMOJIS["PLUM"],) * 6,
            *(SLOT_EMOJIS["BELL"],) * 1, *(SLOT_EMOJIS["BAR"],) * 1,
        ],
        [
            *(SLOT_EMOJIS["LEMON"],) * 1, *(SLOT_EMOJIS["CHERRY"],) * 3,
            *(SLOT_EMOJIS["ORANGE"],) * 1, *(SLOT_EMOJIS["PLUM"],) * 3,
            *(SLOT_EMOJIS["BELL"],) * 6, *(SLOT_EMOJIS["BAR"],) * 6,
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

    @commands.command(
        aliases=['slot'],
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
    async def slots(
            self,
            ctx: vbu.SlashContext,
            bet: int,
            currency: str):
        """
        Runs a slot machine.
        """

        # Fix our bet amount into an object
        ba = utils.BetAmount(bet, currency)
        await ba.validate(ctx)

        # See where our reels ended up
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
                    line.append(
                        self.SLOT_ITEMS[reel_index][slot_indexes[reel_index] + offset_index]
                    )
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
        embed = vbu.Embed(use_random_colour=True).add_field("Roll", "\n".join(joined_lines))
        if ba.amount:
            if multiplier == 0:
                embed.add_field("Result", f"You lost, removed **{ba.amount:,}** from your account :c", inline=False)
            elif multiplier > 0:
                embed.add_field("Result", f"You won! Added **{ba.amount * multiplier:,}** to your account! :D", inline=False)
        else:
            if multiplier == 0:
                embed.add_field("Result", "You lost :c", inline=False)
            elif multiplier > 0:
                embed.add_field("Result", "You won! :D", inline=False)

        # And they win
        self.bot.dispatch(
            "transaction",
            ctx.author,
            ba.currency,
            -ba.amount if multiplier == 0 else ba.amount * multiplier,
            "GAME slots",
            multiplier != 0,
        )
        return await ctx.interaction.followup.send(embed=embed)

    slots.autocomplete(utils.autocomplete.currency_name_autocomplete)


def setup(bot: vbu.Bot):
    x = SlotsCommands(bot)
    bot.add_cog(x)
