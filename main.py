import telebot
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("token")

bot = telebot.TeleBot(token)
user_status = {}
message_catched = ""


@bot.message_handler(commands=['start', 'Start'])
def send_welcome(message):
    user_status[message.chat.id] = 'iniciado'
    bot.reply_to(message, 
                    "👋 *Bem-vindo ao meu Bot de Mensagens em Massa!*\n\n"
                    "Olá! Estou empolgado por você estar aqui. Este bot foi criado para facilitar o envio de mensagens para seus contatos de maneira rápida e eficiente.\n\n"
                    "📝 *Funcionalidades do Bot:*\n"
                    "- Envio de mensagens em massa com apenas alguns cliques.\n"
                    "- Opção de agendar mensagens para momentos estratégicos.\n"
                    "- Personalização das mensagens para tornar a comunicação mais atrativa.\n\n"
                    "Para começar, envie o comando /iniciar e vamos aproveitar ao máximo!\n\n"
                    "Se tiver dúvidas ou precisar de ajuda, é só chamar! Estou aqui para tornar sua experiência incrível! 🚀"
        )
    
    store_user_info(message)
    
    
def store_user_id(chat_id, filename='users_id.txt'):
    if not is_user_id_exists(chat_id, filename):
        with open(filename, 'a') as f:  
            f.write(f"{chat_id}\n")  
            print(f"ID do usuário {chat_id} adicionado ao arquivo.")

def is_user_id_exists(chat_id, filename='users_id.txt'):
    try:
        with open(filename, 'r') as f:
            user_ids = f.readlines()
            user_ids = [uid.strip() for uid in user_ids]  
            return str(chat_id) in user_ids 
    except FileNotFoundError:
        return False


# Resto do seu código...
     
@bot.message_handler(commands=['iniciar', 'Iniciar'])
def options(message):
    if user_status.get(message.chat.id) != 'iniciado':
        bot.reply_to(message, "🔒 Você precisa usar o comando /start antes de alterar a mensagem.")
        return
    bot.reply_to(message, 
                    '/enviar - Envio de mensagens em massa com apenas alguns cliques.\n',
                    parse_mode="Markdown"
        )
     
     
#comando de enviar em massa     
@bot.message_handler(commands=['Enviar', 'enviar'])
def start_send(message):
        if user_status.get(message.chat.id) != 'iniciado':
            bot.reply_to(message, "🔒 Você precisa usar o comando /iniciar primeiro.")
            return
        
        bot.reply_to(
            message, 
            "✉️ *Qual mensagem você gostaria de enviar?*\n\n"
            "Digite o texto abaixo e vamos prepará-lo para o envio. Você pode personalizar usando variáveis, como `{nome}`, para tornar a comunicação mais pessoal!\n\n"
            "*Exemplo*: \"Olá, {nome}! Temos novidades exclusivas para você.\"",
            parse_mode="Markdown"
            )
        bot.register_next_step_handler(message, catch_message)
        
def catch_message(message):
    global message_catched
    mensagem_usuario = message.text
    message_catched = message.text
    bot.send_message(
        message.chat.id, 
        f"Sua mensagem foi salva:\n\n{mensagem_usuario}\n\n"
        "Deseja /encaminhar ou /alterar alguma coisa?")
    user_status[message.chat.id] = 'mensagem_capturada'
    
@bot.message_handler(commands=['alterar', 'Alterar'])
def editar_mensagem(message):
    if user_status.get(message.chat.id) != 'mensagem_capturada':
        bot.reply_to(message, "🔒 Você precisa usar o comando /enviar antes de alterar a mensagem.")
        return
    user_status[message.chat.id] = 'enviando'
    bot.send_message(message.chat.id, "✏️ *Digite a nova mensagem que você gostaria de enviar:*", parse_mode="Markdown")
    bot.register_next_step_handler(message, catch_message)
    
    
@bot.message_handler(commands=['encaminhar', 'Encaminhar'])
def send_bulk_message(message):
    if user_status.get(message.chat.id) != 'mensagem_capturada':
        bot.reply_to(message, "🔒 Você precisa usar o comando /alterar primeiro.")
        return
    
    user_status[message.chat.id] = 'iniciado'
    user_ids = load_user_ids()
    message_text = message_catched
    recipients = []

    for chat_id in user_ids:
        try:
            bot.send_message(chat_id, message_text)
            first_name = get_first_name(chat_id)
            if first_name:
                recipients.append(first_name)

            print(f"Mensagem enviada para {chat_id}")
        except Exception as e:
            print(f"Erro ao enviar mensagem para {chat_id}: {e}")

    if recipients:
        recipients_list = ", ".join(recipients)
        bot.reply_to(message, f"As mensagens foram enviadas para: {recipients_list}")
        bot.reply_to(message, f"Caso deseje enviar novamente use o comando /iniciar para repetir o processo ;).")
    else:
        bot.reply_to(message, "Nenhuma mensagem foi enviada.")


#final comando enviar menssagems em massa
    
    
#menssagem padrao 
@bot.message_handler(func=lambda message: True)
def handle_unrecognized_message(message):
    bot.reply_to(message, "Desculpe, não reconheço esse comando. Tente usar /start para iniciar uma conversa comigo ;).")
#menssagem padrao 
    
def load_user_ids(filename='users_id.txt'):
    try:
        with open(filename, 'r') as f:
            user_ids = [line.strip() for line in f.readlines() if line.strip()]
        return user_ids
    except FileNotFoundError:
        print("Arquivo não encontrado. Certifique-se de que 'user_ids.txt' existe.")
        return []
    
def store_user_info(message):
    chat_id = message.chat.id
    username = message.from_user.username or "Nao fornecido"
    first_name = message.from_user.first_name or "Nao fornecido"
    last_name = message.from_user.last_name or "Nao fornecido"
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    try:
        with open('infos_users.txt', 'a') as f:
            f.write(f"{timestamp},{chat_id},{first_name},{last_name},{username}\n")  # Salva as informações
            print(f"Informações do usuário {chat_id} armazenadas.")
    except Exception as e:
        print(f"Erro ao escrever no arquivo: {e}")
        

def get_first_name(chat_id):
    try:
        with open('infos_users.txt', 'r') as f:
            lines = f.readlines()
        
        for line in lines:
            if str(chat_id) in line:
                return line.split(',')[2] 
    except Exception as e:
        print(f"Erro ao obter primeiro nome para o chat_id {chat_id}: {e}")
    return None
    
bot.polling()