import re,discord
from discord.ext import commands
class AutoMod(commands.Cog):
 def __init__(self,bot): self.bot=bot; self.enabled={}
 @commands.command(name='automod')
 @commands.has_guild_permissions(manage_guild=True)
 async def automod(self,ctx,estado:str='on'): self.enabled[ctx.guild.id]=estado.lower() in ('on','ativar','true'); await ctx.send('🛡️ AutoMod '+('ativado.' if self.enabled[ctx.guild.id] else 'desativado.'))
 @commands.Cog.listener()
 async def on_message(self,m):
  if not m.guild or m.author.bot or not self.enabled.get(m.guild.id,True): return
  if re.search(r'(?:discord\.gg/|https?://\S+)',m.content,re.I) and not m.author.guild_permissions.manage_messages:
   try: await m.delete(); await m.channel.send(f'🛡️ {m.author.mention}, links não são permitidos.',delete_after=4)
   except discord.HTTPException: pass
async def setup(bot): await bot.add_cog(AutoMod(bot))
