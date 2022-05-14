import discord
from discord.ext import commands, vbu


async def currency_name_autocomplete(
        cog: commands.Cog,
        ctx: commands.SlashContext,
        interaction: discord.Interaction) -> None:
    """
    An autocomplete for currency names.
    """

    async with vbu.Database() as db:
        rows = await db.call(
            """SELECT * FROM guild_currencies WHERE guild_id=$1""",
            interaction.guild_id,
        )
    await interaction.response.send_autocomplete([
        discord.ApplicationCommandOptionChoice(name=r['currency_name'])
        for r in rows
    ])
