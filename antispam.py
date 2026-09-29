import time
from collections import defaultdict, deque
import discord
from discord.ext import commands

class AntiSpam(commands.Cog):
    def __init__(self, bot):
        self.bot=bot
        self.messages=defaultdict(lambda: deque(maxlen=8))
        self.warned=set()
    @commands.Cog.listener()
    async def on_message(self, m):
        if m.author.bot or not m.guild or m.author.guild_permissions.manage_messages: return
        key=(m.guild.id,m.author.id); now=time.monotonic(); q=self.messages[key]
        q.append((now,m.content.strip().lower()))
        while q and now-q[0][0]>6: q.popleft()
        recent=list(q)
        flood=len(recent)>=6 and (recent[-1][0]-recent[0][0] <= 5)
        dup=len(recent)>=3 and len({x[1] for x in recent[-3:]})==1 and recent[-1][1]
        if flood or dup:
            try:
                await m.delete()
                await m.channel.send(f'🛡️ {m.author.mention}, evite spam/flood.', delete_after=4)
            except discord.HTTPException: pass
            self.messages[key].clear()

async def setup(bot): await bot.add_cog(AntiSpam(bot))
