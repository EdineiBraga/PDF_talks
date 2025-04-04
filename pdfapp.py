import tempfile
import streamlit as st
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from loaders import *
from langchain.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()

MEMORIA=ConversationBufferMemory()
modelo='gpt-4o-mini'
api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title='FileTalks',layout='wide',page_icon='📖')

def carrega_arquivos(tipo_arquivo, arquivo):

    if tipo_arquivo == 'Site':
        documento = carrega_site(arquivo)
    if tipo_arquivo == 'Youtube':
        documento = carrega_youtube(arquivo)
    if tipo_arquivo == 'pdf':
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp:
            temp.write(arquivo.read())
            nome_temp = temp.name
        documento = carrega_pdf(nome_temp)
    if tipo_arquivo == 'csv':
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as temp:
            temp.write(arquivo.read())
            nome_temp = temp.name
        documento = carrega_csv(nome_temp)
    if tipo_arquivo == 'txt':
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp:
            temp.write(arquivo.read())
            nome_temp = temp.name
        documento = carrega_txt(nome_temp)    
    return documento                    



def carrega_modelo(modelo,api_key,tipo_arquivo,arquivo):

    documento=carrega_arquivos(tipo_arquivo,arquivo)

    system_message = '''Você é um assistente amigável chamado Oráculo.
    Você possui acesso às seguintes informações vindas 
    de um documento {}: 

    ####
    {}
    ####

    Utilize as informações fornecidas para basear as suas respostas.

    Sempre que houver $ na sua saída, substita por S.

    Se a informação do documento for algo como "Just a moment...Enable JavaScript and cookies to continue" 
    sugira ao usuário carregar novamente o Oráculo!'''.format(tipo_arquivo, documento)

    template = ChatPromptTemplate.from_messages([
        ('system', system_message),
        ('placeholder', '{chat_history}'),
        ('user', '{input}')
    ])
    
   
    chat=ChatOpenAI(model=modelo,api_key=api_key,temperature=0.3)
    chain=template|chat   
    st.session_state['chain']=chain

TIPOS_ARQUIVOS_VALIDOS=[
    'Site','Youtube','pdf','csv','txt'
]

def pagina_chat():
    st.header('📖 Bem vindo!',divider=True,)
    st.write('Este é um explorador de arquivos.\n1. Selecione o tipo de arquivo.\n2. Inicialize o assistente.\n3. Faça perguntas referentes ao arquivo.')
    chain=st.session_state.get('chain')
    if chain is None:
        st.error('CARREGUE UM DOCUMENTO!')
        st.stop()
    memoria=st.session_state.get('memoria',MEMORIA)

    for mensagem in memoria.buffer_as_messages:
        if mensagem.type == "human":
            chat = st.chat_message("human", avatar="😎")  # Ícone personalizado do usuário
        else:
            chat = st.chat_message("ai", avatar="🤖")  # Ícone personalizado da IA
        #chat=st.chat_message(mensagem.type,'😎','🤖')
        chat.markdown(mensagem.content)
    input_usuario=st.chat_input('Faça uma pergunta sobre o documento carregado...')
    if input_usuario:
        memoria.chat_memory.add_user_message(input_usuario)
        chat=st.chat_message('human',avatar='😎')
        chat.markdown(input_usuario)
        chat=st.chat_message('ai',avatar='🤖')
        resposta=chat.write_stream(chain.stream({'input':input_usuario,'chat_history':memoria.buffer_as_messages}))
        memoria.chat_memory.add_ai_message(resposta) 
        st.session_state['memoria']=memoria
        #st.rerun()

def sidebar():
    #tabs=st.tabs(['Upload de Arquivos','Seleção de Modelos'])
    #with tabs[0]:
    tipo_arquivo=st.selectbox('Selecione o tipo de arquivo',TIPOS_ARQUIVOS_VALIDOS)
    if tipo_arquivo=='Site':
        arquivo=st.text_input('Digite a URL do site:')
    if tipo_arquivo=='Youtube':
        arquivo=st.text_input('Digite a URL do vídeo:') 
    if tipo_arquivo=='pdf':
        arquivo=st.file_uploader('Faça o upload do arquivo .pdf:',type=['.pdf'])
    if tipo_arquivo=='csv':
        arquivo=st.file_uploader('Faça o upload do arquivo .csv:',type=['.csv'])
    if tipo_arquivo=='txt':
        arquivo=st.file_uploader('Faça o upload do arquivo .txt:',type=['.txt'])
    if st.button('Inicializar Assistente',use_container_width=True):
        carrega_modelo(modelo,api_key,tipo_arquivo,arquivo)
    if st.button('Apagar Histórico de Conversa', use_container_width=True):
        st.session_state['memoria'] = MEMORIA
        
        
                  

                                                      


def main():
    #carrega_modelo()    
    with st.sidebar:
        sidebar()
    pagina_chat()

if __name__=='__main__' :
    main()       

