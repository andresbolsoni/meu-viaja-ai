import streamlit as st
from google import genai
from google.genai import types
from datetime import datetime

# 1. CONFIGURAÇÃO DA PÁGINA (TÍTULO E ÍCONE)
st.set_page_config(page_title="Viaja-AI Pro", page_icon="✈️", layout="centered")

st.title("✈️ Viaja-AI Pro")
st.caption("Seu Consultor de Viagens com Google Search em Tempo Real")

# 2. BARRA LATERAL PARA SEGURANÇA (Para não deixar a chave exposta no código)
with st.sidebar:
    st.header("⚙️ Configuração")
    api_key = st.text_input("Cole sua Google API Key:", type="password")
    st.info("A chave não fica salva. É usada apenas nesta sessão.")

# 3. VERIFICA SE TEM CHAVE
if not api_key:
    st.warning("⬅️ Por favor, insira sua API Key na barra lateral para começar.")
    st.stop()

# 4. CONFIGURAÇÃO DO CLIENTE E MEMÓRIA (SESSION STATE)
# O Streamlit roda o código todo a cada clique. Precisamos guardar o chat na memória.

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_session" not in st.session_state:
    # Inicia o cliente apenas uma vez
    client = genai.Client(api_key=api_key)
    
    # Ferramenta de Busca
    google_search_tool = types.Tool(
        google_search=types.GoogleSearch()
    )
    
    hoje = datetime.now().strftime("%d/%m/%Y")
    
    # Inicia o Chat
    st.session_state.chat_session = client.chats.create(
        model='gemini-2.0-flash',
        config=types.GenerateContentConfig(
            tools=[google_search_tool],
            system_instruction=f"""
            Você é o Viaja-AI Pro. Hoje é {hoje}.
            Seu objetivo é planejar viagens usando dados REAIS do Google Search.
            Sempre cite preços e links. Seja cordial e use emojis.
            """
        )
    )

# 5. EXIBE O HISTÓRICO NA TELA (INTERFACE TIPO WHATSAPP)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. CAPTURA A MENSAGEM DO USUÁRIO
if prompt := st.chat_input("Para onde vamos viajar?"):
    
    # Mostra a mensagem do usuário na tela
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # O Agente Pensa e Responde
    with st.chat_message("assistant"):
        with st.spinner("Pesquisando no Google..."):
            try:
                # Envia para o Gemini
                response = st.session_state.chat_session.send_message(prompt)
                
                # Mostra a resposta
                st.markdown(response.text)
                
                # Salva no histórico
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                
            except Exception as e:
                st.error(f"Erro: {e}")
