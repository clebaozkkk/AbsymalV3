import re,io,os,asyncio
from datetime import datetime
import discord, aiosqlite
from discord import app_commands
from discord.ext import commands
DB='data/abysmal.db'
TYPES={'support':('🛠️','Suporte','Ajuda geral e dúvidas.'),'report':('🚨','Denúncia','Denúncias e problemas.'),'partnership':('🤝','Parceria','Propostas de parceria.'),'other':('📩','Outros','Outros assuntos.')}
def safe(s): return re.sub(r'-+','-',re.sub(r'[^a-zA-Z0-9-]','-',s.lower())).strip('-')[:18] or 'usuario'
async def db():
 c=await aiosqlite.connect(DB); await c.execute('CREATE TABLE IF NOT EXISTS cfg(guild INTEGER PRIMARY KEY,cat INTEGER,logs INTEGER,staff INTEGER)'); await c.execute('CREATE TABLE IF NOT EXISTS tickets(channel INTEGER PRIMARY KEY,guild INTEGER,owner INTEGER,kind TEXT,claimed INTEGER,closed INTEGER DEFAULT 0)'); await c.commit(); return c
async def cfg(g):
 c=await db(); r=await (await c.execute('SELECT cat,logs,staff FROM cfg WHERE guild=?',(g,))).fetchone(); await c.close(); return r or (None,None,None)
async def setcfg(g,**kw):
 a=await cfg(g); v=(kw.get('cat',a[0]),kw.get('logs',a[1]),kw.get('staff',a[2])); c=await db(); await c.execute('INSERT INTO cfg(guild,cat,logs,staff) VALUES(?,?,?,?) ON CONFLICT(guild) DO UPDATE SET cat=excluded.cat,logs=excluded.logs,staff=excluded.staff',(g,*v)); await c.commit(); await c.close()
async def gett(ch):
 c=await db(); r=await (await c.execute('SELECT guild,owner,kind,claimed,closed FROM tickets WHERE channel=?',(ch,))).fetchone(); await c.close(); return r
async def sett(ch,**kw):
 c=await db();
 for k,v in kw.items(): await c.execute(f'UPDATE tickets SET {k}=? WHERE channel=?',(v,ch))
 await c.commit(); await c.close()
async def transcript(ch):
 x=[f'Abysmal Transcript | #{ch.name}',f'Gerado: {datetime.now():%d/%m/%Y %H:%M:%S}','']
 async for m in ch.history(limit=None,oldest_first=True): x.append(f'[{m.created_at:%d/%m/%Y %H:%M}] {m.author} ({m.author.id}): {m.content or "[sem texto]"}')
 return '\n'.join(x)
class Select(discord.ui.Select):
 def __init__(self): super().__init__(placeholder='Escolha o tipo de atendimento...',options=[discord.SelectOption(label=v[1],description=v[2],emoji=v[0],value=k) for k,v in TYPES.items()])
 async def callback(self,i): await create(i,self.values[0])
class Panel(discord.ui.View):
 def __init__(self): super().__init__(timeout=None); self.add_item(Select())
class Controls(discord.ui.View):
 def __init__(self): super().__init__(timeout=None)
 @discord.ui.button(label='Assumir',emoji='📌',style=discord.ButtonStyle.primary,custom_id='aby:claim')
 async def claim(self,i,b):
  t=await gett(i.channel.id)
  if not t:return await i.response.send_message('Não é um ticket.',ephemeral=True)
  c=await cfg(i.guild.id)
  if c[2] and not i.user.guild_permissions.manage_channels and not any(r.id==c[2] for r in i.user.roles): return await i.response.send_message('Sem permissão.',ephemeral=True)
  await sett(i.channel.id,claimed=i.user.id); await i.response.send_message(f'📌 Atendimento assumido por {i.user.mention}.')
 @discord.ui.button(label='Adicionar',emoji='👤',style=discord.ButtonStyle.secondary,custom_id='aby:add')
 async def add(self,i,b): await i.response.send_modal(AddModal())
 @discord.ui.button(label='Renomear',emoji='📝',style=discord.ButtonStyle.secondary,custom_id='aby:rename')
 async def rename(self,i,b): await i.response.send_modal(RenameModal())
 @discord.ui.button(label='Transcript',emoji='📋',style=discord.ButtonStyle.secondary,custom_id='aby:trans')
 async def trans(self,i,b):
  await i.response.defer(ephemeral=True); f=discord.File(io.BytesIO((await transcript(i.channel)).encode()),filename=f'{i.channel.name}.txt'); await i.followup.send('📋 Transcript gerado.',file=f,ephemeral=True)
 @discord.ui.button(label='Fechar',emoji='🔒',style=discord.ButtonStyle.danger,custom_id='aby:close')
 async def close(self,i,b): await close(i,'Fechado pelo painel')
class AddModal(discord.ui.Modal,title='Adicionar usuário'):
 user_id=discord.ui.TextInput(label='ID do usuário')
 async def on_submit(self,i):
  try:
   m=i.guild.get_member(int(self.user_id.value)); assert m
   await i.channel.set_permissions(m,view_channel=True,send_messages=True,read_message_history=True); await i.response.send_message(f'👤 {m.mention} adicionado.')
  except: await i.response.send_message('ID inválido.',ephemeral=True)
class RenameModal(discord.ui.Modal,title='Renomear ticket'):
 name=discord.ui.TextInput(label='Novo nome')
 async def on_submit(self,i): await i.channel.edit(name='🎫・'+safe(self.name.value)); await i.response.send_message('📝 Renomeado.')
async def create(i,kind):
 await i.response.defer(ephemeral=True); g=i.guild; c=await cfg(g.id)
 con=await db(); r=await (await con.execute('SELECT channel FROM tickets WHERE guild=? AND owner=? AND closed=0',(g.id,i.user.id))).fetchone(); await con.close()
 if r and g.get_channel(r[0]): return await i.followup.send(f'Você já tem um ticket: <#{r[0]}>',ephemeral=True)
 cat=g.get_channel(c[0]) if c[0] else None
 if not cat: cat=await g.create_category('🎫 TICKETS'); await setcfg(g.id,cat=cat.id)
 emoji,label,desc=TYPES[kind]; ow={g.default_role:discord.PermissionOverwrite(view_channel=False),i.user:discord.PermissionOverwrite(view_channel=True,send_messages=True,read_message_history=True),g.me:discord.PermissionOverwrite(view_channel=True,send_messages=True,manage_channels=True)}
 if c[2] and g.get_role(c[2]): ow[g.get_role(c[2])]=discord.PermissionOverwrite(view_channel=True,send_messages=True,read_message_history=True)
 ch=await g.create_text_channel(f'🎫・{kind}-{safe(i.user.name)}',category=cat,overwrites=ow,topic=f'Ticket de {i.user} | {label}')
 con=await db(); await con.execute('INSERT INTO tickets VALUES(?,?,?,?,?,0)',(ch.id,g.id,i.user.id,kind,0)); await con.commit(); await con.close()
 e=discord.Embed(title=f'{emoji} {label}',description=f'Olá {i.user.mention}!\n\n**Tipo:** {label}\n{desc}\n\nExplique seu problema com detalhes.',color=discord.Color.dark_red()); e.set_footer(text='Abysmal • Sistema de Tickets')
 await ch.send(content=i.user.mention,embed=e,view=Controls());
 if c[2] and g.get_role(c[2]): await ch.send(f'{g.get_role(c[2]).mention} novo ticket aberto.')
 await i.followup.send(f'🎫 Criado: {ch.mention}',ephemeral=True)
 if c[1] and g.get_channel(c[1]): await g.get_channel(c[1]).send(f'🎫 Ticket aberto: {ch.mention} | {i.user.mention} | `{label}`')
async def close(i,reason):
 t=await gett(i.channel.id)
 if not t:return await i.response.send_message('Não é um ticket.',ephemeral=True)
 c=await cfg(i.guild.id); allowed=i.user.guild_permissions.manage_channels or i.user.id==t[1] or (c[2] and any(r.id==c[2] for r in i.user.roles))
 if not allowed:return await i.response.send_message('Sem permissão.',ephemeral=True)
 await i.response.defer(); txt=await transcript(i.channel)
 if c[1] and i.guild.get_channel(c[1]): await i.guild.get_channel(c[1]).send(f'🔒 Ticket fechado por {i.user.mention} | Motivo: `{reason}`',file=discord.File(io.BytesIO(txt.encode()),filename=f'{i.channel.name}.txt'))
 await sett(i.channel.id,closed=1); await i.followup.send('🔒 Ticket fechado.'); await asyncio.sleep(3); await i.channel.delete()
class Tickets(commands.Cog):
 def __init__(self,bot): self.bot=bot
 async def cog_load(self): self.bot.add_view(Panel()); self.bot.add_view(Controls())
 @app_commands.command(name='ticket_painel',description='Envia o painel de tickets.')
 @app_commands.checks.has_permissions(manage_guild=True)
 async def panel(self,i):
  e=discord.Embed(title='🎫 Central de Atendimento',description='Escolha abaixo o tipo de atendimento.',color=discord.Color.dark_red()); e.add_field(name='🛠️ Suporte',value='Ajuda e dúvidas',inline=True); e.add_field(name='🚨 Denúncia',value='Denúncias',inline=True); e.add_field(name='🤝 Parceria',value='Parcerias',inline=True); e.add_field(name='📩 Outros',value='Outros assuntos',inline=True); await i.channel.send(embed=e,view=Panel()); await i.response.send_message('✅ Painel enviado.',ephemeral=True)
 @app_commands.command(name='ticket_categoria',description='Define a categoria dos tickets.')
 @app_commands.checks.has_permissions(manage_guild=True)
 async def category(self,i,categoria:discord.CategoryChannel): await setcfg(i.guild.id,cat=categoria.id); await i.response.send_message(f'✅ {categoria.mention}',ephemeral=True)
 @app_commands.command(name='ticket_logs',description='Define o canal de logs.')
 @app_commands.checks.has_permissions(manage_guild=True)
 async def logs(self,i,canal:discord.TextChannel): await setcfg(i.guild.id,logs=canal.id); await i.response.send_message(f'✅ {canal.mention}',ephemeral=True)
 @app_commands.command(name='ticket_staff',description='Define o cargo da equipe.')
 @app_commands.checks.has_permissions(manage_guild=True)
 async def staff(self,i,cargo:discord.Role): await setcfg(i.guild.id,staff=cargo.id); await i.response.send_message(f'✅ {cargo.mention}',ephemeral=True)
 @app_commands.command(name='ticket_fechar',description='Fecha o ticket atual.')
 async def closecmd(self,i,motivo:str='Sem motivo'): await close(i,motivo)
async def setup(bot): await bot.add_cog(Tickets(bot))
