import streamlit as st
from google import genai
from google.genai import types
from datetime import datetime

# 1. Configuração da página
st.set_page_config(page_title="Viaja-AI Pro", page_icon="✈️")
st.title("✈️ Viaja-AI Pro")
st.caption("Agente de Viagens com Google Search (Gemini 2.0)")

# 2. Configuração da Chave API (Barra Lateral)
with st.sidebar:
    st.header("⚙️ Configuração")
    if "api_key" not in st.session_state:
        st.session_state.api_key = ""
    
    # Campo de senha que atualiza a memória
    key_input = st.text_input("Cole sua API Key aqui:", type="password", value=st.session_state.api_key)
    if key_input:
        st.session_state.api_key = key_input

# Trava de segurança: Se não tiver chave, para tudo aqui.
if not st.session_state.api_key:
    st.warning("⬅️ Cole sua API Key na barra lateral para iniciar.")
    st.stop()

# 3. Inicialização do Cliente e do Chat (A CORREÇÃO ESTÁ AQUI)
# Usamos o 'session_state' para manter o Cliente VIVO entre os cliques.

if "my_client" not in st.session_state:
    try:
        # Cria o cliente apenas UMA vez e guarda na memória
        st.session_state.my_client = genai.Client(api_key=st.session_state.api_key)
    except Exception as e:
        st.error(f"Erro ao criar cliente: {e}")
        st.stop()

if "chat_session" not in st.session_state:
    try:
        # Configura a ferramenta de busca
        google_search_tool = types.Tool(
            google_search=types.GoogleSearch()
        )
        
        hoje = datetime.now().strftime("%d/%m/%Y")
        
        # Inicia o chat usando o cliente QUE JÁ ESTÁ NA MEMÓRIA
        st.session_state.chat_session = st.session_state.my_client.chats.create(
            model='gemini-2.0-flash',
            config=types.GenerateContentConfig(
                tools=[google_search_tool],
                system_instruction=f"Você é um agente de viagens experiente. Hoje é {hoje}. Use o Google Search para achar preços reais e links."
            )
        )
    except Exception as e:
        st.error(f"Erro ao iniciar chat: {e}")
        st.stop()

# 4. Exibe o Histórico de Mensagens
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Área de Chat (Interação do Usuário)
if prompt := st.chat_input("Ex: Passagem para Recife em Julho de 2026"):
    
    # Mostra mensagem do usuário
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Resposta do Agente
    with st.chat_message("assistant"):
        with st.spinner("Pesquisando..."):
            try:
                # Envia mensagem para a sessão ativa na memória
                response = st.session_state.chat_session.send_message(prompt)
                
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            
            except Exception as e:
                st.error(f"Erro de conexão: {e}")
                # Botão de emergência para reiniciar se a net cair
                if st.button("Reiniciar Conexão"):
                    for key in list(st.session_state.keys()):
                        del st.session_state[key]
                    st.rerun()
