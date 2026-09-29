import discord
from discord import app_commands
from discord.ext import commands
class Welcome(commands.Cog):
 def __init__(self,bot): self.bot=bot; self.channels={}
 @app_commands.command(name='setwelcome',description='Define o canal de boas-vindas.')
 @app_commands.checks.has_permissions(manage_guild=True)
 async def setwelcome(self,i,canal:discord.TextChannel): self.channels[i.guild.id]=canal.id; await i.response.send_message(f'👋 Boas-vindas: {canal.mention}',ephemeral=True)
 @commands.Cog.listener()
 async def on_member_join(self,m):
  cid=self.channels.get(m.guild.id); ch=m.guild.get_channel(cid) if cid else None
  if ch:
   e=discord.Embed(title='👋 Bem-vindo!',description=f'Bem-vindo(a), {m.mention}, ao **{m.guild.name}**!',color=discord.Color.dark_red()); await ch.send(embed=e)
async def setup(bot): await bot.add_cog(Welcome(bot))
