import discord
from discord import app_commands
from discord.ext import commands
class Suggestions(commands.Cog):
 def __init__(self,bot): self.bot=bot
 @app_commands.command(name='suggest',description='Envia uma sugestão.')
 async def suggest(self,i,texto:str):
  e=discord.Embed(title='💡 Sugestão',description=texto,color=discord.Color.dark_red()); e.set_author(name=str(i.user),icon_url=i.user.display_avatar.url); e.set_footer(text='Abysmal • Sugestões'); await i.response.send_message(embed=e); msg=await i.original_response();
  try:
   await msg.add_reaction('👍'); await msg.add_reaction('👎')
  except: pass
async def setup(bot): await bot.add_cog(Suggestions(bot))
