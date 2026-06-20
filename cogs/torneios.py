import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime

class Torneios(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Grupo principal de comandos: /torneio
    @app_commands.guild_only()
    class TorneioGroup(app_commands.Group):
        def __init__(self, cog):
            super().__init__(name="torneio", description="Comandos para gerenciamento de torneios")
            self.cog = cog

        # Subcomando: /torneio criar
        @app_commands.command(name="criar", description="Cria um novo torneio e salva no MongoDB")
        @app_commands.describe(
            nome="Nome do torneio",
            vagas="Quantidade máxima de jogadores ou equipes",
            tipo="Formato do torneio (ex: Eliminatória Simples, Pontos)"
        )
        async def criar_torneio(self, interaction: discord.Interaction, nome: str, vagas: int, tipo: str):
            await interaction.response.defer(ephemeral=True)

            # Estrutura do documento que vai pro MongoDB
            dados_torneio = {
                "nome": nome,
                "vagas_totais": vagas,
                "vagas_preenchidas": 0,
                "tipo": tipo,
                "status": "Inscrições Abertas",
                "criado_por": interaction.user.id,
                "servidor_id": interaction.guild_id,
                "data_criacao": datetime.utcnow(),
                "jogadores": []
            }

            try:
                # Acessa a database do main.py e insere o documento na collection 'torneios'
                result = await self.cog.bot.db["torneios"].insert_one(dados_torneio)
                
                # Resposta visual bonita usando Embed
                embed = discord.Embed(
                    title="🏆 NOVO TORNEIO CRIADO!",
                    description=f"O torneio **{nome}** foi registrado com sucesso na nuvem.",
                    color=discord.Color.green()
                )
                embed.add_field(name="📌 Formato", value=tipo, inline=True)
                embed.add_field(name="👥 Vagas", value=f"{vagas}", inline=True)
                embed.add_field(name="🆔 ID no Banco", value=f"`{result.inserted_id}`", inline=False)
                embed.set_footer(text=f"Criado por {interaction.user.name}", icon_url=interaction.user.display_avatar.url)

                await interaction.followup.send(embed=embed)
                
            except Exception as e:
                print(f"❌ [ERRO MONGO] Falha ao salvar torneio: {e}")
                await interaction.followup.send("❌ Erro interno ao salvar o torneio no banco de dados.", ephemeral=True)

# Função obrigatória para o bot carregar a Cog
async def setup(bot):
    await bot.add_cog(Torneios(bot))
    # Registra o grupo de comandos na árvore do bot
    bot.tree.add_command(Torneios(bot).TorneioGroup(Torneios(bot)))
