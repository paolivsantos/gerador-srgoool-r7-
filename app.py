import re
import html
import streamlit as str_lit

# Configuração da página
str_lit.set_page_config(
    page_title="Gerador de Iframes - Lance a Lance",
    page_icon="⚽",
    layout="wide",
)

str_lit.title("⚽ Gerador e Organizador de Iframes - Lance a Lance (R7)")
str_lit.markdown(
    "Gerencie os dados por campeonato, crie sub-abas de rodadas e selecione quais competições entram na página final."
)

# Categorias principais
todas_categorias = [
    "Brasileirão",
    "Paulistão",
    "Paulistão F",
    "Brasileirão Feminino",
    "Copa do Mundo",
    "Libertadores da América",
    "Copa Sulamericana",
    "Outras Competições",
]

# Inicializar o estado da sessão para armazenar as sub-abas e seus jogos por categoria
if "sub_abas_dados" not in str_lit.session_state:
    str_lit.session_state["sub_abas_dados"] = {}

str_lit.divider()

# 1. Filtro de Campeonatos Visíveis (Ocultar/Exibir)
str_lit.subheader("⚙️ Configuração de Exibição da Página")
campeonatos_ativos = str_lit.multiselect(
    "Selecione os campeonatos que devem aparecer no portal:",
    options=todas_categorias,
    default=todas_categorias
)

str_lit.divider()

# 2. Seleção do Campeonato para Edição/Upload
str_lit.subheader("📁 Gerenciamento de Dados por Competição")
col_cat1, col_cat2 = str_lit.columns([1, 2])
with col_cat1:
    categoria_selecionada = str_lit.selectbox(
        "Selecione o campeonato para gerenciar os uploads:",
        todas_categorias
    )

if categoria_selecionada not in str_lit.session_state["sub_abas_dados"]:
    str_lit.session_state["sub_abas_dados"][categoria_selecionada] = {}

# Gestão de Sub-Abas para o campeonato selecionado
str_lit.markdown(f"#### Sub-abas para: **{categoria_selecionada}**")
col_add1, col_add2 = str_lit.columns([2, 1])
with col_add1:
    nova_sub_aba = str_lit.text_input(
        "Nome da nova sub-aba (ex: Rodada 1, Quartas de Final):",
        placeholder="Digite o nome...",
        key=f"input_{categoria_selecionada}"
    )
with col_add2:
    str_lit.markdown("###")
    if str_lit.button("➕ Adicionar Sub-Aba", key=f"btn_add_{categoria_selecionada}"):
        if nova_sub_aba:
            if nova_sub_aba not in str_lit.session_state["sub_abas_dados"][categoria_selecionada]:
                str_lit.session_state["sub_abas_dados"][categoria_selecionada][nova_sub_aba] = []
                str_lit.success(f"Sub-aba '{nova_sub_aba}' criada com sucesso!")
                str_lit.rerun()
            else:
                str_lit.warning("Esta sub-aba já existe.")
        else:
            str_lit.error("Digite um nome válido.")

# Obter sub-abas da categoria atual
sub_abas_existentes = list(str_lit.session_state["sub_abas_dados"][categoria_selecionada].keys())

if not sub_abas_existentes:
    str_lit.info(f"Nenhuma sub-aba criada para **{categoria_selecionada}**. Adicione uma acima.")
else:
    str_lit.divider()
    abas_interface = str_lit.tabs(sub_abas_existentes)

    for idx, sub_aba_nome in enumerate(sub_abas_existentes):
        with abas_interface[idx]:
            str_lit.markdown(f"### Conteúdo de {sub_aba_nome} ({categoria_selecionada})")

            uploaded_file = str_lit.file_uploader(
                f"Envie o arquivo .txt para '{sub_aba_nome}'",
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
                        if novo_item not in str_lit.session_state["sub_abas_dados"][categoria_selecionada][sub_aba_nome]:
                            str_lit.session_state["sub_abas_dados"][categoria_selecionada][sub_aba_nome].append(novo_item)
                    
                    str_lit.success(f"{len(keys)} jogos importados com sucesso!")
                else:
                    str_lit.error("Formato do arquivo .txt incompatível.")

            if str_lit.session_state["sub_abas_dados"][categoria_selecionada][sub_aba_nome]:
                if str_lit.button("🗑️ Limpar jogos desta sub-aba", key=f"clear_{categoria_selecionada}_{sub_aba_nome}"):
                    str_lit.session_state["sub_abas_dados"][categoria_selecionada][sub_aba_nome] = []
                    str_lit.rerun()

            jogos_atuais = str_lit.session_state["sub_abas_dados"][categoria_selecionada][sub_aba_nome]
            
            if jogos_atuais:
                str_lit.markdown("---")
                str_lit.markdown("#### Jogos cadastrados:")
                for i, jogo in enumerate(jogos_atuais):
                    id_container = f"iframe_{categoria_selecionada}_{sub_aba_nome}_{i}".lower().replace(" ", "_")
                    codigo_iframe_puro = f"""<!-- {jogo.get('comentario_original', jogo['nome'])} -->
<div style="display: flex">
    <div id="{id_container}" style="width: 100%; max-height: 100%; height: 2000px"></div>
    <script src="https://www.srgoool.com.br/iframe.js.php?id={id_container}&key={jogo['key']}"></script>
</div>"""
                    with str_lit.expander(f"⚽ {jogo['nome']}"):
                        str_lit.code(codigo_iframe_puro, language="html")

# 3. Geração do HTML Consolidado considerando os campeonatos ativos
str_lit.divider()
str_lit.subheader("📋 Código HTML Completo da Página para o Servidor")
str_lit.markdown("O código abaixo já reflete apenas os campeonatos selecionados na configuração de exibição superior.")

if not campeonatos_ativos:
    str_lit.warning("Nenhum campeonato selecionado para exibição.")
else:
    # Aqui você pode estruturar como prefere renderizar os blocos combinados no HTML final
    html_resumo_debug = f"<!-- Campeonatos ativos na página: {', '.join(campeonatos_ativos)} -->"
    str_lit.code(html_resumo_debug, language="html")
