import os
import random
import time
import aiosqlite
import discord
from discord import app_commands
from discord.ext import commands

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(BASE, 'data', 'abysmal.db')


def xp_for_next(level: int) -> int:
    return 100 + (level * 25)


class Levels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cooldowns = {}
        os.makedirs(os.path.dirname(DB), exist_ok=True)

    async def db(self):
        c = await aiosqlite.connect(DB)
        await c.execute('''CREATE TABLE IF NOT EXISTS xp (
            guild INTEGER NOT NULL,
            user INTEGER NOT NULL,
            xp INTEGER NOT NULL DEFAULT 0,
            level INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY(guild, user)
        )''')
        await c.commit()
        return c

    async def get_user(self, guild_id, user_id):
        c = await self.db()
        row = await (await c.execute(
            'SELECT xp, level FROM xp WHERE guild=? AND user=?',
            (guild_id, user_id)
        )).fetchone()
        await c.close()
        return row or (0, 0)

    async def add_xp(self, guild_id, user_id):
        c = await self.db()
        row = await (await c.execute(
            'SELECT xp, level FROM xp WHERE guild=? AND user=?',
            (guild_id, user_id)
        )).fetchone()

        xp, level = row or (0, 0)
        old_level = level
        xp += random.randint(8, 15)

        while xp >= xp_for_next(level):
            xp -= xp_for_next(level)
            level += 1

        await c.execute('''INSERT INTO xp(guild,user,xp,level) VALUES(?,?,?,?)
            ON CONFLICT(guild,user) DO UPDATE SET xp=excluded.xp, level=excluded.level''',
            (guild_id, user_id, xp, level)
        )
        await c.commit()
        await c.close()
        return old_level, level

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild or message.author.bot:
            return

        key = (message.guild.id, message.author.id)
        now = time.monotonic()
        if now - self.cooldowns.get(key, 0) < 30:
            return
        self.cooldowns[key] = now

        try:
            old_level, new_level = await self.add_xp(message.guild.id, message.author.id)
        except Exception as e:
            print(f'[LEVELS] Erro ao adicionar XP: {e}')
            return

        if new_level > old_level:
            embed = discord.Embed(
                title='✨ LEVEL UP!',
                description=f'{message.author.mention} chegou ao **nível {new_level}**!',
                color=discord.Color.from_rgb(170, 0, 0)
            )
            embed.set_thumbnail(url=message.author.display_avatar.url)
            embed.set_footer(text='Abysmal • Sistema de níveis')
            try:
                await message.channel.send(embed=embed, delete_after=10)
            except discord.HTTPException:
                pass

    @app_commands.command(name='rank', description='Mostra seu nível, XP e posição no servidor.')
    @app_commands.describe(usuario='Usuário que você quer consultar')
    async def rank(self, interaction: discord.Interaction, usuario: discord.Member = None):
        user = usuario or interaction.user
        xp, level = await self.get_user(interaction.guild.id, user.id)

        c = await self.db()
        row = await (await c.execute(
            'SELECT COUNT(*) FROM xp WHERE guild=? AND (level > ? OR (level = ? AND xp > ?))',
            (interaction.guild.id, level, level, xp)
        )).fetchone()
        await c.close()
        position = (row[0] or 0) + 1

        needed = xp_for_next(level)
        embed = discord.Embed(
            title='🏆 ABYSMAL RANK',
            description=f'**{user.display_name}**\nSeu progresso no servidor',
            color=discord.Color.from_rgb(170, 0, 0)
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name='⭐ Nível', value=f'`{level}`', inline=True)
        embed.add_field(name='✨ XP', value=f'`{xp}/{needed}`', inline=True)
        embed.add_field(name='🏅 Posição', value=f'`#{position}`', inline=True)
        embed.add_field(name='📈 Próximo nível', value=f'`{needed - xp} XP` restantes', inline=False)
        embed.set_footer(text=f'Abysmal • {interaction.guild.name}')
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='leaderboard', description='Mostra os 10 maiores níveis do servidor.')
    async def leaderboard(self, interaction: discord.Interaction):
        c = await self.db()
        rows = await (await c.execute(
            'SELECT user, xp, level FROM xp WHERE guild=? ORDER BY level DESC, xp DESC LIMIT 10',
            (interaction.guild.id,)
        )).fetchall()
        await c.close()

        embed = discord.Embed(
            title='🏆 ABYSMAL LEADERBOARD',
            description='Top 10 membros por nível e XP',
            color=discord.Color.from_rgb(170, 0, 0)
        )
        if not rows:
            embed.description = 'Ainda não existe XP registrado. Converse no servidor para começar!'
        else:
            medals = ['🥇', '🥈', '🥉']
            lines = []
            for index, (user_id, xp, level) in enumerate(rows, 1):
                member = interaction.guild.get_member(user_id)
                name = member.display_name if member else f'Usuário {user_id}'
                prefix = medals[index - 1] if index <= 3 else f'`#{index}`'
                lines.append(f'{prefix} **{name}** — Nível `{level}` • `{xp} XP`')
            embed.description = '\n'.join(lines)

        embed.set_footer(text=f'Abysmal • {interaction.guild.name}')
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Levels(bot))
