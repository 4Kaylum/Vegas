import random

import discord
import voxelbotutils as utils


class DiceCommands(utils.Cog):

    async def roll_dice(self, ctx: utils.Context, dice_limit: int, multiplier: int, bet_amount: int = 0):
        """
        Roll the dice on the user's bet.
        """

        # Work out what the user's rolled
        rolled_number = random.randint(1, 100)
        user_won = rolled_number > dice_limit

        # Work out what to say to the user
        embed = utils.Embed(title=f"\N{GAME DIE} {rolled_number}")
        if user_won:
            embed.colour = discord.Colour.green()
            embed.description = "You won! :D"
            if bet_amount:
                embed.description = f"You won! Added {bet_amount * (2 - 1)} to your account!"
        else:
            embed.colour = discord.Colour.red()
            embed.description = "You lost :c"
            if bet_amount:
                embed.description = f"You lost, removed {bet_amount} from your account :c"

        # Tell the user all is well
        return await ctx.send(embed=embed)

    @utils.command(name="55x2")
    async def dice_55x2(self, ctx: utils.Context, *, bet_amount: int = 0):
        """
        Place a bet on a dice roll - any number rolled that's higher than 55 will multiply your bet x2.
        """

        await self.roll_dice(ctx, 55, 2, bet_amount)

    @utils.command(name="75x3")
    async def dice_75x3(self, ctx: utils.Context, *, bet_amount: int = 0):
        """
        Place a bet on a dice roll - any number rolled that's higher than 75 will multiply your bet x3.
        """

        await self.roll_dice(ctx, 75, 3, bet_amount)

    @utils.command(name="95x5")
    async def dice_95x5(self, ctx: utils.Context, *, bet_amount: int = 0):
        """
        Place a bet on a dice roll - any number rolled that's higher than 95 will multiply your bet x5.
        """

        await self.roll_dice(ctx, 95, 5, bet_amount)


def setup(bot: utils.Bot):
    x = DiceCommands(bot)
    bot.add_cog(x)
