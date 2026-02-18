import streamlit as st
from google import genai
from google.genai import types
from datetime import datetime
import os

# 1. Configuração da página
st.set_page_config(page_title="Viaja-AI Pro", page_icon="✈️")
st.title("✈️ Viaja-AI Pro")
st.caption("Agente de Viagens Automático (Gemini 2.0)")

# 2. CARREGAMENTO AUTOMÁTICO DA CHAVE (DO COFRE)
# Em vez de pedir na tela, tentamos pegar dos "Segredos" do Streamlit
try:
    # Tenta pegar a chave que você salvou no site (Secrets)
    API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("❌ ERRO: Chave de API não encontrada!")
    st.info("Vá em 'Manage App' > 'Settings' > 'Secrets' e adicione: GEMINI_API_KEY = 'sua-chave'")
    st.stop()

# 3. Inicialização do Cliente e do Chat (AUTOMÁTICA)
if "chat_session" not in st.session_state:
    try:
        # Cria o cliente usando a chave automática
        client = genai.Client(api_key=API_KEY)
        
        # Configura a ferramenta de busca
        google_search_tool = types.Tool(
            google_search=types.GoogleSearch()
        )
        
        hoje = datetime.now().strftime("%d/%m/%Y")
        
        # Inicia o chat
        st.session_state.chat_session = client.chats.create(
            model='gemini-2.0-flash',
            config=types.GenerateContentConfig(
                tools=[google_search_tool],
                system_instruction=f"Você é um agente de viagens experiente. Hoje é {hoje}. Use o Google Search para achar preços reais e links."
            )
        )
    except Exception as e:
        st.error(f"Erro ao conectar: {e}")
        st.stop()

# 4. Histórico de Mensagens
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Área de Chat
if prompt := st.chat_input("Para onde vamos viajar?"):
    
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("assistant"):
        with st.spinner("Pesquisando..."):
            try:
                response = st.session_state.chat_session.send_message(prompt)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error("A conexão caiu. Tente recarregar a página.")
