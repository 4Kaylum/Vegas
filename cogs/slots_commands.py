import random


import voxelbotutils as utils

from cogs import utils as localutils


class SlotsCommands(utils.Cog):

    SLOT_EMOJIS = {
        "LEMON": "LEMON",
        "CHERRY": "CHERRY",
        "ORANGE": "ORANGE",
        "PLUM": "PLUM",
        "BELL": "BELL",
        "BAR": "BAR",
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
    for i in ITEMS:
        r.shuffle(i)

    @utils.command()
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    @commands.guild_only()
    async def slots(self, ctx: utils.Context, *, bet: localutils.BetAmount = None):
        """
        Runs a slot machine.
        """

        # See where our reels ended up
        slot_indexes = [
            random.randint(0, len(self.SLOT_ITEMS[0]) - 1),
            random.randint(0, len(self.SLOT_ITEMS[1]) - 1),
            random.randint(0, len(self.SLOT_ITEMS[2]) - 1),
        ]

        # See what our output for the reels is
        untransposed_lines = []
        for reel_index in range(0, 3):
            line = ""
            for fruit_index in range(0, 3):
                line += self.SLOT_ITEMS[reel_index][i - 1]
            untransposed_lines.append(line)

        # Transpose the fruit
        transposed_lines = []
        for reel_index in range(0, 3):
            line = ""
            for fruit_index in range(0, 3):
                line += untransposed_lines[fruit_index][reel_index]

        # Output
        return await ctx.send("\n".join(transposed_lines))


def setup(bot: utils.Bot):
    x = SlotsCommands(bot)
    bot.add_cog(x)
