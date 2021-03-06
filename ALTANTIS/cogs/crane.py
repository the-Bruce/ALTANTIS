from discord.ext import commands

from ALTANTIS.utils.consts import CONTROL_ROLE, SCIENTIST
from ALTANTIS.utils.bot import perform, get_team
from ALTANTIS.utils.actions import DiscordAction, Message, FAIL_REACT
from ALTANTIS.subs.state import with_sub

class Crane(commands.Cog):
    """
    Commands for operating the crane.
    """
    @commands.command()
    @commands.has_any_role(SCIENTIST, CONTROL_ROLE)
    async def crane(self, ctx):
        """
        Drops the crane in your current location. Takes two turns to resolve.
        """
        await perform(drop_crane, ctx, get_team(ctx.channel))

def drop_crane(team : str) -> DiscordAction:
    def do_crane(sub):
        return Message(sub.inventory.drop_crane())
    return with_sub(team, do_crane, FAIL_REACT)