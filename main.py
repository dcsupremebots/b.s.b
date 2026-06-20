import os
import asyncio
import discord
from discord.ext import commands
from motor.motor_asyncio import AsyncIOMotorClient
from estrutura import GerenciadorEstrutura  # Chamando o chefe da raiz

TOKEN = os.environ.get("DISCORD_TOKEN")
MONGO_URI = os.environ.get("MONGO_URI")

intents = discord.Intents.default()
intents.message_content = True  
intents.members = True          

class BotTorneio(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents, application_id=None)
        self.db = None
        self.cluster = None
        self.chefe_estrutura = None  # Espaço para o chefe trabalhar

    async def setup_hook(self):
        # 1. Estabiliza a conexão com o Banco de Dados
        if MONGO_URI:
            try:
                self.cluster = AsyncIOMotorClient(MONGO_URI)
                self.db = self.cluster["dc_supreme_db"]
                print("✅ [DIRETOR] Conexão com o MongoDB estabelecida.")
                
                # Instancia o chefe da estrutura passando o banco de dados para ele
                self.chefe_estrutura = GerenciadorEstrutura(self.db)
            except Exception as e:
                print(f"❌ [DIRETOR] Erro no MongoDB: {e}")

        # 2. Chama os funcionários (comandos na pasta cogs)
        if os.path.exists("./cogs"):
            for filename in os.listdir("./cogs"):
                if filename.endswith(".py") and not filename.startswith("_"):
                    await self.load_extension(f"cogs.{filename[:-3]}")
                    print(f"📦 [DIRETOR] Funcionário '{filename}' ativado.")

        # 3. Sincroniza os comandos com o Discord
        try:
            await self.tree.sync()
            print("🚀 [DIRETOR] Comandos sincronizados com o Discord.")
        except Exception as e:
            print(f"❌ [DIRETOR] Erro ao sincronizar: {e}")

    async def on_guild_join(self, guild: discord.Guild):
        # Diretor recebe o evento do Discord e manda o chefe da estrutura resolver
        if self.chefe_estrutura:
            await self.chefe_estrutura.criar_documento_inicial(guild)

    async def on_ready(self):
        print(f"\n🤖 {self.user.name} online e pronto para direcionar!\n")

async def main():
    if not TOKEN:
        print("❌ DISCORD_TOKEN faltando.")
        return
    bot = BotTorneio()
    try:
        await bot.start(TOKEN)
    except KeyboardInterrupt:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())
