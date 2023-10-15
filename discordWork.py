from pprint import pprint
import discord
from discord.ext import commands
# from workTelegram import any_message
import dialogWork
from pprint import pprint
from loguru import logger
import workYDB
from helper import *
import sys
import os
from dotenv import load_dotenv
from chat import GPT
import workGS
from workRedis import *
# import workTelegram
# import discordWork 
import asyncio

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

config = {
    'token': DISCORD_TOKEN,
    'prefix': '12',
}
intents = discord.Intents.default() # Подключаем "Разрешения"
intents.message_content = True

# bot = commands.Bot(command_prefix=config['prefix'],intents=intents)
bot = commands.Bot(command_prefix='<', intents=intents)


logger.add(sys.stderr, format="{time} {level} {message}", level="INFO")
logger.add("discord.log", rotation="50 MB")
gpt = GPT()
GPT.set_key(os.getenv('KEY_AI'))
# bot = telebot.TeleBot(os.getenv('TELEBOT_TOKEN'))
sheet = workGS.Sheet('kgtaprojects-8706cc47a185.json','Доработка AI бота Grimace')
sql = workYDB.Ydb()

URL_USERS = {}

MODEL_URL= 'https://docs.google.com/document/d/17a4WtyRxhDk3D2-Kger1eBiekBQ2BmMLTYg3e6joKDI/edit?usp=sharing'
gsText, urls_photo = sheet.get_gs_text()
# gsText = ''
# print(f'{gsText=}')
model_index=gpt.load_search_indexes(MODEL_URL, gsText=gsText) 
PROMT_URL = 'https://docs.google.com/document/d/1Oiys8iwstN4Ugjfz3pnD3LFGpHHgVHwUTp2ILjqcbsw/edit?usp=sharing'
model= gpt.load_prompt(PROMT_URL)

@bot.event
async def on_message(message):
    if message.author == bot.user:
    # if message.author != bot.user:
        return 0
        # await message.reply(message.content)
    

    global URL_USERS
    #print('это сообщение', message)
    #text = message.text.lower()
    # reply_to = message.reply_to_message
    username = message.author.name
    text = message.content.lower() 
    userID = message.author.id
    chatID = message.channel.id

    logger.debug(f'{username=}')
    logger.debug(f'{text=}')
    logger.debug(f'{chatID=}')
    logger.debug(f'{userID=}')
    # print(message.type)
    #TODO залить на сервер чтобы обрабатывал сообщения только в одном чате но возможно тогда не будет отвечать в лмчном сообшении 
    
    if chatID != 1156326501248151682:
        return 0
    
    if message.reference:
        logger.info('это реплай')
        if message.reference.resolved.author.id != bot.user.id:
            logger.info('это не боту')
            if text.find('hey ai') >= 0: 
                logger.info('есть кодовое слово')    
                text = 'hey ai ' + message.reference.resolved.content
                1+0
            elif text.find('hey ai') == -1:
                logger.info('нету кодовое слово')    
                return 0   
            
    # if message.reference and message.reference.resolved.author.id != bot.user.id:
    #     return 0 
     
    if message.reference and message.reference.resolved.author.id == bot.user.id:
        # Проверяем, что сообщение является ответом на сообщение бота
        response = 'Спасибо за ответ!'

    elif chatID == 1156326501248151682 and text.find('hey ai') == -1: 
    # elif chatID == 1157317115850805300 and text.find('?') == -1: 
        return 0
    


    try:
        payload = sql.get_payload(userID)
    except:
        row = {'id': 'Uint64', 'MODEL_DIALOG': 'String', 'TEXT': 'String'}
        sql.create_table(userID, row)
        #row = {'id': message.chat.id, 'payload': '',}
        row = {'id': userID, 'model': '', 'promt': '','nicname':username, 'payload': ''}
        sql.replace_query('user', row)

    payload = ''

    #context = sql.get_context(userID, payload)
    #if context is None or context == '' or context == []:
        #context = text
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
        await message.reply(answer)
        add_message_to_history(userID, 'assistant', answer)

        return answer
    

    add_message_to_history(userID, 'assistant', answer)
   
    prepareAnswer= answer.lower()
    #выборка 
    #logger.info(f'{message_content=}')
    try:    
        #bot.send_message(message.chat.id, answer,  parse_mode='markdown')
        # bot.reply_to(message, answer,  parse_mode='markdown')
        await message.reply(answer)
    except:
        #bot.send_message(message.chat.id, answer,)
        await message.reply(answer)
       

    now = datetime.now()+timedelta(hours=3)
    #now = datetime.now()
# Format the date and time according to the desired format
    formatted_date = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    
    #answer, allToken, allTokenPrice= gpt.answer(' ',mess,)
    row = {'all_price': float(allTokenPrice), 'all_token': int(allToken), 'all_messages': 1}
    sql.plus_query_user('user', row, f"id={userID}")
    
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
    bot.run(config['token'])




