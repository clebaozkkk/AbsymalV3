import os, discord, aiosqlite
from discord import app_commands
from discord.ext import commands
DB=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'abysmal.db')
class Moderation(commands.Cog):
 def __init__(self,bot):
  self.bot=bot
  os.makedirs(os.path.dirname(DB), exist_ok=True)
 async def db(self):
  c=await aiosqlite.connect(DB); await c.execute('CREATE TABLE IF NOT EXISTS warns(guild INTEGER,user INTEGER,mod INTEGER,reason TEXT,created TEXT DEFAULT CURRENT_TIMESTAMP)'); await c.commit(); return c
 @app_commands.command(name='ban',description='Bane um membro.')
 @app_commands.checks.has_permissions(ban_members=True)
 async def ban(self,i,m:discord.Member,razao:str='Sem motivo'): await m.ban(reason=razao); await i.response.send_message(f'🔨 {m} banido. Motivo: {razao}')
 @app_commands.command(name='kick',description='Expulsa um membro.')
 @app_commands.checks.has_permissions(kick_members=True)
 async def kick(self,i,m:discord.Member,razao:str='Sem motivo'): await m.kick(reason=razao); await i.response.send_message(f'👢 {m} expulso. Motivo: {razao}')
 @app_commands.command(name='timeout',description='Coloca membro em timeout.')
 @app_commands.checks.has_permissions(moderate_members=True)
 async def timeout(self,i,m:discord.Member,minutos:int,razao:str='Sem motivo'): await m.timeout(discord.utils.utcnow()+__import__('datetime').timedelta(minutes=minutos),reason=razao); await i.response.send_message(f'⏳ {m.mention} em timeout por {minutos} min.')
 @app_commands.command(name='untimeout',description='Remove timeout.')
 @app_commands.checks.has_permissions(moderate_members=True)
 async def untimeout(self,i,m:discord.Member): await m.timeout(None); await i.response.send_message(f'✅ Timeout removido de {m.mention}.')
 @app_commands.command(name='warn',description='Adverte um membro.')
 @app_commands.checks.has_permissions(moderate_members=True)
 async def warn(self,i,m:discord.Member,razao:str='Sem motivo'):
  c=await self.db(); await c.execute('INSERT INTO warns(guild,user,mod,reason) VALUES(?,?,?,?)',(i.guild.id,m.id,i.user.id,razao)); await c.commit(); n=await (await c.execute('SELECT COUNT(*) FROM warns WHERE guild=? AND user=?',(i.guild.id,m.id))).fetchone(); await c.close(); await i.response.send_message(f'⚠️ {m.mention} recebeu warn #{n[0]}. {razao}')
 @app_commands.command(name='warnings',description='Mostra warns de um membro.')
 async def warnings(self,i,m:discord.Member):
  c=await self.db(); rows=await (await c.execute('SELECT reason,created FROM warns WHERE guild=? AND user=? ORDER BY rowid DESC LIMIT 10',(i.guild.id,m.id))).fetchall(); await c.close(); await i.response.send_message('⚠️ Sem warns.' if not rows else '\n'.join(f'• {r} ({d})' for r,d in rows))
 @app_commands.command(name='clear',description='Apaga mensagens.')
 @app_commands.checks.has_permissions(manage_messages=True)
 async def clear(self,i,quantidade:int): await i.response.defer(ephemeral=True); n=await i.channel.purge(limit=max(1,min(100,quantidade))); await i.followup.send(f'🧹 {len(n)} mensagens apagadas.',ephemeral=True)
 @app_commands.command(name='unban',description='Desbane por ID.')
 @app_commands.checks.has_permissions(ban_members=True)
 async def unban(self,i,usuario_id:str):
  try: u=await self.bot.fetch_user(int(usuario_id)); await i.guild.unban(u); await i.response.send_message(f'✅ {u} desbanido.')
  except: await i.response.send_message('❌ ID inválido ou usuário não banido.',ephemeral=True)
async def setup(bot): await bot.add_cog(Moderation(bot))
