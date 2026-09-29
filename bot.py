import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

BASE = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE)
load_dotenv(os.path.join(BASE, '.env'))
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = os.getenv('GUILD_ID', '').strip()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class Abysmal(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents)

    async def setup_hook(self):
        names = ('tickets','utility','admin','moderation','welcome','automod','levels','suggestions','antispam','antiraid')
        for name in names:
            try:
                await self.load_extension(f'cogs.{name}')
                print(f'[ABYSMAL] Cog carregado: {name}')
            except Exception as e:
                print(f'[ABYSMAL] Erro no cog {name}: {e}')

        try:
            if GUILD_ID.isdigit():
                guild = discord.Object(id=int(GUILD_ID))
                self.tree.copy_global_to(guild=guild)
                synced = await self.tree.sync(guild=guild)
                print(f'[ABYSMAL] {len(synced)} comandos sincronizados no servidor {GUILD_ID}.')
            else:
                synced = await self.tree.sync()
                print(f'[ABYSMAL] {len(synced)} comandos globais sincronizados.')
        except Exception as e:
            print(f'[ABYSMAL] Erro ao sincronizar comandos: {e}')

bot = Abysmal()

@bot.event
async def on_ready():
    print(f'Abysmal online: {bot.user} ({bot.user.id})')

if not TOKEN:
    raise RuntimeError('DISCORD_TOKEN não encontrado no .env')

bot.run(TOKEN)
