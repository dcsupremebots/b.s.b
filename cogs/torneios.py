import discord
from discord import app_commands
from discord.ext import commands

class Torneios(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.guild_only()
    class SetupGroup(app_commands.Group):
        def __init__(self, cog):
            super().__init__(name="setup", description="Configurações do bot")
            self.cog = cog

        @app_commands.command(name="configurar", description="Atualiza o canal e cargo da Staff")
        async def configurar_bot(self, interaction: discord.Interaction, canal: discord.TextChannel, cargo_staff: discord.Role):
            await interaction.response.defer(ephemeral=True)

            filtro = {"discord_banco_de_dados.fixo_ate_tirar.servidor_id": interaction.guild_id}
            atualizacao = {
                "$set": {
                    "discord_banco_de_dados.temp.status_setup": "Pronto",
                    "discord_banco_de_dados.temp.canal_torneio_id": canal.id,
                    "discord_banco_de_dados.temp.cargo_staff_id": cargo_staff.id
                }
            }

            try:
                result = await self.cog.bot.db["aprovações"].update_one(filtro, atualizacao)
                if result.matched_count == 0:
                    await interaction.followup.send("❌ Erro: Servidor não encontrado no banco. Peça para o bot reentrar.", ephemeral=True)
                    return

                await interaction.followup.send(f"⚙️ Configuração salva! Canal: {canal.mention} | Staff: {cargo_staff.mention}", ephemeral=True)
            except Exception as e:
                print(f"❌ [FUNCIONÁRIO] Erro ao atualizar: {e}")
                await interaction.followup.send("❌ Erro ao salvar no banco.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Torneios(bot))
    bot.tree.add_command(Torneios(bot).SetupGroup(Torneios(bot)))
