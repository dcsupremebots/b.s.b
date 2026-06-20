import os
import asyncio
import discord
from discord.ext import commands
from motor.motor_asyncio import AsyncIOMotorClient

# Coleta as variáveis de ambiente direto do sistema (configuradas no painel da hospedagem)
TOKEN = os.environ.get("DISCORD_TOKEN")
MONGO_URI = os.environ.get("MONGO_URI")

# Configuração das Intents do Discord
intents = discord.Intents.default()
intents.message_content = True  
intents.members = True          

class BotTorneio(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents, application_id=None)
        self.db = None
        self.cluster = None

    async def setup_hook(self):
        # 1. Inicializa a conexão assíncrona com o MongoDB
        if MONGO_URI:
            try:
                self.cluster = AsyncIOMotorClient(MONGO_URI)
                self.db = self.cluster["dc_supreme_db"]
                print("✅ [DATABASE] Conexão assíncrona com o MongoDB estabelecida com sucesso!")
            except Exception as e:
                print(f"❌ [DATABASE] Erro ao conectar ao MongoDB: {e}")
        else:
            print("⚠️ [DATABASE] MONGO_URI não encontrada nas variáveis de ambiente da hospedagem.")

        # 2. Carrega as Cogs de forma dinâmica
        if os.path.exists("./cogs"):
            for filename in os.listdir("./cogs"):
                if filename.endswith(".py") and not filename.startswith("_"):
                    try:
                        await self.load_extension(f"cogs.{filename[:-3]}")
                        print(f"📦 [COGS] Módulo '{filename}' carregado com sucesso.")
                    except Exception as e:
                        print(f"❌ [COGS] Erro ao carregar o módulo '{filename}': {e}")

        # 3. Sincroniza os Comandos de Barra (Slash Commands)
        print("🔄 [SLASH] Sincronizando comandos globais com o Discord...")
        try:
            synced = await self.tree.sync()
            print(f"🚀 [SLASH] {len(synced)} comandos globais sincronizados!")
        except Exception as e:
            print(f"❌ [SLASH] Erro ao sincronizar comandos: {e}")

    async def on_ready(self):
        print("\n==================================================")
        print(f"🤖 Bot Online na Nuvem: {self.user.name} ({self.user.id})")
        print(f"📊 Ativo em {len(self.guilds)} servidor(es)")
        print("==================================================\n")
        
        await self.change_presence(
            activity=discord.Game(name="🏆 Organizando Torneios Supreme")
        )

async def main():
    if not TOKEN:
        print("❌ [ERRO CRÍTICO] O DISCORD_TOKEN não foi encontrado nas variáveis de ambiente!")
        return
        
    bot = BotTorneio()
    
    try:
        await bot.start(TOKEN)
    except KeyboardInterrupt:
        await bot.close()
    finally:
        if bot.cluster:
            bot.cluster.close()
            print("🔒 [DATABASE] Conexão com o MongoDB encerrada.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot desligado.")
