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
    "Faça o upload do arquivo de texto para estruturar a página com os blocos de código e botões de cópia para a redação."
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
                        if novo_item not in st.session_state["sub_abas_dados"][categoria_selecionada][sub_aba_nome]:
                            st.session_state["sub_abas_dados"][categoria_selecionada][sub_aba_nome].append(novo_item)
                    
                    str_lit.success(f"{len(keys)} jogos importados com sucesso do arquivo .txt!")
                else:
                    str_lit.error("Não foi possível extrair os dados automaticamente. Verifique o formato do arquivo.")

            # Botão para limpar itens desta sub-aba
            if str_lit.session_state["sub_abas_dados"][categoria_selecionada][sub_aba_nome]:
                if str_lit.button("🗑️ Limpar jogos desta sub-aba", key=f"clear_{sub_aba_nome}"):
                    str_lit.session_state["sub_abas_dados"][categoria_selecionada][sub_aba_nome] = []
                    str_lit.rerun()

            str_lit.markdown("---")
            str_lit.markdown("#### Validação na Administração (Visualização rápida):")
            
            jogos_atuais = str_lit.session_state["sub_abas_dados"][categoria_selecionada][sub_aba_nome]
            
            if not jogos_atuais:
                str_lit.info("Nenhum jogo cadastrado nesta sub-aba ainda. Faça o upload de um arquivo .txt acima.")
            else:
                cards_html_gerador = ""
                
                for i, jogo in enumerate(jogos_atuais):
                    id_container = f"iframe_container_{i}"
                    
                    # O código HTML completo do iframe exato conforme o padrão enviado
                    codigo_iframe_puro = f"""<!-- {jogo.get('comentario_original', jogo['nome'])} -->
<div style="display: flex">
    <div id="{id_container}" style="width: 100%; max-height: 100%; height: 2000px"> </div>
    <script src="https://www.srgoool.com.br/iframe.js.php?id={id_container}&key={jogo['key']}"></script>
</div>"""

                    # Card estruturado exatamente igual ao modelo da imagem fornecida
                    card_html = f"""
    <div class="match-card">
        <div class="match-comment">{jogo.get('comentario_original', jogo['nome'])}</div>
        <div class="code-box-wrapper">
            <pre><code id="code_{i}">{codigo_iframe_puro}</code></pre>
        </div>
        <button class="copy-btn" onclick="copiarCodigo('code_{i}', this)">Copiar</button>
    </div>\n\n"""
                    
                    cards_html_gerador += card_html

                    with str_lit.expander(f"⚽ {jogo['nome']}"):
                        str_lit.code(codigo_iframe_puro, language="html")

                # Montagem do Template HTML Completo para o Servidor com o layout idêntico à referência
                html_pagina_completa = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lance a Lance - {categoria_selecionada} ({sub_aba_nome})</title>
    
    <!-- Meta tags Open Graph -->
    <meta property="og:title" content="Lance a Lance: {categoria_selecionada} - {sub_aba_nome}">
    <meta property="og:description" content="Central de cópias de iframes para os artigos de {categoria_selecionada}.">
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
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        .page-title {{
            text-align: center;
            color: #137d00;
            font-size: 1.8rem;
            margin: 25px 0;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .match-card {{
            background: #f1f3f5;
            border: 1px solid #dcdcdc;
            border-radius: 8px;
            margin-bottom: 25px;
            padding: 15px 20px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
            color: #212529;
        }}
        .match-comment {{
            font-size: 0.85rem;
            font-style: italic;
            color: #495057;
            margin-bottom: 10px;
        }}
        .code-box-wrapper {{
            background: #ffffff;
            border: 1px solid #ced4da;
            border-radius: 4px;
            padding: 10px;
            margin-bottom: 12px;
        }}
        pre {{
            margin: 0;
            overflow-x: auto;
            white-space: pre-wrap;
            word-break: break-all;
        }}
        code {{
            font-family: Consolas, Monaco, "Andale Mono", monospace;
            color: #212529;
            font-size: 0.85rem;
        }}
        .copy-btn {{
            background-color: #137d00;
            color: #ffffff;
            border: none;
            padding: 8px 22px;
            font-size: 0.9rem;
            font-weight: bold;
            border-radius: 4px;
            cursor: pointer;
            transition: background 0.2s;
        }}
        .copy-btn:hover {{
            background-color: #0f6600;
        }}
        .copy-btn.copied {{
            background-color: #2b8a3e;
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

    <!-- Header Responsivo -->
    <header class="header-container">
        <img src="https://cloudfront-us-east-1.images.arcpublishing.com/newr7/7XJNKPHSNRGB7K5DJFYFATVSKU.jpg" alt="Header R7" class="header-desktop">
        <img src="https://cloudfront-us-east-1.images.arcpublishing.com/newr7/7XJNKPHSNRGB7K5DJFYFATVSKU.jpg" alt="Header R7 Mobile" class="header-mobile">
    </header>

    <div class="container">
        <h1 class="page-title">{categoria_selecionada} — {sub_aba_nome}</h1>

        <!-- Cards de Códigos por Jogo -->
{cards_html_gerador}
    </div>

    <footer>
        <p>R7 Esportes • Sistema de Cobertura Lance a Lance</p>
    </footer>

    <script>
        function copiarCodigo(idElemento, botao) {{
            const elementoCodigo = document.getElementById(idElemento);
            const texto = elementoCodigo.innerText;
            
            navigator.clipboard.writeText(texto).then(() => {{
                const textoOriginal = botao.innerText;
                botao.innerText = "Copiado! ✔️";
                botao.classList.add("copied");
                
                setTimeout(() => {{
                    botao.innerText = textoOriginal;
                    botao.classList.remove("copied");
                }}, 2000);
            }}).catch(err => {{
                console.error('Erro ao tentar copiar: ', err);
            }});
        }}
    </script>
</body>
</html>"""

                str_lit.divider()
                str_lit.subheader("📋 Código HTML Completo da Página para o Servidor")
                str_lit.markdown("Copie o código completo abaixo, salve como arquivo `.html` e faça o upload para o servidor:")
                str_lit.code(html_pagina_completa, language="html")
