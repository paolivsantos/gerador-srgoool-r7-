import json
import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="Gerenciador de Campeonatos - R7", page_icon="⚽", layout="wide"
)

# Inicialização do session_state
if "campeonatos" not in st.session_state:
    st.session_state.campeonatos = {
        "Brasileirão 2026": {
            "Rodada 1": ["Flamengo x Vasco", "Palmeiras x Corinthians"],
            "Rodada 2": ["São Paulo x Santos", "Grêmio x Internacional"],
        }
    }

if "campeonato_selecionado" not in st.session_state:
    st.session_state.campeonato_selecionado = "Brasileirão 2026"

st.title("⚽ Gerenciador de Jogos e Campeonatos - R7")
st.markdown("---")

# Sidebar para gerenciamento de campeonatos
st.sidebar.header("Configurações")
campeonatos_lista = list(st.session_state.campeonatos.keys())
st.session_state.campeonato_selecionado = st.sidebar.selectbox(
    "Campeonato Ativo", campeonatos_lista
)

camp_atual = st.session_state.campeonato_selecionado
rodadas_lista = list(st.session_state.campeonatos[camp_atual].keys())

# Bloco principal de gerenciamento de rodadas
st.subheader("Gerenciar Rodadas")

# Selectbox puro (impede digitação livre por padrão no Streamlit)
rodada_selecionada = st.selectbox(
    "Selecione a Rodada para gerenciar os jogos/TXT:", options=rodadas_lista
)

# Campo para renomear a rodada com label em negrito
novo_nome_rodada = st.text_input(
    "**Renomear rodada:**", value=rodada_selecionada
)

col1, col2 = st.columns(2)
with col1:
    if st.button("Atualizar Nome da Rodada"):
        if (
            novo_nome_rodada
            and novo_nome_rodada
            != st.session_state.campeonatos[camp_atual][rodada_selecionada]
        ):
            jogos = st.session_state.campeonatos[camp_atual].pop(
                rodada_selecionada
            )
            st.session_state.campeonatos[camp_atual][novo_nome_rodada] = jogos
            st.success(
                f"Rodada renomeada com sucesso para '{novo_nome_rodada}'!"
            )
            st.rerun()

st.markdown("---")
st.subheader(f"Jogos da {rodada_selecionada}")

# Exibição e edição dos jogos da rodada selecionada
jogos_atuais = st.session_state.campeonatos[camp_atual][rodada_selecionada]
jogos_texto = "\n".join(jogos_atuais)

novos_jogos_texto = st.text_area(
    "Edite os jogos (um por linha):", value=jogos_texto, height=150
)

if st.button("Salvar Jogos"):
    lista_atualizada = [
        j.strip() for j in novos_jogos_texto.split("\n") if j.strip()
    ]
    st.session_state.campeonatos[camp_atual][
        rodada_selecionada
    ] = lista_atualizada
    st.success("Jogos atualizados com sucesso!")

st.markdown("---")

# Visualização do JSON / Exportação TXT para o Portal R7
st.subheader("Exportação de Dados (TXT / JSON)")
json_str = json.dumps(
    st.session_state.campeonatos[camp_atual], indent=4, ensure_ascii=False
)
st.download_button(
    label="Baixar TXT para o R7",
    data=json_str,
    file_name=f"{camp_atual.lower().replace(' ', '_')}.txt",
    mime="text/plain",
)
