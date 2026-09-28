import streamlit as st
import streamlit.components.v1 as components

# Configuração da página do Streamlit
st.set_page_config(
    page_title="R7 Esportes - Painel de Controlo",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Definição centralizada das URLs das imagens
url_desktop = "https://cloudfront-us-east-1.images.arcpublishing.com/newr7/7XJNKPHSNRGB7K5DJFYFATVSKU.jpg"
url_mobile = "https://cloudfront-us-east-1.images.arcpublishing.com/newr7/AXEMY2CIPFA4JJL57TICBSEXBM.jpg"

# Montagem completa da página injetada no componente do Streamlit
html_code = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>R7 Esportes - Painel</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            background-color: #121212;
            color: #ffffff;
            font-family: Arial, sans-serif;
            display: flex;
            flex-direction: column;
            min-height: 100vh;
        }}

        header {{
            width: 100%;
            background-color: #006b3f;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 20px;
            border-bottom: 4px solid #004d2c;
        }}

        .logo-container {{
            max-width: 600px;
            width: 100%;
        }}

        .logo-container img {{
            width: 100%;
            height: auto;
            display: block;
            object-fit: contain;
        }}

        .contrato-badge {{
            background-color: #000000;
            color: #ffffff;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            border: 1px solid #00ff66;
            white-space: nowrap;
        }}

        .main-container {{
            display: flex;
            flex: 1;
        }}

        aside {{
            width: 260px;
            background-color: #1a1a1a;
            padding: 20px 0;
            border-right: 1px solid #333;
            flex-shrink: 0;
        }}

        .menu-titulo {{
            font-size: 11px;
            text-transform: uppercase;
            color: #888;
            padding: 0 20px 10px 20px;
            letter-spacing: 1px;
        }}

        aside ul {{
            list-style: none;
        }}

        aside ul li a {{
            display: block;
            padding: 12px 20px;
            color: #ccc;
            text-decoration: none;
            font-size: 14px;
            transition: background 0.2s, color 0.2s;
        }}

        aside ul li a:hover, aside ul li a.active {{
            background-color: #2a2a2a;
            color: #ffffff;
            border-left: 4px solid #00ff66;
        }}

        .content-area {{
            flex: 1;
            padding: 30px;
            background-color: #121212;
        }}

        .section-title {{
            color: #00ff66;
            font-size: 18px;
            margin-bottom: 20px;
            letter-spacing: 0.5px;
            border-bottom: 1px solid #222;
            padding-bottom: 8px;
        }}

        .selector-box {{
            background-color: #181818;
            padding: 15px 20px;
            border: 1px solid #333;
            border-radius: 4px;
            margin-bottom: 25px;
            display: flex;
            align-items: center;
            gap: 15px;
        }}

        .selector-box label {{
            font-size: 14px;
            color: #ddd;
        }}

        .selector-box select {{
            background-color: #111;
            color: #fff;
            border: 1px solid #444;
            padding: 6px 10px;
            border-radius: 4px;
            width: 250px;
        }}

        .code-container {{
            background-color: #181818;
            border: 1px solid #333;
            border-radius: 4px;
            padding: 20px;
        }}

        .code-container h3 {{
            font-size: 16px;
            margin-bottom: 15px;
            color: #fff;
        }}

        pre {{
            background-color: #0d0d0d;
            border: 1px solid #262626;
            padding: 15px;
            border-radius: 4px;
            overflow-x: auto;
            font-family: Consolas, Monaco, monospace;
            font-size: 13px;
            color: #a6e22e;
            line-height: 1.5;
            margin-bottom: 15px;
        }}

        .btn-copiar {{
            background-color: #008040;
            color: white;
            border: none;
            padding: 8px 18px;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
            font-size: 13px;
            transition: background 0.2s;
        }}

        .btn-copiar:hover {{
            background-color: #00a854;
        }}
    </style>
</head>
<body>

    <!-- Cabeçalho visual do painel com tag picture -->
    <header>
        <div class="logo-container">
            <picture>
                <source media="(max-width: 768px)" srcset="{url_mobile}">
                <img src="{url_desktop}" alt="R7 Esportes">
            </picture>
        </div>
        <div class="contrato-badge">Contrato: 389 / 500</div>
    </header>

    <!-- Estrutura Principal -->
    <div class="main-container">
        <aside>
            <div class="menu-titulo">Campeonatos</div>
            <ul>
                <li><a href="#">Amistosos</a></li>
                <li><a href="#">Brasileirão</a></li>
                <li><a href="#">Champions League 2025/2026</a></li>
                <li><a href="#">Champions League 2026/2027</a></li>
                <li><a href="#">Copa do Brasil</a></li>
                <li><a href="#">Copa do Mundo</a></li>
                <li><a href="#" class="active">Copa dos Campeões Feminina</a></li>
                <li><a href="#">Copa Sulamericana</a></li>
                <li><a href="#">Libertadores da América</a></li>
                <li><a href="#">Paulistão</a></li>
            </ul>
        </aside>

        <div class="content-area">
            <div class="section-title">BRASILEIRÃO FEMININO</div>

            <div class="selector-box">
                <label for="rodada">Selecione a Rodada / Fase:</label>
                <select id="rodada">
                    <option value="final">Final</option>
                </select>
            </div>

            <div class="code-container">
                <h3>FINAL</h3>
                <!-- Injeta diretamente o HTML limpo e formatado com as variáveis exatas -->
                <pre>&lt;!-- R7 Esportes Header Responsivo --&gt;
&lt;header style="width: 100%; background-color: #006b3f;"&gt;
  &lt;picture&gt;
    &lt;source media="(max-width: 768px)" srcset="{url_mobile}"&gt;
    &lt;img src="{url_desktop}" alt="R7 Esportes" style="width: 100%; height: auto; display: block; object-fit: contain;"&gt;
  &lt;/picture&gt;
&lt;/header&gt;

&lt;!-- Campeonato Brasileiro - 2026 - Feminino Série A1 - Final --&gt;
&lt;div style="display: flex"&gt;
  &lt;div id="iframe_brasileirão_feminino_final_8" style="width: 100%; max-height: 100%; height: 2000px"&gt;&lt;/div&gt;
  &lt;script src="https://www.srsgoo.com.br/iframe.js?id=iframe_brasileirão_feminino_final_8key=NC4rmJc5hTCzOTYXTV5MJQ-ng"&gt;&lt;/script&gt;
&lt;/div&gt;</pre>
                <button class="btn-copiar" onclick="alert('Código copiado para a área de transferência!')">Copiar</button>
            </div>
        </div>
    </div>

</body>
</html>
"""

# Renderização do componente HTML no Streamlit
components.html(html_code, height=800, scrolling=True)
