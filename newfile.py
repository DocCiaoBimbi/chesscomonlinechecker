import telebot
import threading
import time as tm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

TOKEN = "7579561581:AAGPMxnzMt9NOTJc_AyMsBreyDHfjha3-Yo"
bot = telebot.TeleBot(TOKEN)

followed_users = {}

def check_html_line_exists(username):
    url = f"https://www.chess.com/member/{username}"
    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    options.add_argument("--headless=new")

    driver = webdriver.Chrome(options=options)
    driver.get(url)

    try:
        tm.sleep(5)
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "profile-card-info-item-value"))
        )
        if element.text.strip().lower() == "Online Now":
            return True
    except Exception as e:
        print("Errore:", e)
    finally:
        driver.quit()
    return False

def follow_user(chat_id, username):
    while True:
        is_online = check_html_line_exists(username)
        
        if is_online and not was_online:
            bot.send_message(chat_id, f"{username} è online su Chess.com!")
            was_online = True  # Aggiorna lo stato a "online"
        elif not is_online and was_online:
            bot.send_message(chat_id, f"{username} è offline su Chess.com.")
            was_online = False  # Aggiorna lo stato a "offline"

        tm.sleep(5)  # Controlla ogni 5 secondi

def follow_user(chat_id, username):
    followed_users[chat_id] = followed_users.get(chat_id, [])
    if username not in followed_users[chat_id]:
        followed_users[chat_id].append(username)

    was_online = False

    while True:
        is_online = check_html_line_exists(username)
        
        if is_online and not was_online:
            bot.send_message(chat_id, f"{username} è online su Chess.com!")
            was_online = True
        elif not is_online and was_online:
            bot.send_message(chat_id, f"{username} è offline su Chess.com.")
            was_online = False

        tm.sleep(5)

@bot.message_handler(commands=['list'])
def show_followed(message):
    chat_id = message.chat.id
    if chat_id not in followed_users or not followed_users[chat_id]:
        bot.reply_to(message, "Non stai seguendo nessun giocatore.")
    else:
        followed_list = "\n".join(followed_users[chat_id])
        bot.reply_to(message, f"Giochi seguiti:\n{followed_list}")


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Ciao! Sono un bot per controllare lo stato online dei giocatori su Chess.com.\n\nComandi disponibili:\n/start - Mostra questo messaggio\n/follow <username> - Segui un utente e ricevi una notifica quando è online\n/verify <username> - Controlla se un utente è online in questo momento")

@bot.message_handler(commands=['follow'])
def follow(message):
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "Uso corretto: /follow <username>")
        return
    username = args[1]
    bot.reply_to(message, f"Sto monitorando {username}. Ti avviserò quando sarà online.")
    thread = threading.Thread(target=follow_user, args=(message.chat.id, username))
    thread.start()

@bot.message_handler(commands=['verify'])
def verify(message):
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "Uso corretto: /verify <username>")
        return
    username = args[1]
    if check_html_line_exists(username):
        bot.reply_to(message, f"{username} è attualmente online su Chess.com!")
    else:
        bot.reply_to(message, f"{username} non è online su Chess.com.")

if __name__ == "__main__":
    bot.polling(none_stop=True)