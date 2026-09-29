import time
from collections import defaultdict, deque
import discord
from discord.ext import commands
from discord import app_commands

class AntiRaid(commands.Cog):
    def __init__(self, bot):
        self.bot=bot; self.joins=defaultdict(deque); self.locked=set()
    @app_commands.command(name='antiraid', description='Ativa/desativa proteção contra raids.')
    @app_commands.checks.has_permissions(manage_guild=True)
    async def antiraid(self, interaction: discord.Interaction, ativar: bool):
        if ativar: self.locked.discard(interaction.guild.id); await interaction.response.send_message('🛡️ AntiRaid ativado. Proteção automática contra entradas em massa está ligada.')
        else: self.locked.add(interaction.guild.id); await interaction.response.send_message('🛡️ AntiRaid desativado.')
    @commands.Cog.listener()
    async def on_member_join(self, member):
        gid=member.guild.id
        if gid in self.locked: return
        q=self.joins[gid]; now=time.monotonic(); q.append(now)
        while q and now-q[0]>12: q.popleft()
        if len(q)>=6:
            try:
                await member.guild.edit(verifications_level=discord.VerificationLevel.high)
            except discord.HTTPException: pass
            if len(q)>=10:
                # Don't mass-ban or mass-kick users automatically; notify staff instead.
                for ch in member.guild.text_channels:
                    if ch.permissions_for(member.guild.me).send_messages:
                        try:
                            await ch.send('🚨 **AntiRaid:** muitas entradas detectadas em pouco tempo. Verificação do servidor foi elevada temporariamente.', delete_after=12)
                        except discord.HTTPException: pass
                        break
                q.clear()

async def setup(bot): await bot.add_cog(AntiRaid(bot))
