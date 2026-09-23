import base64
import json
import requests
import streamlit as st

# Configuração da página
st.set_page_config(page_title="Gerador Lance a Lance - R7", layout="wide")

# ==========================================
# CONFIGURAÇÕES DO REPOSITÓRIO
# ==========================================
GITHUB_REPO = "paolivsantos/gerador-srgoool-r7-"
GITHUB_BRANCH = "main"

def verificar_secrets():
    """Garante que o token está configurado de forma segura nos Secrets."""
    if "GITHUB_TOKEN" not in st.secrets:
        st.error("⚠️ Erro de configuração: O GITHUB_TOKEN não foi encontrado nos Secrets do Streamlit Cloud.")
        st.stop()

# ==========================================
# FUNÇÕES DE PERSISTÊNCIA (GITHUB API)
# ==========================================
@st.cache_data(ttl=5)
def carregar_do_github():
    verificar_secrets()
    try:
        token = st.secrets["GITHUB_TOKEN"]
        url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/estrutura_lance_a_lance.json?ref={GITHUB_BRANCH}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        }
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            file_content = response.json().get("content", "")
            decoded_bytes = base64.b64decode(file_content)
            data = json.loads(decoded_bytes.decode("utf-8"))
            if data:
                return data
    except Exception as e:
        st.warning(f"Não foi possível carregar os dados do GitHub: {e}")
    
    return {}

def salvar_no_github(dados):
    verificar_secrets()
    try:
        token = st.secrets["GITHUB_TOKEN"]
        url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/estrutura_lance_a_lance.json"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        }
        
        # Obter o SHA atual do arquivo (obrigatório para atualizações na API do GitHub)
        get_resp = requests.get(url, headers=headers, params={"ref": GITHUB_BRANCH})
        sha = get_resp.json().get("sha") if get_resp.status_code == 200 else None
            
        # Converter dados para JSON formatado em Base64
        json_str = json.dumps(dados, indent=4, ensure_ascii=False)
        content_encoded = base64.b64encode(json_str.encode("utf-8")).decode("utf-8")
        
        payload = {
            "message": "Atualização automática de dados via painel Streamlit",
            "content": content_encoded,
            "branch": GITHUB_BRANCH
        }
        if sha:
            payload["sha"] = sha
            
        put_resp = requests.put(url, headers=headers, json=payload)
        
        if put_resp.status_code in [200, 201]:
            st.success("Dados salvos e sincronizados com o GitHub com sucesso!")
            return True
        else:
            st.error(f"Erro ao atualizar no GitHub (Status {put_resp.status_code}): {put_resp.text}")
            return False
            
    except Exception as e:
        st.error(f"Erro crítico na conexão com o GitHub: {e}")
        return False

# ==========================================
# INICIALIZAÇÃO DO ESTADO DA APLICAÇÃO
# ==========================================
if "dados" not in st.session_state:
    st.session_state.dados = carregar_do_github()

# ==========================================
# INTERFACE DO PAINEL
# ==========================================
st.title("⚽ Gerador Lance a Lance - R7")
st.write("Painel integrado diretamente com o repositório do GitHub.")

# Exemplo de área de visualização/edição rápida dos dados atuais
with st.expander("Ver JSON Atual em Memória"):
    st.json(st.session_state.dados)

# Botão para disparar a gravação no GitHub
if st.button("💾 Salvar Alterações no GitHub"):
    sucesso = salvar_no_github(st.session_state.dados)
    if sucesso:
        st.balloons()
