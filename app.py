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
    "Gerencie campeonatos, reordene, renomeie, defina visibilidade, organize rodadas e exporte/importe via JSON."
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

# --- GERENCIAMENTO DE CAMPEONATOS ---
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
    st.markdown("##### Organizar, Renomear e Exibir Campeonatos:")

    for idx, camp in enumerate(campeonatos_cadastrados):
        if camp not in st.session_state["campeonatos_visibilidade"]:
            st.session_state["campeonatos_visibilidade"][camp] = True
            
        cols = st.columns([0.4, 0.4, 3.0, 0.8, 0.4])
        
        # Botão Subir na Ordem
        with cols[0]:
            if idx > 0:
                if st.button("⬆️", key=f"up_camp_{camp}", help="Mover para cima"):
                    chaves = list(st.session_state["campeonatos_dados"].keys())
                    chaves[idx], chaves[idx-1] = chaves[idx-1], chaves[idx]
                    st.session_state["campeonatos_dados"] = {k: st.session_state["campeonatos_dados"][k] for k in chaves}
                    st.rerun()
            else:
                st.markdown("")

        # Botão Descer na Ordem
        with cols[1]:
            if idx < len(campeonatos_cadastrados) - 1:
                if st.button("⬇️", key=f"down_camp_{camp}", help="Mover para baixo"):
                    chaves = list(st.session_state["campeonatos_dados"].keys())
                    chaves[idx], chaves[idx+1] = chaves[idx+1], chaves[idx]
                    st.session_state["campeonatos_dados"] = {k: st.session_state["campeonatos_dados"][k] for k in chaves}
                    st.rerun()
            else:
                st.markdown("")

        # Edição de Nome
        with cols[2]:
            novo_nome_input = st.text_input(f"Editar {camp}", value=camp, key=f"edit_name_{camp}", label_visibility="collapsed")
            if novo_nome_input.strip() and novo_nome_input.strip() != camp:
                novo_nome = novo_nome_input.strip()
                if novo_nome not in st.session_state["campeonatos_dados"]:
                    novo_dict = {}
                    for k, v in st.session_state["campeonatos_dados"].items():
                        chave_final = novo_nome if k == camp else k
                        novo_dict[chave_final] = v
                    st.session_state["campeonatos_dados"] = novo_dict
                    
                    vis_val = st.session_state["campeonatos_visibilidade"].pop(camp, True)
                    st.session_state["campeonatos_visibilidade"][novo_nome] = vis_val
                    st.rerun()
                else:
                    st.error("Já existe um campeonato com esse nome.")

        # Visibilidade
        with cols[3]:
            st.session_state["campeonatos_visibilidade"][camp] = st.checkbox(
                "Exibir",
                value=st.session_state["campeonatos_visibilidade"][camp],
                key=f"chk_vis_{camp}"
            )

        # Exclusão
        with cols[4]:
            if st.button("❌", key=f"del_camp_{camp}", help=f"Excluir {camp}"):
                del st.session_state["campeonatos_dados"][camp]
                if camp in st.session_state["campeonatos_visibilidade"]:
                    del st.session_state["campeonatos_visibilidade"][camp]
                st.rerun()

if not campeonatos_cadastrados:
    st.info("Nenhum campeonato cadastrado ainda. Adicione um acima ou importe um JSON na barra lateral.")
else:
    st.divider()
    
    campeonatos_cadastrados = list(st.session_state["campeonatos_dados"].keys())
    abas_campeonatos = st.tabs(campeonatos_cadastrados)

    menu_lateral_html = ""
    conteudo_paineis_html = ""
    dados_controle_json = {}
    total_geral_iframes = 0
    LIMITE_CONTRATO = 500

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

            options_select_html = ""
            blocos_rodadas_html = ""
            total_iframes_camp = 0

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
                            if st.button(f"🗑️ Limpar rodada", key=f"clear_{camp_nome}_{rodada_nome}"):
                                st.session_state["campeonatos_dados"][camp_nome][rodada_nome] = []
                                st.rerun()

                        jogos_rodada = st.session_state["campeonatos_dados"][camp_nome][rodada_nome]
                        total_iframes_camp += len(jogos_rodada)
                        
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
        </div>\n"""

                                with st.expander(f"⚽ {jogo['nome']}"):
                                    st.code(codigo_iframe_puro, language="html")

                            safe_rodada_id = re.sub(r'[^a-zA-Z0-9]', '_', rodada_nome).lower()
                            safe_camp_prefix = re.sub(r'[^a-zA-Z0-9]', '_', camp_nome).lower()
                            div_id = f"rodada_{safe_camp_prefix}_{safe_rodada_id}"

                            is_last_round = (idx_rod == len(rodadas_existentes) - 1)
                            selected_attr = "selected" if is_last_round else ""
                            options_select_html += f'<option value="{div_id}" {selected_attr}>{rodada_nome}</option>\n'

                            display_style = "block" if is_last_round else "none"

                            blocos_rodadas_html += f"""
    <div id="{div_id}" class="rodada-content-panel" style="display: {display_style};">
        <h2 class="round-title">{rodada_nome}</h2>
        {cards_html_rodada}
    </div>\n"""

            total_geral_iframes += total_iframes_camp
            dados_controle_json[camp_nome] = total_iframes_camp

            if blocos_rodadas_html and st.session_state["campeonatos_visibilidade"].get(camp_nome, True):
                safe_camp_id = re.sub(r'[^a-zA-Z0-9]', '_', camp_nome).lower()
                is_first_camp = (menu_lateral_html == "")
                active_menu_class = "active" if is_first_camp else ""
                active_panel_class = "active" if is_first_camp else ""

                menu_lateral_html += f"""
        <button class="menu-item {active_menu_class}" onclick="mudarCampeonato(event, '{safe_camp_id}')">{camp_nome}</button>"""

                conteudo_paineis_html += f"""
    <div id="{safe_camp_id}" class="championship-panel {active_panel_class}">
        <h1 class="page-title">{camp_nome}</h1>
        <div class="round-selector-container">
            <label for="select_{safe_camp_id}" class="select-label">Selecione a Rodada / Fase:</label>
            <select id="select_{safe_camp_id}" class="round-select" onchange="mudarRodada(this, '{safe_camp_id}')">
                {options_select_html}
            </select>
        </div>
        <div class="rounds-container">
            {blocos_rodadas_html}
        </div>
    </div>\n"""

    # --- HTML DO PAINEL DE CONTROLE ---
    paineis_controle_linhas = ""
    for c_nome, qtd in dados_controle_json.items():
        porcentagem = min(round((qtd / LIMITE_CONTRATO) * 100, 1), 100) if LIMITE_CONTRATO > 0 else 0
        paineis_controle_linhas += f"""
        <div class="control-item">
            <div class="control-info">
                <span class="control-camp-name">{c_nome}</span>
                <span class="control-camp-count">{qtd} iframes</span>
            </div>
            <div class="control-bar-bg">
                <div class="control-bar-fill" style="width: {porcentagem}%;"></div>
            </div>
        </div>\n"""

    if not paineis_controle_linhas:
        paineis_controle_linhas = '<p style="color: #777;">Nenhum dado de campeonato cadastrado ainda.</p>'

    restantes_contrato = LIMITE_CONTRATO - total_geral_iframes

    conteudo_paineis_html += f"""
    <div id="painel_controle" class="championship-panel">
        <h1 class="page-title">Controle de Contrato (Iframes)</h1>
        <div class="control-wrapper">
            <p class="control-desc">Acompanhe abaixo o consumo detalhado por campeonato em relação ao limite estipulado em contrato.</p>
            {paineis_controle_linhas}
            <div class="control-footer-summary">
                <span>Utilização Total do Contrato: <strong>{total_geral_iframes} / {LIMITE_CONTRATO}</strong></span>
            </div>
        </div>
    </div>\n"""

    menu_lateral_html += f"""
        <button class="menu-item menu-control-btn" onclick="mudarCampeonato(event, 'painel_controle')">📊 Controle de Contrato</button>"""

    st.divider()
    st.subheader("📋 Código HTML Completo da Página para o Servidor")

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
            position: relative;
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
        
        .header-counter-badge {{
            position: absolute;
            top: 15px;
            right: 20px;
            background-color: #0f1710;
            border: 1px solid #137d00;
            color: #ffffff;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: bold;
            box-shadow: 0 4px 10px rgba(0,0,0,0.6);
            z-index: 10;
            letter-spacing: 0.3px;
        }}
        .header-counter-badge span {{
            color: #4af626;
        }}

        .main-wrapper {{
            max-width: 1280px;
            margin: 30px auto;
            padding: 0 20px;
            display: flex;
            gap: 30px;
        }}
        
        .championship-sidebar {{
            width: 280px;
            flex-shrink: 0;
            background: #141414;
            border: 1px solid #222;
            border-radius: 8px;
            padding: 15px;
            height: fit-content;
            position: sticky;
            top: 20px;
        }}
        .sidebar-title {{
            font-size: 0.9rem;
            text-transform: uppercase;
            color: #888;
            margin: 0 0 12px 10px;
            letter-spacing: 0.5px;
        }}
        .menu-item {{
            display: block;
            width: 100%;
            background: transparent;
            color: #ccc;
            border: none;
            text-align: left;
            padding: 12px 15px;
            font-size: 0.95rem;
            font-weight: 600;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s;
            margin-bottom: 4px;
        }}
        .menu-item:hover {{
            background-color: rgba(19, 125, 0, 0.1);
            color: #ffffff;
        }}
        .menu-item.active {{
            background-color: #137d00;
            color: #ffffff;
        }}
        
        .menu-control-btn {{
            margin-top: 15px;
            border-top: 1px solid #222;
            padding-top: 15px;
            color: #4af626;
        }}
        .menu-control-btn.active {{
            background-color: #0d4205 !important;
            color: #ffffff !important;
        }}

        .content-area {{
            flex-grow: 1;
            min-width: 0;
        }}
        .championship-panel {{
            display: none;
        }}
        .championship-panel.active {{
            display: block;
        }}

        .page-title {{
            color: #137d00;
            font-size: 1.8rem;
            margin: 0 0 20px 0;
            text-transform: uppercase;
            letter-spacing: 1px;
            border-bottom: 2px solid #137d00;
            padding-bottom: 10px;
        }}

        .round-selector-container {{
            background: #141414;
            border: 1px solid #222;
            padding: 15px 20px;
            border-radius: 6px;
            margin-bottom: 25px;
            display: flex;
            align-items: center;
            gap: 15px;
        }}
        .select-label {{
            font-weight: bold;
            font-size: 0.95rem;
            color: #ccc;
        }}
        .round-select {{
            background-color: #0b0b0b;
            color: #ffffff;
            border: 1px solid #333;
            padding: 10px 15px;
            font-size: 1rem;
            border-radius: 4px;
            flex-grow: 1;
            cursor: pointer;
            outline: none;
        }}
        .round-select:focus {{
            border-color: #137d00;
        }}

        .round-title {{
            color: #ffffff;
            font-size: 1.3rem;
            margin: 20px 0 15px 0;
            text-transform: uppercase;
            border-left: 4px solid #137d00;
            padding-left: 10px;
        }}
        .match-card {{
            background: #141414;
            border: 1px solid #222;
            border-left: 5px solid #137d00;
            border-radius: 6px;
            margin-bottom: 20px;
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
            font-size: 0.82rem;
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

        .control-wrapper {{
            background: #141414;
            border: 1px solid #222;
            border-radius: 8px;
            padding: 25px;
        }}
        .control-desc {{
            color: #aaa;
            margin-top: 0;
            margin-bottom: 25px;
            font-size: 0.95rem;
        }}
        .control-item {{
            margin-bottom: 20px;
        }}
        .control-info {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            font-size: 0.95rem;
            font-weight: 600;
        }}
        .control-camp-name {{
            color: #fff;
            text-transform: uppercase;
        }}
        .control-camp-count {{
            color: #4af626;
        }}
        .control-bar-bg {{
            width: 100%;
            background-color: #0b0b0b;
            border: 1px solid #262626;
            height: 12px;
            border-radius: 6px;
            overflow: hidden;
        }}
        .control-bar-fill {{
            height: 100%;
            background-color: #137d00;
            border-radius: 6px;
            transition: width 0.4s ease;
        }}
        .control-footer-summary {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #222;
            text-align: right;
            font-size: 1.1rem;
            color: #fff;
        }}
        .control-footer-summary strong {{
            color: #4af626;
        }}

        @media (max-width: 900px) {{
            .main-wrapper {{
                flex-direction: column;
            }}
            .championship-sidebar {{
                width: 100%;
                position: static;
            }}
            .header-counter-badge {{
                top: 10px;
                right: 10px;
                font-size: 0.8rem;
                padding: 6px 12px;
            }}
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
        <div class="header-counter-badge">
            Scripts restantes: <span>{restantes_contrato}</span> / {LIMITE_CONTRATO}
        </div>
        <img src="https://cloudfront-us-east-1.images.arcpublishing.com/newr7/7XJNKPHSNRGB7K5DJFYFATVSKU.jpg" alt="Header R7" class="header-desktop">
        <img src="https://cloudfront-us-east-1.images.arcpublishing.com/newr7/7XJNKPHSNRGB7K5DJFYFATVSKU.jpg" alt="Header R7 Mobile" class="header-mobile">
    </header>

    <div class="main-wrapper">
        <nav class="championship-sidebar">
            <div class="sidebar-title">Campeonatos</div>
            {menu_lateral_html}
        </nav>

        <main class="content-area">
            {conteudo_paineis_html}
        </main>
    </div>

    <footer>
        <p>R7 Esportes • Sistema de Cobertura Lance a Lance</p>
    </footer>

    <script>
        function mudarCampeonato(evt, campId) {{
            const panels = document.getElementsByClassName("championship-panel");
            for (let i = 0; i < panels.length; i++) {{
                panels[i].classList.remove("active");
            }}
            
            const items = document.getElementsByClassName("menu-item");
            for (let i = 0; i < items.length; i++) {{
                items[i].classList.remove("active");
            }}
            
            document.getElementById(campId).classList.add("active");
            evt.currentTarget.classList.add("active");
        }}

        function mudarRodada(selectElement, campId) {{
            const selectedValue = selectElement.value;
            const panel = document.getElementById(campId);
            const rodadas = panel.getElementsByClassName("rodada-content-panel");
            
            for (let i = 0; i < rodadas.length; i++) {{
                rodadas[i].style.display = "none";
            }}
            
            const rodadaAlvo = document.getElementById(selectedValue);
            if (rodadaAlvo) {{
                rodadaAlvo.style.display = "block";
            }}
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
