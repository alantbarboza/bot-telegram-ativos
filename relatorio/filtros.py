from json import load, dump
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USUARIOS_PATH = os.path.join(BASE_DIR, "usuarios.json")

def carregar_usuarios():
    with open(
        USUARIOS_PATH,
        "r",
        encoding="utf-8"
    ) as arquivo:
        return load(arquivo)
    
def usuario_cadastrado(user_id):
    usuarios = carregar_usuarios()

    return str(user_id) in usuarios

def obter_nome_usuario(chat_id):
    usuarios = carregar_usuarios()
    
    return usuarios.get(str(chat_id), {}).get("nome", str(chat_id))

def obter_proxima_execucao(user_id):
    usuarios = carregar_usuarios()

    return usuarios[str(user_id)].get("proxima_execucao")

def salvar_proxima_execucao(user_id, data):
    usuarios = carregar_usuarios()

    usuarios[str(user_id)]["proxima_execucao"] = data.isoformat()

    with open(
        USUARIOS_PATH,
        "w",
        encoding="utf-8"
    ) as arquivo:

        dump(
            usuarios,
            arquivo,
            ensure_ascii=False,
            indent=4
        )

def obter_ativos(user_id):
    usuarios = carregar_usuarios()

    return usuarios[str(user_id)].get("ativos", [])
