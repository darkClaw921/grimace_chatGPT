import os
import random
import telebot
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pprint import pprint
from chat import GPT
from datetime import datetime
import workYDB
import redis
import json
from loguru import logger
import sys
from createKeyboard import create_menu_keyboard
from workBitrix import *
from helper import *
from workGDrive import *
from telebot.types import InputMediaPhoto
from workRedis import *
import workGS
from workFaiss import *
from flask import Flask
app = Flask(__name__)

#если sqlite3 не поддерживается на системе
# pip3 install pysqlite3-binary
# __import__('pysqlite3')
# import sys
# sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

load_dotenv()


logger.add(sys.stderr, format="{time} {level} {message}", level="INFO")
logger.add("file_1.log", rotation="50 MB")
gpt = GPT()
GPT.set_key(os.getenv('KEY_AI'))
bot = telebot.TeleBot(os.getenv('TELEBOT_TOKEN'))
sheet = workGS.Sheet('kgtaprojects-8706cc47a185.json','Доработка AI бота Grimace')
sql = workYDB.Ydb()

URL_USERS = {}

MODEL_URL= 'https://docs.google.com/document/d/17a4WtyRxhDk3D2-Kger1eBiekBQ2BmMLTYg3e6joKDI/edit?usp=sharing'
#TODO
gsText, urls_photo = sheet.get_gs_text()
# gsText = ''
# print(f'{gsText=}')
model_index=gpt.load_search_indexes(MODEL_URL, gsText=gsText) 
PROMT_URL = 'https://docs.google.com/document/d/1Oiys8iwstN4Ugjfz3pnD3LFGpHHgVHwUTp2ILjqcbsw/edit?usp=sharing'
model= gpt.load_prompt(PROMT_URL)


# PROMT_URL_SUMMARY ='https://docs.google.com/document/d/1XhSDXvzNKA9JpF3QusXtgMnpFKY8vVpT9e3ZkivPePE/edit?usp=sharing'
# PROMT_PODBOR_HOUSE = 'https://docs.google.com/document/d/1WTS8SQ2hQSVf8q3trXoQwHuZy5Q-U0fxAof5LYmjYYc/edit?usp=sharing'

#info_db=create_info_vector()

@bot.message_handler(commands=['addmodel'])
def add_new_model(message):
    sql.set_payload(message.chat.id, 'addmodel')
    bot.send_message(message.chat.id, 
        "Пришлите ссылку promt google document и через пробел название модели (model1). Не используйте уже существующие названия модели\n Внимани! конец ссылки должен вылядить так /edit?usp=sharing",)
    

@bot.message_handler(commands=['help', 'start'])
def say_welcome(message):
    username = message.from_user.username
    row = {'id': 'Uint64', 'MODEL_DIALOG': 'String', 'TEXT': 'String'}
    sql.create_table(str(message.chat.id), row)
    #row = {'id': message.chat.id, 'payload': '',}
    row = {'id': abs(message.chat.id), 'model': '', 'promt': '','nicname':username, 'payload': ''}
    sql.replace_query('user', row)
    
    #text = """Здравствуйте, я AI ассистент компании Сканди ЭкоДом. Я отвечу на Ваши вопросы по поводу строительства загородного дома и задам свои 😁. Хотите я Вам расскажу про варианты комплектации домов?
    #"""
    text = """Здравствуйте"""
    history = []
    answer, allToken, allTokenPrice, message_content = gpt.answer_index(model, text, history, model_index,temp=0.5, verbose=0)
    add_message_to_history(message.chat.id, 'assistant', answer) 
    bot.send_message(message.chat.id, answer, 
                     parse_mode='markdown',)
                     #reply_markup= create_menu_keyboard())
#expert_promt = gpt.load_prompt('https://docs.google.com/document/d/181Q-jJpSpV0PGnGnx45zQTHlHSQxXvkpuqlKmVlHDvU/')

@bot.message_handler(commands=['restart'])
def restart_modal_index(message):
    global model_index, model 
  
    MODEL_URL= 'https://docs.google.com/document/d/17a4WtyRxhDk3D2-Kger1eBiekBQ2BmMLTYg3e6joKDI/edit?usp=sharing'
    gsText, urls_photo = sheet.get_gs_text()
    # print(f'{gsText=}')
    model_index=gpt.load_search_indexes(MODEL_URL, gsText=gsText) 
    bot.send_message(message.chat.id, 'Обновлено', 
                     parse_mode='markdown',)
                     #reply_markup= create_menu_keyboard())

@bot.message_handler(commands=['context'])
def send_button(message):
    global URL_USERS
    URL_USERS={}
    #payload = sql.get_payload(message.chat.id)
    

    #answer = gpt.answer(validation_promt, context, temp = 0.1)
   # sql.delete_query(message.chat.id, f'MODEL_DIALOG = "{payload}"')
   # sql.set_payload(message.chat.id, ' ')
    #bot.send_message(message.chat.id, answer)
    clear_history(message.chat.id)
    bot.send_message(message.chat.id, 
        "Контекст сброшен",reply_markup=create_menu_keyboard(),)

@bot.message_handler(commands=['model1'])
def dialog_model1(message):
    #payload = sql.get_payload(message.chat.id)
    sql.set_payload(message.chat.id, 'model1')
    bot.send_message(message.chat.id,'Что вы хотите узнать?',)

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
     # Получаем информацию о фото
    username = message.from_user.username
    photo_info = message.photo[-1]
    file_id = photo_info.file_id

    # Скачиваем фото
    file_info = bot.get_file(file_id)
    file_url = f"https://api.telegram.org/file/bot{os.getenv('TELEBOT_TOKEN')}/{file_info.file_path}" 
    fileName = download_file(file_url)
    # create_lead_and_attach_file([fileName], username)
    #bot.reply_to(message, f'Спасибо, мы просчитаем Ваш проект и свяжемся с вами')

@bot.message_handler(content_types=['document'])
def handle_document(message):
    userID= message.chat.id
    username = message.from_user.username
    logger.info(f'{message.document=}')#
    #for document in message.document:
    file_info = bot.get_file(message.document.file_id)
    pprint(file_info)
    file_url = f"https://api.telegram.org/file/bot{os.getenv('TELEBOT_TOKEN')}/{file_info.file_path}"
        # Отправляем ответное сообщение
    fileName = download_file(file_url)
    # create_lead_and_attach_file([fileName], username)
    # bot.reply_to(message, f'Спасибо, мы просчитаем Ваш проект и свяжемся с вами')
    

    #create_lead_and_attach_file([],userID)

#@logger.catch
@bot.message_handler(content_types=['text'])
@logger.catch
def any_message(message):
    global URL_USERS
    #print('это сообщение', message)
    #text = message.text.lower()
    # reply_to = message.reply_to_message
    logger.debug(f'{message.from_user.username=}')
    logger.debug(f'{message.from_user=}')
    logger.debug(f'{message.from_user.id=}')
    logger.debug(f'{message.chat.id=}')
    # if reply_to is not None:
    #     return 0 
    #pprint(reply_to)
    text = message.text.lower()
    

    userID= abs(message.from_user.id)
    
    
    logger.debug(f'{message=}')
    
    logger.debug(f'{message.content_type=}')
    # logger.debug(f'{message.reply_to_message.from_user.id=}')
    logger.debug(f'{message.entities=}')
    logger.debug(f'{bot.get_me().id=}')
    
    logger.debug(f'{message.reply_to_message=}')
    # logger.debug(f'{message.reply_to_message.from_user.id=}')
    logger.debug(f'{bot.get_me().id=}')
    
    if message.reply_to_message is not None:
        logger.info('это реплай')
        if message.reply_to_message.from_user.id != bot.get_me().id:
            logger.info('это не боту')
            if text.find('hey ai') >= 0: 
                logger.info('есть кодовое слово')    
                text = 'hey ai ' + message.reply_to_message.text 
                1+0
            elif text.find('hey ai') == -1:
                logger.info('нету кодовое слово')    
                return 0  

    # if message.reply_to_message is not None and message.reply_to_message.from_user.id != bot.get_me().id:
    #     return 0 
    
    if message.reply_to_message is not None and message.reply_to_message.from_user.id == bot.get_me().id:
        1+0
        
    # elif message.chat.id < 0 and (message.text.find('hey ai,') == -1 or message.text.find('hey ai') == -1): 
    elif message.chat.id < 0 and text.find('hey ai') == -1 : 
        return 0
    

    try:
        payload = sql.get_payload(userID)
    except:
        username = message.from_user.username
        row = {'id': 'Uint64', 'MODEL_DIALOG': 'String', 'TEXT': 'String'}
        sql.create_table(userID, row)
        #row = {'id': message.chat.id, 'payload': '',}
        row = {'id': userID, 'model': '', 'promt': '','nicname':username, 'payload': ''}
        sql.replace_query('user', row)

    payload = ''


    add_message_to_history(userID, 'user', text)
    history = get_history(str(userID))
    logger.info(f'история {history}')


    try:
        logger.info(f'{PROMT_URL}')
        model= gpt.load_prompt(PROMT_URL) 
    except:
        model= gpt.load_prompt(PROMT_URL) 
    
    model = model.replace('[price]', str(get_grimace_price()))

    lastMessage = history[-1]['content'] 
        
    try:
        if text == 'aabb':
            1/0
        answer, allToken, allTokenPrice, message_content = gpt.answer_index(model, lastMessage+text, history, model_index,temp=0.5, verbose=0)
        logger.info(f'ответ сети если нет ощибок: {answer}')
        #print('мы получили ответ \n', answer)
    except Exception as e:
        #bot.send_message(userID, e)
        #bot.send_message(userID, 'начинаю sammury: ответ может занять больше времени, но не более 3х минут')
        history = get_history(str(userID))
        #summaryHistory = gpt.get_summary(history)
        promt_summary= gpt.load_prompt('https://docs.google.com/document/d/1O9lJUnDT_yqDnfip0xIvvomsb4DT_oei8kEi6JUV0CA/edit?usp=sharing') 
        summaryHistory1 = gpt.summarize_questions(history,promt_summary)
        logger.info(f'summary истории1 {summaryHistory1}')
     
        history = [summaryHistory1]
        history.extend([{'role':'user', 'content': text}])
        add_old_history(userID,history)
        history = get_history(str(userID))
        logger.info(f'история после summary {history}')
        #print('история после очистки\n', history)
        
        #answer = gpt.answer_index(model, text, history, model_index,temp=0.2, verbose=1)
        answer, allToken, allTokenPrice, message_content = gpt.answer_index(model, text, history, model_index,temp=0.5, verbose=0)
        bot.send_message(message.chat.id, answer)
        add_message_to_history(userID, 'assistant', answer)

        return 0 
    
   
    add_message_to_history(userID, 'assistant', answer)
  
    try:    
        #bot.send_message(message.chat.id, answer,  parse_mode='markdown')
        bot.reply_to(message, answer,  parse_mode='markdown')
    except:
        #bot.send_message(message.chat.id, answer,)
        bot.reply_to(message, answer,)
    

   
    now = datetime.now()+timedelta(hours=3)
    #now = datetime.now()
# Format the date and time according to the desired format
    formatted_date = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    
    #answer, allToken, allTokenPrice= gpt.answer(' ',mess,)
    row = {'all_price': float(allTokenPrice), 'all_token': int(allToken), 'all_messages': 1}
    sql.plus_query_user('user', row, f"id={userID}")
    
    username = message.from_user.username
    rows = {'time_epoch': time_epoch(),
            'MODEL_DIALOG': payload,
            'date': formatted_date,
            'id': userID,
            'nicname': username,
            #'token': username,
            #'token_price': username,
            'TEXT': f'Клиент: {text}'}
    sql.insert_query('all_user_dialog',  rows)
    
    rows = {'time_epoch': time_epoch(),
            'MODEL_DIALOG': payload,
            'date': formatted_date,
            'id': userID,
            'nicname': username,
            'token': allToken,
            'token_price': allTokenPrice,
            'TEXT': f'Менеджер: {answer}'}
    sql.insert_query('all_user_dialog',  rows)





if __name__ == '__main__':
    import threading
    import multiprocessing

    # flask_thread = threading.Thread(target=app.run(host='0.0.0.0',port='5006',debug=False))
    telebot_thread = threading.Thread(target=bot.infinity_polling())

    # flask_process = multiprocessing.Process(target=flask_thread.start)
    telebot_process = multiprocessing.Process(target=telebot_thread.start)

    # flask_process.start()
    telebot_process.start()
    print(f'[OK]')


