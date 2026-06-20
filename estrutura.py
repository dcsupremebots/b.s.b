import discord
from datetime import datetime

class GerenciadorEstrutura:
    def __init__(self, db):
        self.db = db

    async def criar_documento_inicial(self, guild: discord.Guild):
        """Cria o esqueleto do documentoaprovação assim que o bot entra no servidor"""
        print(f"📥 [ESTRUTURA] Criando esqueleto para o servidor: {guild.name}")
        
        owner = guild.owner if guild.owner else None
        owner_name = owner.name if owner else "Desconhecido"
        owner_id = owner.id if owner else 0

        # A estrutura exata do seu JSON
        documento_aprovacao = {
            "userdocumento": f"@{owner_name}||id:{owner_id}",
            "discord_banco_de_dados": {
                "temp": {
                    "status_setup": "Aguardando Configuração",
                    "canal_torneio_id": None,
                    "cargo_staff_id": None
                },
                "fixo_ate_tirar": {
                    "servidor_id": guild.id,
                    "nome_servidor": guild.name,
                    "jogadores_inscritos": []
                },
                "fixo": {
                    "data_entrada": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                    "sistema_ativo": True
                }
            }
        }

        try:
            # Evita duplicar se o bot já tiver registro
            filtro = {"discord_banco_de_dados.fixo_ate_tirar.servidor_id": guild.id}
            existente = await self.db["aprovações"].find_one(filtro)
            
            if not existente:
                await self.db["aprovações"].insert_one(documento_aprovacao)
                print(f"✅ [ESTRUTURA] Banco de dados de '{guild.name}' inicializado.")
            else:
                print(f"ℹ️ [ESTRUTURA] Servidor '{guild.name}' já possui registro.")
        except Exception as e:
            print(f"❌ [ESTRUTURA] Erro ao inicializar banco: {e}")
