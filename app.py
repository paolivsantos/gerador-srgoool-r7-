# --- GERAÇÃO DO HTML FINAL PARA O SERVIDOR ---
menu_lateral_html = ""
conteudo_paineis_html = ""
dados_controle_json = {}
total_geral_iframes = 0

# Descobre qual deve ser o ativo com base na sua última atualização/criação
campeonato_ativo_padrao = st.session_state.get("ultimo_campeonato_ativo")
chaves_campeonatos = list(st.session_state["campeonatos_dados"].keys())

if not campeonato_ativo_padrao and chaves_campeonatos:
    campeonato_ativo_padrao = chaves_campeonatos[-1]

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

        # Define se este é o campeonato ativo com base no último atualizado
        is_active_camp = (c_nome == campeonato_ativo_padrao)
        active_menu_class = "active" if is_active_camp else ""
        active_panel_class = "active" if is_active_camp else ""

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
