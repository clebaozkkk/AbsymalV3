import discord
from discord import app_commands
from discord.ext import commands

RED = discord.Color.from_rgb(170, 0, 0)


def base_embed(title, description=None):
    e = discord.Embed(title=title, description=description, color=RED)
    e.set_footer(text='Abysmal • Sistema do servidor')
    return e


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='ping', description='Mostra a latência do Abysmal.')
    async def ping(self, interaction):
        ms = round(self.bot.latency * 1000)
        e = base_embed('🏓 ABYSMAL PING', 'Conexão do bot com o Discord')
        e.add_field(name='⚡ Latência', value=f'`{ms} ms`', inline=True)
        e.add_field(name='🟢 Status', value='`Online`', inline=True)
        await interaction.response.send_message(embed=e)

    @app_commands.command(name='serverinfo', description='Mostra informações detalhadas do servidor.')
    async def serverinfo(self, interaction):
        g = interaction.guild
        e = base_embed('🛡️ INFORMAÇÕES DO SERVIDOR', f'**{g.name}**')
        e.set_thumbnail(url=g.icon.url if g.icon else discord.Embed.Empty)
        e.add_field(name='👥 Membros', value=f'`{g.member_count}`', inline=True)
        e.add_field(name='💬 Canais', value=f'`{len(g.channels)}`', inline=True)
        e.add_field(name='🎭 Cargos', value=f'`{len(g.roles)}`', inline=True)
        e.add_field(name='👑 Dono', value=f'<@{g.owner_id}>', inline=True)
        e.add_field(name='🆔 ID', value=f'`{g.id}`', inline=True)
        e.add_field(name='📅 Criado', value=discord.utils.format_dt(g.created_at, 'D'), inline=True)
        await interaction.response.send_message(embed=e)

    @app_commands.command(name='userinfo', description='Mostra informações de um membro.')
    async def userinfo(self, interaction, membro: discord.Member = None):
        member = membro or interaction.user
        e = base_embed('👤 PERFIL DO USUÁRIO', f'**{member.display_name}**')
        e.set_thumbnail(url=member.display_avatar.url)
        e.add_field(name='🆔 ID', value=f'`{member.id}`', inline=True)
        e.add_field(name='🤖 Bot', value='Sim' if member.bot else 'Não', inline=True)
        e.add_field(name='📅 Conta criada', value=discord.utils.format_dt(member.created_at, 'D'), inline=False)
        e.add_field(name='📥 Entrou no servidor', value=discord.utils.format_dt(member.joined_at, 'D') if member.joined_at else 'Desconhecido', inline=False)
        e.add_field(name='🎭 Cargos', value=f'`{max(0, len(member.roles)-1)}`', inline=True)
        await interaction.response.send_message(embed=e)

    @app_commands.command(name='avatar', description='Mostra o avatar de um membro.')
    async def avatar(self, interaction, membro: discord.Member = None):
        member = membro or interaction.user
        e = base_embed('🖼️ AVATAR', f'Avatar de **{member.display_name}**')
        e.set_image(url=member.display_avatar.url)
        await interaction.response.send_message(embed=e)

    @app_commands.command(name='botinfo', description='Mostra informações do Abysmal.')
    async def botinfo(self, interaction):
        e = base_embed('🌑 ABYSMAL', 'Painel de informações do bot')
        e.set_thumbnail(url=self.bot.user.display_avatar.url)
        e.add_field(name='🌐 Servidores', value=f'`{len(self.bot.guilds)}`', inline=True)
        e.add_field(name='👥 Usuários', value=f'`{len(self.bot.users)}`', inline=True)
        e.add_field(name='⚡ Latência', value=f'`{round(self.bot.latency*1000)} ms`', inline=True)
        e.add_field(name='🧩 Comandos', value=f'`{len(self.bot.tree.get_commands())}`', inline=True)
        e.add_field(name='🐍 Python', value='`3.x`', inline=True)
        e.set_footer(text='Abysmal • Seu servidor, suas regras')
        await interaction.response.send_message(embed=e)

    @app_commands.command(name='infobot', description='Abre o painel de informações do Abysmal.')
    async def infobot(self, interaction):
        await self.botinfo(interaction)

    @app_commands.command(name='help', description='Abre o painel de comandos do Abysmal.')
    async def help(self, interaction):
        e = base_embed('🌑 ABYSMAL • CENTRAL DE COMANDOS', 'Use os comandos abaixo para controlar e consultar o servidor.')
        e.add_field(name='🏆 Níveis', value='`/rank` `/leaderboard`', inline=False)
        e.add_field(name='🛡️ Moderação', value='`/ban` `/kick` `/timeout` `/untimeout` `/warn` `/warnings` `/clear` `/unban`', inline=False)
        e.add_field(name='⚙️ Administração', value='`/lock` `/unlock` `/slowmode` `/nick` `/say`', inline=False)
        e.add_field(name='🎫 Tickets', value='`/ticket_painel` `/close`', inline=False)
        e.add_field(name='🛡️ Segurança', value='`/automod` `/antilink` `/antispam` `/antiraid`', inline=False)
        e.add_field(name='🔧 Utilidade', value='`/ping` `/serverinfo` `/userinfo` `/avatar` `/botinfo` `/infobot`', inline=False)
        e.set_footer(text='Abysmal • Use / para encontrar todos os comandos')
        await interaction.response.send_message(embed=e)


async def setup(bot):
    await bot.add_cog(Utility(bot))
