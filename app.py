if st.button("🧪 Testar Conexão e Gravação com o GitHub"):
    dados_teste = {"teste": "funcionando", "timestamp": "2026-03-30"}
    
    # Valida se as secrets existem
    try:
        t = st.secrets["GITHUB_TOKEN"]
        r = st.secrets["GITHUB_REPO"]
        b = st.secrets.get("GITHUB_BRANCH", "main")
        st.write(f"Repositório configurado: `{r}` (Branch: `{b}`)")
        st.write(f"Token detectado (primeiros 6 chars): `{t[:6]}...`")
    except Exception as err:
        st.error(f"Erro nas Secrets do Streamlit: {err}")
        st.stop()
        
    # Tenta enviar um JSON de teste
    url = f"https://api.github.com/repos/{r}/contents/estrutura_lance_a_lance.json"
    headers = {"Authorization": f"Bearer {t}", "Accept": "application/vnd.github+json"}
    
    get_resp = requests.get(url, headers=headers, params={"ref": b})
    sha = get_resp.json().get("sha") if get_resp.status_code == 200 else None
    
    import base64
    content_encoded = base64.b64encode(json.dumps(dados_teste).encode("utf-8")).decode("utf-8")
    
    payload = {
        "message": "Teste de gravação via Streamlit",
        "content": content_encoded,
        "branch": b
    }
    if sha:
        payload["sha"] = sha
        
    put_resp = requests.put(url, headers=headers, json=payload)
    st.write(f"Status Code retornado pelo GitHub: **{put_resp.status_code}**")
    st.json(put_resp.json())
