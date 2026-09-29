import discord
from discord import app_commands
from discord.ext import commands
class Admin(commands.Cog):
 def __init__(self,bot): self.bot=bot
 @app_commands.command(name='lock',description='Bloqueia o canal.')
 @app_commands.checks.has_permissions(manage_channels=True)
 async def lock(self,i): await i.channel.set_permissions(i.guild.default_role,send_messages=False); await i.response.send_message('🔒 Canal bloqueado.')
 @app_commands.command(name='unlock',description='Desbloqueia o canal.')
 @app_commands.checks.has_permissions(manage_channels=True)
 async def unlock(self,i): await i.channel.set_permissions(i.guild.default_role,send_messages=None); await i.response.send_message('🔓 Canal desbloqueado.')
 @app_commands.command(name='slowmode',description='Define slowmode em segundos.')
 @app_commands.checks.has_permissions(manage_channels=True)
 async def slowmode(self,i,segundos:int): await i.channel.edit(slowmode_delay=max(0,min(21600,segundos))); await i.response.send_message(f'🐢 Slowmode: {segundos}s.')
 @app_commands.command(name='nick',description='Muda o apelido.')
 @app_commands.checks.has_permissions(manage_nicknames=True)
 async def nick(self,i,m:discord.Member,apelido:str): await m.edit(nick=apelido); await i.response.send_message('✅ Apelido alterado.')
 @app_commands.command(name='say',description='Envia uma mensagem pelo bot.')
 @app_commands.checks.has_permissions(manage_messages=True)
 async def say(self,i,texto:str): await i.response.defer(ephemeral=True); await i.channel.send(texto); await i.delete_original_response()
async def setup(bot): await bot.add_cog(Admin(bot))
