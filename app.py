import re
import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="Gerador de Iframes - Lance a Lance",
    page_icon="⚽",
    layout="wide",
)

st.title("⚽ Gerador e Organizador de Iframes - Lance a Lance (R7)")
st.markdown(
    "Faça o upload do arquivo de texto da rodada para organizar e gerar os códigos limpos para a redação."
)

# Categorias principais
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

col_cat1, col_cat2 = st.columns([1, 2])
with col_cat1:
    categoria_selecionada = st.selectbox(
        "Competição Principal:", categorias
    )

# Inicializar o estado da sessão para armazenar as sub-abas e seus jogos
if "sub_abas_dados" not in st.session_state:
    st.session_state["sub_abas_dados"] = {}

if categoria_selecionada not in st.session_state["sub_abas_dados"]:
    st.session_state["sub_abas_dados"][categoria_selecionada] = {}

st.divider()

# Gestão de Sub-Abas (Ex: Rodada 1, Rodada 2, 27ª Rodada, etc.)
st.subheader("Gerenciar Sub-Abas (Rodadas / Fases)")

col_add1, col_add2 = st.columns([2, 1])
with col_add1:
    nova_sub_aba = st.text_input(
        "Nome da nova sub-aba (ex: 27ª Rodada, Quartas de Final):",
        placeholder="Digite o nome...",
    )
with col_add2:
    st.markdown("###")  # Alinhamento visual
    if st.button("➕ Adicionar Sub-Aba"):
        if nova_sub_aba:
            if (
                nova_sub_aba
                not in st.session_state["sub_abas_dados"][categoria_selecionada]
            ):
                st.session_state["sub_abas_dados"][categoria_selecionada][
                    nova_sub_aba
                ] = []
                st.success(f"Sub-aba '{nova_sub_aba}' criada com sucesso!")
            else:
                st.warning("Esta sub-aba já existe.")
        else:
            st.error("Digite um nome válido para a sub-aba.")

# Obter as sub-abas cadastradas para a categoria atual
sub_abas_existentes = list(
    st.session_state["sub_abas_dados"][categoria_selecionada].keys()
)

if not sub_abas_existentes:
    st.info(
        "Nenhuma sub-aba criada ainda para esta categoria. Adicione uma acima para começar."
    )
else:
    st.divider()
    # Renderiza as abas dinamicamente com a indentação corrigida
    abas_interface = st.tabs(sub_abas_existentes)

    for idx, sub_aba_nome in enumerate(sub_abas_existentes):
        with abas_interface[idx]:
            st.markdown(f"### Conteúdo da Sub-Aba: {sub_aba_nome}")

            # Área de Upload do .txt
            uploaded_file = st.file_uploader(
                f"Envie o arquivo .txt para preencher '{sub_aba_nome}'",
                type=["txt"],
                key=f"uploader_{categoria_selecionada}_{sub_aba_nome}",
            )

            if uploaded_file is not None:
                conteudo_txt = uploaded_file.read().decode("utf-8")

                comentarios = re.findall(r"<!--(.*?)-->", conteudo_txt)
                keys = re.findall(r"key=([A-Za-z0-9=_\-]+)", conteudo_txt)

                if comentarios and keys:
                    for c_comentario, c_key in zip(comentarios, keys):
                        partes = c_comentario.split("-")
                        nome_jogo = partes[-1].strip() if len(partes) > 0 else c_comentario.strip()
                        
                        novo_item = {"nome": nome_jogo, "key": c_key, "comentario_original": c_comentario.strip()}
                        if novo_item not in st.session_state["sub_abas_dados"][categoria_selecionada][sub_aba_nome]:
                            st.session_state["sub_abas_dados"][categoria_selecionada][sub_aba_nome].append(novo_item)
                    
                    st.success(f"{len(keys)} jogos importados com sucesso do arquivo .txt!")
                else:
                    st.error("Não foi possível extrair os dados automaticamente. Verifique o formato do arquivo.")

            # Botão para limpar itens desta sub-aba
            if st.session_state["sub_abas_dados"][categoria_selecionada][sub_aba_nome]:
                if st.button("🗑️ Limpar jogos desta sub-aba", key=f"clear_{sub_aba_nome}"):
                    st.session_state["sub_abas_dados"][categoria_selecionada][sub_aba_nome] = []
                    st.rerun()

            st.markdown("---")
            st.markdown("#### Jogos / Iframes Configurados:")
            
            jogos_atuais = st.session_state["sub_abas_dados"][categoria_selecionada][sub_aba_nome]
            
            if not jogos_atuais:
                st.info("Nenhum jogo cadastrado nesta sub-aba ainda. Faça o upload de um arquivo .txt acima.")
            else:
                html_gerado_completo = ""
                
                for i, jogo in enumerate(jogos_atuais):
                    id_container = f"iframe_container_{i}"
                    bloco_html = f"""<!-- {jogo.get('comentario_original', jogo['nome'])} -->
<div style="display: flex">
    <div id="{id_container}" style="width: 100%; max-height: 100%; height: 90vh"> </div>
    <script src="https://www.srgoool.com.br/iframe.js.php?id={id_container}&key={jogo['key']}"></script>
</div>\n\n"""
                    
                    html_gerado_completo += bloco_html

                    with st.expander(f"⚽ {jogo['nome']}"):
                        st.code(bloco_html, language="html")
                        st.markdown("**Visualização do Iframe:**")
                        st.markdown(bloco_html, unsafe_allow_html=True)

                st.divider()
                st.subheader("📤 Exportar HTML da Sub-Aba")
                st.text_area(
                    "Código HTML consolidado desta sub-aba para inserir no artigo ou servidor:",
                    value=html_gerado_completo,
                    height=200,
                    key=f"textarea_{sub_aba_nome}"
                )
                
                st.download_button(
                    label=f"Baixar HTML ({sub_aba_nome}.html)",
                    data=html_gerado_completo,
                    file_name=f"{categoria_selecionada.lower().replace(' ', '_')}_{sub_aba_nome.lower().replace(' ', '_')}.html",
                    mime="text/html",
                    key=f"download_{sub_aba_nome}"
                )
