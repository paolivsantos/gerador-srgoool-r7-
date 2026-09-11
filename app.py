import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="Gerador de Iframes - Lance a Lance",
    page_icon="⚽",
    layout="wide",
)

st.title("⚽ Gerador de Iframes - Lance a Lance (R7)")
st.markdown(
    "Ferramenta para a redação gerar e organizar os códigos de lance a lance para inserção nos artigos."
)

# Categorias principais solicitadas
categorias = [
    "Brasileirão",
    "Paulistão",
    "Paulistão F",
    "Brasileirão Feminino",
    "Copa do Mundo",
    "Libertadores da América",
    "Copa Sulamericana",
    "Outras Competições",
]

# Seleção da categoria principal
categoria_selecionada = st.selectbox(
    "Selecione a Competição Principal:", categorias
)

st.divider()

# Simulando a estrutura de abas/grupos (ex: Rodadas ou Fases)
st.subheader(f"Organização: {categoria_selecionada}")

# Abas de segundo nível (ex: Rodadas / Grupos / Fases)
sub_abas = st.tabs(
    ["Rodada 1", "Rodada 2", "Rodada 3", "Mata-Mata / Outros"]
)

# Estrutura para armazenar ou renderizar os itens por sub-aba
# Em um cenário real, você pode persistir isso em JSON ou banco. Aqui faremos dinâmico na sessão.
if "dados_iframes" not in st.session_state:
    st.session_state["dados_iframes"] = {}

# Exemplo interativo dentro da primeira aba (Rodada 1)
with sub_abas[0]:
    st.markdown("### Configurar Iframes da Rodada 1")

    col1, col2 = st.columns(2)
    with col1:
        nome_jogo = st.text_input(
            "Identificação do Jogo (Ex: Corinthians x Palmeiras)",
            key=f"nome_{categoria_selecionada}_r1",
        )
    with col2:
        key_srgoool = st.text_input(
            "Chave (Key) do Sr. Goool (Ex: MC4...)",
            key=f"key_{categoria_selecionada}_r1",
        )

    if st.button("Adicionar Jogo à Rodada 1", key=f"btn_{categoria_selecionada}_r1"):
        if nome_jogo and key_srgoool:
            chave_dict = f"{categoria_selecionada}_Rodada 1"
            if chave_dict not in st.session_state["dados_iframes"]:
                st.session_state["dados_iframes"][chave_dict] = []
            st.session_state["dados_iframes"][chave_dict].append(
                {"nome": nome_jogo, "key": key_srgoool}
            )
            st.success(f"Jogo '{nome_jogo}' adicionado com sucesso!")
        else:
            st.warning("Preencha o nome do jogo e a chave.")

    # Exibir itens adicionados nesta seção
    chave_dict = f"{categoria_selecionada}_Rodada 1"
    if (
        chave_dict in st.session_state
        and st.session_state["dados_iframes"][chave_dict]
    ):
        st.markdown("#### Jogos Cadastrados nesta Seção:")
        for i, item in enumerate(
            st.session_state["dados_iframes"][chave_dict]
        ):
            # Monta o HTML padrão solicitado
            html_gerado = f"""<div style="display: flex">
         <div id="iframe_container_{i}" style="width: 100%; max-height: 100%; height: 2000px"> </div>
         <script src="https://www.srgoool.com.br/iframe.js.php?id=iframe_container_{i}&key={item['key']}"></script>
      </div>"""

            with st.expander(f"📌 {item['nome']}"):
                st.code(html_gerado, language="html")
                st.markdown("**Pré-visualização do Código:**")
                st.markdown(html_gerado, unsafe_allow_html=True)

with sub_abas[1]:
    st.markdown("### Configurar Iframes da Rodada 2")
    st.info("Estrutura similar replicável para as demais rodadas/sub-abas.")

with sub_abas[2]:
    st.markdown("### Configurar Iframes da Rodada 3")

with sub_abas[3]:
    st.markdown("### Configurar Fases Finais / Mata-Mata")

st.divider()

# Seção de Exportação do HTML Final para o Servidor
st.header("📤 Exportar Página HTML")
st.markdown(
    "Gere o arquivo HTML final consolidado para fazer o upload direto no servidor do portal."
)

if st.button("Gerar Código HTML Final da Página"):
    # Exemplo de HTML estruturado consolidado
    html_final_exemplo = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lance a Lance - {categoria_selecionada}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f4f4f4; }}
        .match-container {{ margin-bottom: 30px; background: #fff; padding: 15px; border-radius: 8px; }}
    </style>
</head>
<body>
    <h1>Cobertura: {categoria_selecionada}</h1>
    <!-- Os blocos gerados entram aqui -->
    <div style="display: flex">
         <div id="iframe_container" style="width: 100%; max-height: 100%; height: 2000px"> </div>
         <script src="https://www.srgoool.com.br/iframe.js.php?id=iframe_container&key=SUA_CHAVE_AQUI"></script>
    </div>
</body>
</html>"""

    st.text_area(
        "Copie o HTML completo abaixo ou baixe o arquivo:",
        html_final_exemplo,
        height=250,
    )
    st.download_button(
        label="Baixar index.html",
        data=html_final_exemplo,
        file_name="index.html",
        mime="text/html",
    )
