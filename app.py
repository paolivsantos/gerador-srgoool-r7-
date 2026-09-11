import json
import re
import html
import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="Gerador de Iframes - Lance a Lance",
    page_icon="⚽",
    layout="wide",
)

st.title("⚽ Gerador e Organizador de Iframes - Lance a Lance (R7)")
st.markdown(
    "Gerencie campeonatos, defina quais ficam visíveis, organize rodadas e exporte/importe via JSON."
)

# Inicializar estados no session_state
if "campeonatos_dados" not in st.session_state:
    st.session_state["campeonatos_dados"] = {}

if "campeonatos_visibilidade" not in st.session_state:
    st.session_state["campeonatos_visibilidade"] = {}

# --- SIDEBAR: EXPORTAR E IMPORTAR JSON ---
st.sidebar.subheader("💾 Backup e Recuperação (JSON)")

if st.session_state["campeonatos_dados"]:
    json_str = json.dumps(st.session_state["campeonatos_dados"], ensure_ascii=False, indent=4)
    st.sidebar.download_button(
        label="📥 Exportar Estrutura (JSON)",
        data=json_str,
        file_name="estrutura_lance_a_lance.json",
        mime="application/json",
    )

st.sidebar.divider()
json_file = st.sidebar.file_uploader("Carregar arquivo JSON salvo", type=["json"], key="json_uploader")

if json_file is not None:
    if st.sidebar.button("🔄 Aplicar JSON Carregado"):
        try:
            dados_carregados = json.load(json_file)
            if isinstance(dados_carregados, dict):
                st.session_state["campeonatos_dados"] = dados_carregados
                for c in dados_carregados.keys():
                    if c not in st.session_state["campeonatos_visibilidade"]:
                        st.session_state["campeonatos_visibilidade"][c] = True
                st.sidebar.success("Dados carregados com sucesso!")
                st.rerun()
            else:
                st.sidebar.error("O arquivo JSON não possui o formato esperado.")
        except Exception as e:
            st.sidebar.error(f"Erro ao ler o arquivo JSON: {e}")

st.divider()

# --- 1 & 3. GERENCIAMENTO DE CAMPEONATOS ---
st.subheader("🏆 Gerenciar Campeonatos")

def adicionar_campeonato_callback():
    valor_digitado = st.session_state.get("input_camp_val", "").strip()
    if valor_digitado:
        if valor_digitado not in st.session_state["campeonatos_dados"]:
            st.session_state["campeonatos_dados"][valor_digitado] = {}
            st.session_state["campeonatos_visibilidade"][valor_digitado] = True
            st.session_state["input_camp_val"] = ""
            st.success(f"Campeonato '{valor_digitado}' criado com sucesso!")
        else:
            st.warning("Este campeonato já existe.")
    else:
        st.error("Digite um nome válido.")

col_c1, col_c2 = st.columns([3, 1], vertical_alignment="bottom")
with col_c1:
    st.text_input(
        "Nome do campeonato:",
        placeholder="",
        key="input_camp_val"
    )
with col_c2:
    st.button("➕ Adicionar Campeonato", on_click=adicionar_campeonato_callback, use_container_width=True)

campeonatos_cadastrados = list(st.session_state["campeonatos_dados"].keys())

if campeonatos_cadastrados:
    st.markdown("##### Campeonatos Cadastrados (Exibição e Exclusão):")
    for camp in campeonatos_cadastrados:
        if camp not in st.session_state["campeonatos_visibilidade"]:
            st.session_state["campeonatos_visibilidade"][camp] = True
            
        c_cols = [3, 0.4]
        cols = st.columns(c_cols)
        
        with cols[0]:
            st.session_state["campeonatos_visibilidade"][camp] = st.checkbox(
                f"Exibir **{camp}** na página final",
                value=st.session_state["campeonatos_visibilidade"][camp],
                key=f"chk_vis_{camp}"
            )
        with cols[1]:
            if st.button("❌", key=f"del_camp_{camp}", help=f"Excluir {camp}"):
                del st.session_state["campeonatos_dados"][camp]
                if camp in st.session_state["campeonatos_visibilidade"]:
                    del st.session_state["campeonatos_visibilidade"][camp]
                st.rerun()

if not campeonatos_cadastrados:
    st.info("Nenhum campeonato cadastrado ainda. Adicione um acima ou importe um JSON na barra lateral.")
else:
    st.divider()
    # --- 2. CADA CAMPEONATO CRIADO GERA UMA ABA ---
    abas_campeonatos = st.tabs(campeonatos_cadastrados)

    botoes_abas_html = ""
    conteudo_abas_html = ""

    for idx_camp, camp_nome in enumerate(campeonatos_cadastrados):
        with abas_campeonatos[idx_camp]:
            st.markdown(f"### Competição: **{camp_nome}**")
            st.markdown("#### Gerenciar Rodadas / Fases")

            def criar_callback_rodada(c_nome):
                key_input = f"input_rodada_{c_nome}"
                valor_rodada = st.session_state.get(key_input, "").strip()
                if valor_rodada:
                    if valor_rodada not in st.session_state["campeonatos_dados"][c_nome]:
                        st.session_state["campeonatos_dados"][c_nome][valor_rodada] = []
                        st.session_state[key_input] = ""
                        st.success(f"Rodada '{valor_rodada}' adicionada!")
                    else:
                        st.warning("Esta rodada já existe neste campeonato.")
                else:
                    st.error("Digite um nome válido para a rodada.")

            col_r1, col_r2 = st.columns([3, 1], vertical_alignment="bottom")
            with col_r1:
                st.text_input(
                    f"Nome da rodada/fase para {camp_nome}:",
                    placeholder="",
                    key=f"input_rodada_{camp_nome}"
                )
            with col_r2:
                st.button(
                    "➕ Adicionar Rodada", 
                    key=f"btn_add_rodada_{camp_nome}", 
                    on_click=criar_callback_rodada, 
                    args=(camp_nome,), 
                    use_container_width=True
                )

            rodadas_existentes = list(st.session_state["campeonatos_dados"][camp_nome].keys())

            cards_html_campeonato = ""

            if rodadas_existentes:
                st.divider()
                abas_rodadas = st.tabs(rodadas_existentes)

                for idx_rod, rodada_nome in enumerate(rodadas_existentes):
                    with abas_rodadas[idx_rod]:
                        st.markdown(f"##### Conteúdo da Rodada: {rodada_nome}")

                        if st.button(f"🗑️ Excluir Rodada '{rodada_nome}'", key=f"del_rod_{camp_nome}_{rodada_nome}"):
                            del st.session_state["campeonatos_dados"][camp_nome][rodada_nome]
                            st.rerun()

                        uploaded_file = st.file_uploader(
                            f"Envie o arquivo .txt para {camp_nome} - {rodada_nome}",
                            type=["txt"],
                            key=f"uploader_{camp_nome}_{rodada_nome}",
                        )

                        if uploaded_file is not None:
                            conteudo_txt = uploaded_file.read().decode("utf-8")
                            comentarios = re.findall(r"<!--(.*?)-->", conteudo_txt)
                            keys = re.findall(r"key=([A-Za-z0-9=_\-]+)", conteudo_txt)

                            if comentarios and keys:
                                novos_jogos = []
                                for c_comentario, c_key in zip(comentarios, keys):
                                    partes = c_comentario.split("-")
                                    nome_jogo = partes[-1].strip() if len(partes) > 0 else c_comentario.strip()
                                    novos_jogos.append({
                                        "nome": nome_jogo,
                                        "key": c_key,
                                        "comentario_original": c_comentario.strip()
                                    })
                                
                                st.session_state["campeonatos_dados"][camp_nome][rodada_nome] = novos_jogos
                                st.success(f"{len(keys)} jogos importados com sucesso para {rodada_nome}!")
                            else:
                                st.error("Não foi possível extrair dados do .txt. Verifique o formato.")

                        if st.session_state["campeonatos_dados"][camp_nome][rodada_nome]:
                            if st.button("🗑️ Limpar rodada", key=f"clear_{camp_nome}_{rodada_nome}"):
                                st.session_state["campeonatos_dados"][camp_nome][rodada_nome] = []
                                st.rerun()

                        jogos_rodada = st.session_state["campeonatos_dados"][camp_nome][rodada_nome]
                        
                        if jogos_rodada:
                            st.markdown("---")
                            cards_html_rodada = ""
                            for i, jogo in enumerate(jogos_rodada):
                                id_container = f"iframe_{camp_nome}_{rodada_nome}_{i}".lower().replace(" ", "_")
                                
                                codigo_iframe_puro = f"""<!-- {jogo.get('comentario_original', jogo['nome'])} -->
<div style="display: flex">
    <div id="{id_container}" style="width: 100%; max-height: 100%; height: 2000px"></div>
    <script src="https://www.srgoool.com.br/iframe.js.php?id={id_container}&key={jogo['key']}"></script>
</div>"""

                                codigo_escapado_exibicao = html.escape(codigo_iframe_puro)
                                codigo_escapado_copia = html.escape(codigo_iframe_puro, quote=True)

                                cards_html_rodada += f"""
    <div class="match-card">
        <div class="code-box-wrapper">
            <pre><code>{codigo_escapado_exibicao}</code></pre>
        </div>
        <button class="copy-btn" data-code="{codigo_escapado_copia}" onclick="copiarTexto(this)">Copiar</button>
    </div>\n\n"""

                                with st.expander(f"⚽ {jogo['nome']}"):
                                    st.code(codigo_iframe_puro, language="html")

                            cards_html_campeonato += f"""
    <div class="round-section" data-round="{rodada_nome}">
        <h2 class="round-title">{rodada_nome}</h2>
        {cards_html_rodada}
    </div>\n"""

            # --- CONSTRUÇÃO DAS ABAS NO FRONTEND HTML ---
            if cards_html_campeonato and st.session_state["campeonatos_visibilidade"].get(camp_nome, True):
                safe_id = re.sub(r'[^a-zA-Z0-9]', '_', camp_nome).lower()
                is_first = (botoes_abas_html == "")
                active_class_btn = "active" if is_first else ""
                active_class_content = "active" if is_first else ""

                botoes_abas_html += f"""
        <button class="tab-btn {active_class_btn}" onclick="mudarAba(event, '{safe_id}')">{camp_nome}</button>"""

                conteudo_abas_html += f"""
    <div id="{safe_id}" class="tab-content {active_class_content}">
        {cards_html_campeonato}
    </div>\n"""

    st.divider()
    st.subheader("📋 Código HTML Completo da Página para o Servidor")
    st.markdown("O código abaixo consolida os campeonatos organizados em abas para facilitar a navegação no portal:")

    html_pagina_completa = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lance a Lance - Cobertura Esportiva</title>
    
    <meta property="og:title" content="Lance a Lance - Cobertura Esportiva">
    <meta property="og:description" content="Central de cópias de iframes para os artigos de coberturas esportivas.">
    <meta property="og:image" content="https://cloudfront-us-east-1.images.arcpublishing.com/newr7/ZKWPEFW6KJA5BBMQXMQ2R3X6XA.jpg">
    <meta property="og:type" content="website">

    <style>
        * {{ box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: #0b0b0b;
            color: #ffffff;
            margin: 0;
            padding: 0;
        }}
        .header-container {{
            width: 100%;
            background-color: #000;
            text-align: center;
            border-bottom: 4px solid #137d00;
        }}
        .header-desktop {{
            width: 100%;
            max-height: 250px;
            object-fit: cover;
            display: block;
        }}
        .header-mobile {{
            display: none;
            width: 100%;
            object-fit: cover;
        }}
        @media (max-width: 768px) {{
            .header-desktop {{ display: none; }}
            .header-mobile {{ display: block; }}
        }}
        .container {{
            max-width: 1100px;
            margin: 0 auto;
            padding: 20px;
        }}
        /* Estilos das Abas de Campeonatos */
        .tabs-header {{
            display: flex;
            background-color: #141414;
            border-bottom: 2px solid #222;
            overflow-x: auto;
            margin-top: 25px;
            border-radius: 6px 6px 0 0;
        }}
        .tab-btn {{
            background-color: transparent;
            color: #888;
            border: none;
            padding: 14px 24px;
            font-size: 1rem;
            font-weight: bold;
            text-transform: uppercase;
            cursor: pointer;
            transition: all 0.2s ease;
            white-space: nowrap;
            border-bottom: 3px solid transparent;
        }}
        .tab-btn:hover {{
            color: #ffffff;
            background-color: rgba(19, 125, 0, 0.05);
        }}
        .tab-btn.active {{
            color: #ffffff;
            border-bottom: 3px solid #137d00;
            background-color: rgba(19, 125, 0, 0.1);
        }}
        .tab-content {{
            display: none;
            padding: 20px 0;
            animation: fadeIn 0.3s ease;
        }}
        .tab-content.active {{
            display: block;
        }}
        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}
        .round-title {{
            color: #ffffff;
            font-size: 1.4rem;
            margin: 25px 0 15px 0;
            text-transform: uppercase;
            border-left: 4px solid #137d00;
            padding-left: 10px;
        }}
        .match-card {{
            background: #141414;
            border: 1px solid #222;
            border-left: 5px solid #137d00;
            border-radius: 6px;
            margin-bottom: 25px;
            padding: 15px 20px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
        }}
        .code-box-wrapper {{
            background: #000;
            border: 1px solid #262626;
            border-radius: 4px;
            padding: 12px;
            margin-bottom: 12px;
            height: 183px;
            max-height: 183px;
            overflow-y: auto;
            overflow-x: auto;
        }}
        pre {{
            margin: 0;
        }}
        code {{
            font-family: Consolas, Monaco, "Andale Mono", monospace;
            color: #4af626;
            font-size: 0.85rem;
            white-space: pre-wrap;
            word-break: break-all;
        }}
        .copy-btn {{
            background-color: #137d00;
            color: #ffffff;
            border: none;
            padding: 8px 20px;
            font-size: 0.85rem;
            font-weight: bold;
            border-radius: 4px;
            cursor: pointer;
            transition: background 0.2s;
        }}
        .copy-btn:hover {{
            background-color: #0f6600;
        }}
        .copy-btn.copied {{
            background-color: #ffffff;
            color: #000000;
        }}
        footer {{
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 0.9rem;
            border-top: 1px solid #1a1a1a;
            margin-top: 40px;
        }}
    </style>
</head>
<body>

    <header class="header-container">
        <img src="https://cloudfront-us-east-1.images.arcpublishing.com/newr7/7XJNKPHSNRGB7K5DJFYFATVSKU.jpg" alt="Header R7" class="header-desktop">
        <img src="https://cloudfront-us-east-1.images.arcpublishing.com/newr7/7XJNKPHSNRGB7K5DJFYFATVSKU.jpg" alt="Header R7 Mobile" class="header-mobile">
    </header>

    <div class="container">
        <!-- Navegação por Abas -->
        <div class="tabs-header">
{botoes_abas_html}
        </div>

        <!-- Conteúdo das Abas -->
{conteudo_abas_html}
    </div>

    <footer>
        <p>R7 Esportes • Sistema de Cobertura Lance a Lance</p>
    </footer>

    <script>
        function mudarAba(evt, tabId) {{
            const contents = document.getElementsByClassName("tab-content");
            for (let i = 0; i < contents.length; i++) {{
                contents[i].classList.remove("active");
            }}
            
            const buttons = document.getElementsByClassName("tab-btn");
            for (let i = 0; i < buttons.length; i++) {{
                buttons[i].classList.remove("active");
            }}
            
            document.getElementById(tabId).classList.add("active");
            evt.currentTarget.classList.add("active");
        }}

        function copiarTexto(botao) {{
            const codigoCodificado = botao.getAttribute('data-code');
            
            const textareaTemp = document.createElement('textarea');
            textareaTemp.innerHTML = codigoCodificado;
            const textoParaCopiar = textareaTemp.value;
            
            const inputInvisivel = document.createElement('textarea');
            inputInvisivel.value = textoParaCopiar;
            document.body.appendChild(inputInvisivel);
            inputInvisivel.select();
            
            try {{
                document.execCommand('copy');
                const textoOriginal = botao.innerText;
                botao.innerText = "Copiado! ✔️";
                botao.classList.add("copied");
                
                setTimeout(() => {{
                    botao.innerText = textoOriginal;
                    botao.classList.remove("copied");
                }}, 2000);
            }} catch (err) {{
                console.error('Erro ao copiar: ', err);
                alert('Erro ao tentar copiar o código.');
            }}
            
            document.body.removeChild(inputInvisivel);
        }}
    </script>
</body>
</html>"""

    st.code(html_pagina_completa, language="html")
