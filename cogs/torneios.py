import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime

class Torneios(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.guild_only()
    class TorneioGroup(app_commands.Group):
        def __init__(self, cog):
            super().__init__(name="torneio", description="Comandos para gerenciamento de torneios")
            self.cog = cog

        @app_commands.command(name="criar", description="Cria um novo torneio no padrão do banco")
        @app_commands.describe(
            nome="Nome do torneio",
            vagas="Quantidade máxima de jogadores"
        )
        async def criar_torneio(self, interaction: discord.Interaction, nome: str, vagas: int):
            await interaction.response.defer(ephemeral=True)

            # Estrutura exata com base no seu esquema de documentoaprovação.json
            documento_aprovacao = {
                "userdocumento": f"@{interaction.user.name}||id:{interaction.user.id}",
                "discord_banco_de_dados": {
                    "temp": {
                        "nome_torneio": nome,
                        "vagas_totais": vagas,
                        "vagas_preenchidas": 0,
                        "status": "Aguardando Aprovação",
                        "data_solicitacao": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                    },
                    "fixo_ate_tirar": {
                        "servidor_id": interaction.guild_id,
                        "jogadores_inscritos": []
                    },
                    "fixo": {
                        "criado_por_id": interaction.user.id,
                        "autenticado": True
                    }
                }
            }

            try:
                # Insere o JSON formatado na coleção 'aprovações'
                result = await self.cog.bot.db["aprovações"].insert_one(documento_aprovacao)
                
                embed = discord.Embed(
                    title="📝 DOCUMENTO DE APROVAÇÃO GERADO",
                    description=f"O esquema para o torneio **{nome}** foi enviado ao banco.",
                    color=discord.Color.blue()
                )
                embed.add_field(name="👤 User", value=f"`@{interaction.user.name}`", inline=True)
                embed.add_field(name="📂 Coleção", value="`aprovações`", inline=True)
                embed.add_field(name="🆔 Object ID", value=f"`{result.inserted_id}`", inline=False)
                
                await int.followup.send(embed=embed)
                
            except Exception as e:
                print(f"❌ [ERRO MONGO] Falha ao estruturar documento: {e}")
                await interaction.followup.send("❌ Erro interno ao salvar no formato especificado.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Torneios(bot))
    bot.tree.add_command(Torneios(bot).TorneioGroup(Torneios(bot)))
