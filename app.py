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

# --- CRIAR CAMPEONATO ---
st.subheader("🏆 Criar Campeonato")

col_c1, col_c2 = st.columns([3, 1], vertical_alignment="bottom")
with col_c1:
    novo_camp_nome = st.text_input("Novo campeonato:", placeholder="Ex: Brasileirão 2026", key="input_novo_camp")
with col_c2:
    if st.button("➕ Adicionar Campeonato", use_container_width=True):
        nome_limpo = novo_camp_nome.strip()
        if nome_limpo:
            if nome_limpo not in st.session_state["campeonatos_dados"]:
                st.session_state["campeonatos_dados"][nome_limpo] = {}
                st.session_state["campeonatos_visibilidade"][nome_limpo] = True
                st.session_state["input_novo_camp"] = ""
                st.success(f"Campeonato '{nome_limpo}' criado com sucesso!")
                st.rerun()
            else:
                st.warning("Este campeonato já existe.")
        else:
            st.error("Digite um nome válido.")

campeonatos_cadastrados = list(st.session_state["campeonatos_dados"].keys())

if not campeonatos_cadastrados:
    st.info("Nenhum campeonato cadastrado ainda. Adicione um acima ou importe um JSON na barra lateral.")
else:
    st.divider()
    st.subheader("⚙️ Painel de Edição e Organização")

    camp_selecionado = st.selectbox(
        "Selecione o Campeonato para gerenciar:",
        campeonatos_cadastrados,
        key="select_gerenciar_campeonato"
    )

    if camp_selecionado:
        idx_camp = campeonatos_cadastrados.index(camp_selecionado)
        
        with st.expander(f"🛠️ Configurações e Ajustes de '{camp_selecionado}'", expanded=False):
            col_A, col_B, col_C = st.columns([2, 1, 1], vertical_alignment="bottom")
            
            with col_A:
                rename_camp = st.text_input("Renomear campeonato:", value=camp_selecionado, key=f"txt_ren_{camp_selecionado}")
                if rename_camp.strip() and rename_camp.strip() != camp_selecionado:
                    novo_n = rename_camp.strip()
                    if novo_n not in st.session_state["campeonatos_dados"]:
                        novo_dict = {}
                        for k, v in st.session_state["campeonatos_dados"].items():
                            chave_f = novo_n if k == camp_selecionado else k
                            novo_dict[chave_f] = v
                        st.session_state["campeonatos_dados"] = novo_dict
                        vis_val = st.session_state["campeonatos_visibilidade"].pop(camp_selecionado, True)
                        st.session_state["campeonatos_visibilidade"][novo_n] = vis_val
                        st.success("Renomeado com sucesso!")
                        st.rerun()
                    else:
                        st.error("Já existe um campeonato com esse nome.")

            with col_B:
                st.write("Ordem:")
                col_sub_1, col_sub_2 = st.columns(2)
                with col_sub_1:
                    if idx_camp > 0 and st.button("⬆️", key=f"up_c_{camp_selecionado}", help="Subir campeonato", use_container_width=True):
                        chaves = list(st.session_state["campeonatos_dados"].keys())
                        chaves[idx_camp], chaves[idx_camp-1] = chaves[idx_camp-1], chaves[idx_camp]
                        st.session_state["campeonatos_dados"] = {k: st.session_state["campeonatos_dados"][k] for k in chaves}
                        st.rerun()
                with col_sub_2:
                    if idx_camp < len(campeonatos_cadastrados) - 1 and st.button("⬇️", key=f"down_c_{camp_selecionado}", help="Descer campeonato", use_container_width=True):
                        chaves = list(st.session_state["campeonatos_dados"].keys())
                        chaves[idx_camp], chaves[idx_camp+1] = chaves[idx_camp+1], chaves[idx_camp]
                        st.session_state["campeonatos_dados"] = {k: st.session_state["campeonatos_dados"][k] for k in chaves}
                        st.rerun()

            with col_C:
                st.write("Status:")
                atual_vis = st.session_state["campeonatos_visibilidade"].get(camp_selecionado, True)
                nova_vis = st.checkbox("Exibir no Site", value=atual_vis, key=f"chk_v_{camp_selecionado}")
                if nova_vis != atual_vis:
                    st.session_state["campeonatos_visibilidade"][camp_selecionado] = nova_vis
                    st.rerun()

            if st.button(f"❌ Excluir Campeonato '{camp_selecionado}'", key=f"del_c_{camp_selecionado}"):
                del st.session_state["campeonatos_dados"][camp_selecionado]
                if camp_selecionado in st.session_state["campeonatos_visibilidade"]:
                    del st.session_state["campeonatos_visibilidade"][camp_selecionado]
                st.rerun()

        st.markdown(f"#### Criar Rodadas / Fases de: **{camp_selecionado}**")

        col_r1, col_r2 = st.columns([3, 1], vertical_alignment="bottom")
        
        key_input_rodada = f"input_nova_rodada_{camp_selecionado}"
        if key_input_rodada not in st.session_state:
            st.session_state[key_input_rodada] = ""

        with col_r1:
            nova_rod_nome = st.text_input("Nova rodada/fase:", placeholder="Ex: Rodada 1 ou Quartas de Final", key=key_input_rodada)
        with col_r2:
            if st.button("➕ Adicionar Rodada", key=f"btn_add_rod_{camp_selecionado}", use_container_width=True):
                r_nome = nova_rod_nome.strip()
                if r_nome:
                    if r_nome not in st.session_state["campeonatos_dados"][camp_selecionado]:
                        st.session_state["campeonatos_dados"][camp_selecionado][r_nome] = []
                        # Limpa o input removendo a chave do session_state antes do próximo rerun
                        del st.session_state[key_input_rodada]
                        st.success(f"Rodada '{r_nome}' adicionada!")
                        st.rerun()
                    else:
                        st.warning("Esta rodada já existe neste campeonato.")
                else:
                    st.error("Digite um nome válido.")

        rodadas_existentes = list(st.session_state["campeonatos_dados"][camp_selecionado].keys())

        if rodadas_existentes:
            st.markdown("---")
            rodada_selecionada = st.selectbox(
                "Selecione a Rodada para gerenciar os jogos/TXT:",
                rodadas_existentes,
                key=f"select_rodada_{camp_selecionado}"
            )

            if rodada_selecionada:
                idx_rod = rodadas_existentes.index(rodada_selecionada)
                jogos_atuais = st.session_state["campeonatos_dados"][camp_selecionado][rodada_selecionada]

                col_rd_A, col_rd_B, col_rd_C = st.columns([2, 1, 1], vertical_alignment="bottom")
                with col_rd_A:
                    rename_rod = st.text_input("Renomear rodada:", value=rodada_selecionada, key=f"txt_ren_rod_{camp_selecionado}_{rodada_selecionada}")
                    if rename_rod.strip() and rename_rod.strip() != rodada_selecionada:
                        novo_nome_r = rename_rod.strip()
                        if novo_nome_r not in st.session_state["campeonatos_dados"][camp_selecionado]:
                            novo_d_rod = {}
                            for r_k, r_v in st.session_state["campeonatos_dados"][camp_selecionado].items():
                                chave_final_r = novo_nome_r if r_k == rodada_selecionada else r_k
                                novo_d_rod[chave_final_r] = r_v
                            st.session_state["campeonatos_dados"][camp_selecionado] = novo_d_rod
                            st.success("Rodada renomeada!")
                            st.rerun()
                        else:
                            st.error("Já existe uma rodada com esse nome.")

                with col_rd_B:
                    st.write("Ordem da Rodada:")
                    c_sub_r1, c_sub_r2 = st.columns(2)
                    with c_sub_r1:
                        if idx_rod > 0 and st.button("⬆️", key=f"up_r_{camp_selecionado}_{rodada_selecionada}", help="Subir rodada", use_container_width=True):
                            chaves_r = list(st.session_state["campeonatos_dados"][camp_selecionado].keys())
                            chaves_r[idx_rod], chaves_r[idx_rod-1] = chaves_r[idx_rod-1], chaves_r[idx_rod]
                            st.session_state["campeonatos_dados"][camp_selecionado] = {k: st.session_state["campeonatos_dados"][camp_selecionado][k] for k in chaves_r}
                            st.rerun()
                    with c_sub_r2:
                        if idx_rod < len(rodadas_existentes) - 1 and st.button("⬇️", key=f"down_r_{camp_selecionado}_{rodada_selecionada}", help="Descer rodada", use_container_width=True):
                            chaves_r = list(st.session_state["campeonatos_dados"][camp_selecionado].keys())
                            chaves_r[idx_rod], chaves_r[idx_rod+1] = chaves_r[idx_rod+1], chaves_r[idx_rod]
                            st.session_state["campeonatos_dados"][camp_selecionado] = {k: st.session_state["campeonatos_dados"][camp_selecionado][k] for k in chaves_r}
                            st.rerun()

                with col_rd_C:
                    st.write("Ação:")
                    if st.button(f"🗑️ Excluir Rodada", key=f"del_r_{camp_selecionado}_{rodada_selecionada}", use_container_width=True):
                        del st.session_state["campeonatos_dados"][camp_selecionado][rodada_selecionada]
                        st.rerun()

                uploaded_file = st.file_uploader(
                    f"📁 Enviar arquivo .txt para '{rodada_selecionada}'",
                    type=["txt"],
                    key=f"uploader_file_{camp_selecionado}_{rodada_selecionada}"
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
                        
                        st.session_state["campeonatos_dados"][camp_selecionado][rodada_selecionada] = novos_jogos
                        st.success(f"{len(keys)} jogos importados com sucesso para {rodada_selecionada}!")
                        st.rerun()
                    else:
                        st.error("Não foi possível extrair dados do .txt. Verifique o formato.")

                if jogos_atuais:
                    if st.button(f"🗑️ Limpar todos os jogos desta rodada", key=f"clear_rod_{camp_selecionado}_{rodada_selecionada}"):
                        st.session_state["campeonatos_dados"][camp_selecionado][rodada_selecionada] = []
                        st.rerun()

                    st.markdown(f"**Jogos cadastrados em {rodada_selecionada} ({len(jogos_atuais)}):**")
                    for jogo in jogos_atuais:
                        st.caption(f"⚽ {jogo['nome']}")

# --- GERAÇÃO DO HTML FINAL PARA O SERVIDOR ---
menu_lateral_html = ""
conteudo_paineis_html = ""
dados_controle_json = {}
total_geral_iframes = 0

for c_nome, r_dict in st.session_state["campeonatos_dados"].items():
    qtd_c = sum(len(j_list) for j_list in r_dict.values())
    total_geral_iframes += qtd_c
    dados_controle_json[c_nome] = qtd_c

    if st.session_state["campeonatos_visibilidade"].get(c_nome, True) and r_dict:
        safe_camp_id = re.sub(r'[^a-zA-Z0-9]', '_', c_nome).lower()
        
        opts_html_exp = ""
        blocos_html_exp = ""
        r_keys = list(r_dict.keys())
        for idx_r_exp, r_exp_name in enumerate(r_keys):
            j_exp_list = r_dict[r_exp_name]
            s_r_id = re.sub(r'[^a-zA-Z0-9]', '_', r_exp_name).lower()
            s_c_id = re.sub(r'[^a-zA-Z0-9]', '_', c_nome).lower()
            d_id = f"rodada_{s_c_id}_{s_r_id}"
            
            is_last_e = (idx_r_exp == len(r_keys) - 1)
            sel_att = "selected" if is_last_e else ""
            opts_html_exp += f'<option value="{d_id}" {sel_att}>{r_exp_name}</option>\n'
            
            disp_sty = "block" if is_last_e else "none"
            cards_exp_str = ""
            for i_e, j_e in enumerate(j_exp_list):
                id_cont_e = f"iframe_{c_nome}_{r_exp_name}_{i_e}".lower().replace(" ", "_")
                c_puro_e = f"""<!-- {j_e.get('comentario_original', j_e['nome'])} -->
<div style="display: flex">
    <div id="{id_cont_e}" style="width: 100%; max-height: 100%; height: 2000px"></div>
    <script src="https://www.srgoool.com.br/iframe.js.php?id={id_cont_e}&key={j_e['key']}"></script>
</div>"""
                c_esc_disp = html.escape(c_puro_e)
                c_esc_cop = html.escape(c_puro_e, quote=True)
                cards_exp_str += f"""
        <div class="match-card">
            <div class="code-box-wrapper">
                <pre><code>{c_esc_disp}</code></pre>
            </div>
            <button class="copy-btn" data-code="{c_esc_cop}" onclick="copiarTexto(this)">Copiar</button>
        </div>\n"""
            
            blocos_html_exp += f"""
    <div id="{d_id}" class="rodada-content-panel" style="display: {disp_sty};">
        <h2 class="round-title">{r_exp_name}</h2>
        {cards_exp_str}
    </div>\n"""

        is_first_camp = (menu_lateral_html == "")
        active_menu_class = "active" if is_first_camp else ""
        active_panel_class = "active" if is_first_camp else ""

        menu_lateral_html += f"""
        <button class="menu-item {active_menu_class}" onclick="mudarCampeonato(event, '{safe_camp_id}')">{c_nome}</button>"""

        conteudo_paineis_html += f"""
    <div id="{safe_camp_id}" class="championship-panel {active_panel_class}">
        <h1 class="page-title">{c_nome}</h1>
        <div class="round-selector-container">
            <label for="select_{safe_camp_id}" class="select-label">Selecione a Rodada / Fase:</label>
            <select id="select_{safe_camp_id}" class="round-select" onchange="mudarRodada(this, '{safe_camp_id}')">
                {opts_html_exp}
            </select>
        </div>
        <div class="rounds-container">
            {blocos_html_exp}
        </div>
    </div>\n"""

LIMITE_CONTRATO = 500
restantes_contrato = LIMITE_CONTRATO - total_geral_iframes

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
