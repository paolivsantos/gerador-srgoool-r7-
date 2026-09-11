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
    "Gerencie campeonatos e rodadas de forma dinâmica, faça uploads dos blocos e exporte/importe sua estrutura via JSON."
)

# Inicializar o estado da sessão para armazenar todos os dados
if "campeonatos_dados" not in st.session_state:
    st.session_state["campeonatos_dados"] = {}

# --- SIDEBAR: EXPORTAR E IMPORTAR JSON ---
st.sidebar.subheader("💾 Backup e Recuperação (JSON)")

# 6. Botão para exportar a estrutura em JSON
if st.session_state["campeonatos_dados"]:
    json_str = json.dumps(st.session_state["campeonatos_dados"], ensure_ascii=False, indent=4)
    st.sidebar.download_button(
        label="📥 Exportar Estrutura (JSON)",
        data=json_str,
        file_name="estrutura_lance_a_lance.json",
        mime="application/json",
    )

st.sidebar.divider()

# 7. Botão de upload do JSON na sidebar
json_file = st.sidebar.file_uploader("Carregar arquivo JSON salvo", type=["json"], key="json_uploader")

# 8. Botão carregar JSON
if json_file is not None:
    if st.sidebar.button("🔄 Aplicar JSON Carregado"):
        try:
            dados_carregados = json.load(json_file)
            if isinstance(dados_carregados, dict):
                st.session_state["campeonatos_dados"] = dados_carregados
                st.sidebar.success("Dados carregados com sucesso!")
                st.rerun()
            else:
                st.sidebar.error("O arquivo JSON não possui o formato esperado.")
        except Exception as e:
            st.sidebar.error(f"Erro ao ler o arquivo JSON: {e}")

st.divider()

# --- 1. CAMPO PARA ADICIONAR CAMPEONATOS LIVREMENTE ---
st.subheader("🏆 Gerenciar Campeonatos")
col_c1, col_c2 = st.columns([2, 1])
with col_c1:
    novo_campeonato = st.text_input(
        "Nome do novo campeonato (ex: Brasileirão 2026, Paulistão):",
        placeholder="Digite o nome do campeonato...",
    )
with col_c2:
    st.markdown("###")
    if st.button("➕ Adicionar Campeonato"):
        if novo_campeonato:
            cammp_limpo = novo_campeonato.strip()
            if cammp_limpo not in st.session_state["campeonatos_dados"]:
                st.session_state["campeonatos_dados"][cammp_limpo] = {}
                st.success(f"Campeonato '{cammp_limpo}' criado com sucesso!")
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
    # --- 2. CADA CAMPEONATO CRIADO GERA UMA ABA ---
    abas_campeonatos = st.tabs(campeonatos_cadastrados)

    html_todos_campeonatos = ""

    for idx_camp, camp_nome in enumerate(campeonatos_cadastrados):
        with abas_campeonatos[idx_camp]:
            st.markdown(f"### Competição: **{camp_nome}**")

            # Opção de ocultar/remover o campeonato se desejar
            col_del_c1, col_del_c2 = st.columns([4, 1])
            with col_del_c2:
                if st.button(f"🗑️ Excluir {camp_nome}", key=f"del_camp_{camp_nome}"):
                    del st.session_state["campeonatos_dados"][camp_nome]
                    st.rerun()

            st.markdown("---")
            st.markdown("#### Gerenciar Rodadas / Fases")

            # --- 3. CRIAR RODADA/FASE DE FORMA DINÂMICA ---
            col_r1, col_r2 = st.columns([2, 1])
            with col_r1:
                nova_rodada = st.text_input(
                    f"Nome da rodada/fase para {camp_nome} (ex: 1ª Rodada, Quartas):",
                    placeholder="Digite a rodada...",
                    key=f"input_rodada_{camp_nome}"
                )
            with col_r2:
                st.markdown("###")
                if st.button("➕ Adicionar Rodada", key=f"btn_add_rodada_{camp_nome}"):
                    if nova_rodada:
                        rodada_limpa = nova_rodada.strip()
                        if rodada_limpa not in st.session_state["campeonatos_dados"][camp_nome]:
                            st.session_state["campeonatos_dados"][camp_nome][rodada_limpa] = []
                            st.success(f"Rodada '{rodada_limpa}' adicionada!")
                            st.rerun()
                        else:
                            st.warning("Esta rodada já existe neste campeonato.")
                    else:
                        st.error("Digite um nome válido para a rodada.")

            rodadas_existentes = list(st.session_state["campeonatos_dados"][camp_nome].keys())

            cards_html_campeonato = ""

            if rodadas_existentes:
                st.divider()
                abas_rodadas = st.tabs(rodadas_existentes)

                for idx_rod, rodada_nome in enumerate(rodadas_existentes):
                    with abas_rodadas[idx_rod]:
                        st.markdown(f"##### Conteúdo da Rodada: {rodada_nome}")

                        # --- 4. UPLOAD PARA O .TXT COM OS IFRAMES ---
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
                                
                                # Código com height: 2000px fixo por padrão
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

                            # Monta a estrutura da rodada no HTML final
                            cards_html_campeonato += f"""
    <div class="round-section" data-round="{rodada_nome}">
        <h2 class="round-title">{rodada_nome}</h2>
        {cards_html_rodada}
    </div>\n"""

            # Salva os blocos montados deste campeonato para o template final
            if cards_html_campeonato:
                html_todos_campeonatos += f"""
<div class="championship-section" data-championship="{camp_nome}">
    <h1 class="page-title">{camp_nome}</h1>
    {cards_html_campeonato}
</div>\n"""

    # --- 5. GERAÇÃO DO HTML COMPLETO DA ESTRUTURA ---
    st.divider()
    st.subheader("📋 Código HTML Completo da Página para o Servidor")
    st.markdown("O código abaixo consolida todos os campeonatos, rodadas e iframes cadastrados:")

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
        .page-title {{
            text-align: center;
            color: #137d00;
            font-size: 2rem;
            margin: 35px 0 20px 0;
            text-transform: uppercase;
            letter-spacing: 1px;
            border-bottom: 2px solid #137d00;
            padding-bottom: 10px;
        }}
        .round-title {{
            color: #ffffff;
            font-size: 1.4rem;
            margin: 25px 0 15px 0;
            text-transform: uppercase;
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
{html_todos_campeonatos}
    </div>

    <footer>
        <p>R7 Esportes • Sistema de Cobertura Lance a Lance</p>
    </footer>

    <script>
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
