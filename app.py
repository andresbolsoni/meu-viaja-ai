import streamlit as st
from google import genai
from google.genai import types
from datetime import datetime

# 1. Configuração da página
st.set_page_config(page_title="Viaja-AI Pro", page_icon="✈️")
st.title("✈️ Viaja-AI Pro")
st.caption("Agente de Viagens (Gemini 2.0 - Conexão Blindada)")

# 2. Carrega a Chave API (Dos Segredos)
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("❌ Chave GEMINI_API_KEY não encontrada nos Secrets!")
    st.stop()

# 3. Gerenciamento do Histórico (Visual)
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostra o chat na tela
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. A Lógica Blindada (Cria conexão nova a cada interação)
def conectar_e_responder(prompt_usuario):
    try:
        # A) Cria um cliente novinho em folha (Zero erro de 'client closed')
        client = genai.Client(api_key=API_KEY)
        
        # B) Configura a busca
        google_search_tool = types.Tool(google_search=types.GoogleSearch())
        hoje = datetime.now().strftime("%d/%m/%Y")
        
        # C) Reconstrói o histórico para o Gemini entender o contexto
        # Pegamos o que já foi falado e transformamos no formato do Google
        historico_gemini = []
        for msg in st.session_state.messages:
            role = "user" if msg["role"] == "user" else "model"
            historico_gemini.append(types.Content(role=role, parts=[types.Part(text=msg["content"])]))
            
        # D) Inicia o chat já com a memória do passado
        chat = client.chats.create(
            model='gemini-2.0-flash',
            history=historico_gemini, # <--- O segredo está aqui
            config=types.GenerateContentConfig(
                tools=[google_search_tool],
                system_instruction=f"Hoje é {hoje}. Você é um agente de viagens. Pesquise preços reais."
            )
        )
        
        # E) Envia a nova mensagem
        response = chat.send_message(prompt_usuario)
        return response.text
        
    except Exception as e:
        return f"⚠️ Erro técnico: {e}"

# 5. Captura a entrada do usuário
if prompt := st.chat_input("Para onde vamos?"):
    
    # Adiciona a pergunta do usuário na tela
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Processa a resposta
    with st.chat_message("assistant"):
        with st.spinner("Conectando ao Google e pesquisando..."):
            
            resposta = conectar_e_responder(prompt)
            
            st.markdown(resposta)
            st.session_state.messages.append({"role": "assistant", "content": resposta})
