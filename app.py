import re
import streamlit as str_lit

# Configuração da página
str_lit.set_page_config(
    page_title="Gerador de Iframes - Lance a Lance",
    page_icon="⚽",
    layout="wide",
)

str_lit.title("⚽ Gerador e Organizador de Iframes - Lance a Lance (R7)")
str_lit.markdown(
    "Faça o upload do arquivo de texto para extrair os códigos e disponibilizar a cópia rápida para a redação."
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

col_cat1, col_cat2 = str_lit.columns([1, 2])
with col_cat1:
    categoria_selecionada = str_lit.selectbox(
        "Competição Principal:", categorias
    )

# Inicializar o estado da sessão para armazenar as sub-abas e seus jogos
if "sub_abas_dados" not in str_lit.session_state:
    str_lit.session_state["sub_abas_dados"] = {}

if categoria_selecionada not in str_lit.session_state["sub_abas_dados"]:
    str_lit.session_state["sub_abas_dados"][categoria_selecionada] = {}

str_lit.divider()

# Gestão de Sub-Abas (Ex: Rodada 1, Rodada 2, 27ª Rodada, etc.)
str_lit.subheader("Gerenciar Sub-Abas (Rodadas / Fases)")

col_add1, col_add2 = str_lit.columns([2, 1])
with col_add1:
    nova_sub_aba = str_lit.text_input(
        "Nome da nova sub-aba (ex: 27ª Rodada, Quartas de Final):",
        placeholder="Digite o nome...",
    )
with col_add2:
    str_lit.markdown("###")  # Alinhamento visual
    if str_lit.button("➕ Adicionar Sub-Aba"):
        if nova_sub_aba:
            if (
                nova_sub_aba
                not in str_lit.session_state["sub_abas_dados"][categoria_selecionada]
            ):
                str_lit.session_state["sub_abas_dados"][categoria_selecionada][
                    nova_sub_aba
                ] = []
                str_lit.success(f"Sub-aba '{nova_sub_aba}' criada com sucesso!")
            else:
                str_lit.warning("Esta sub-aba já existe.")
        else:
            str_lit.error("Digite um nome válido para a sub-aba.")

# Obter as sub-abas cadastradas para a categoria atual
sub_abas_existentes = list(
    str_lit.session_state["sub_abas_dados"][categoria_selecionada].keys()
)

if not sub_abas_existentes:
    str_lit.info(
        "Nenhuma sub-aba criada ainda para esta categoria. Adicione uma acima para começar."
    )
else:
    str_lit.divider()
    # Renderiza as abas dinamicamente
    abas_interface = str_lit.tabs(sub_abas_existentes)

    for idx, sub_aba_nome in enumerate(sub_abas_existentes):
        with abas_interface[idx]:
            str_lit.markdown(f"### Conteúdo da Sub-Aba: {sub_aba_nome}")

            # Área de Upload do .txt
            uploaded_file = str_lit.file_uploader(
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
                        if novo_item not in str_lit.session_state["sub_abas_dados"][categoria_selecionada][sub_aba_nome]:
                            str_lit.session_state["sub_abas_dados"][categoria_selecionada][sub_aba_nome].append(novo_item)
                    
                    str_lit.success(f"{len(keys)} jogos importados com sucesso do arquivo .txt!")
                else:
                    str_lit.error("Não foi possível extrair os dados automaticamente. Verifique o formato do arquivo.")

            # Botão para limpar itens desta sub-aba
            if str_lit.session_state["sub_abas_dados"][categoria_selecionada][sub_aba_nome]:
                if str_lit.button("🗑️ Limpar jogos desta sub-aba", key=f"clear_{sub_aba_nome}"):
                    str_lit.session_state["sub_abas_dados"][categoria_selecionada][sub_aba_nome] = []
                    str_lit.rerun()

            str_lit.markdown("---")
            str_lit.markdown("#### Códigos dos Jogos para Cópia Individual:")
            
            jogos_atuais = str_lit.session_state["sub_abas_dados"][categoria_selecionada][sub_aba_nome]
            
            if not jogos_atuais:
                str_lit.info("Nenhum jogo cadastrado nesta sub-aba ainda. Faça o upload de um arquivo .txt acima.")
            else:
                html_gerado_completo = ""
                
                for i, jogo in enumerate(jogos_atuais):
                    id_container = f"iframe_container_{i}"
                    
                    # Bloco limpo idêntico ao formato padrão que a redação insere nos artigos
                    bloco_html = f"""<!-- {jogo.get('comentario_original', jogo['nome'])} -->
<div style="display: flex">
    <div id="{id_container}" style="width: 100%; max-height: 100%; height: 90vh"> </div>
    <script src="https://www.srgoool.com.br/iframe.js.php?id={id_container}&key={jogo['key']}"></script>
</div>\n\n"""
                    
                    html_gerado_completo += bloco_html

                    # Exibe o título do jogo e o bloco de código com o botão de cópia nativo do Streamlit
                    str_lit.markdown(f"**⚽ {jogo['nome']}**")
                    str_lit.code(bloco_html, language="html")

                str_lit.divider()
                str_lit.subheader("📋 Copiar Todos os Jogos da Sub-Aba")
                str_lit.markdown("Caso queira copiar a rodada inteira de uma só vez:")
                str_lit.code(html_gerado_completo, language="html")
