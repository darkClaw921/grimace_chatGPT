
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

# sql = workYDB.Ydb()

# logger.add(sys.stderr, format="{time} {level} {message}", level="INFO")
# logger.add("dialog.log", rotation="50 MB")
# gpt = GPT()
# GPT.set_key(os.getenv('KEY_AI'))
# bot = telebot.TeleBot(os.getenv('TELEBOT_TOKEN'))
# sheet = workGS.Sheet('kgtaprojects-8706cc47a185.json','Доработка AI бота Grimace')
# sql = workYDB.Ydb()

# URL_USERS = {}

# MODEL_URL= 'https://docs.google.com/document/d/17a4WtyRxhDk3D2-Kger1eBiekBQ2BmMLTYg3e6joKDI/edit?usp=sharing'
# ## gsText, urls_photo = sheet.get_gs_text()
# gsText = ''
# # print(f'{gsText=}')
# model_index=gpt.load_search_indexes(MODEL_URL, gsText=gsText) 
# PROMT_URL = 'https://docs.google.com/document/d/1Oiys8iwstN4Ugjfz3pnD3LFGpHHgVHwUTp2ILjqcbsw/edit?usp=sharing'
# model= gpt.load_prompt(PROMT_URL)

# selectBot ={
#     'telegram': workTelegram.bot,
#     'discord': discordWork.client,
# }

class Bot:
    botType = None
    botClass = None
    # def __init__(self,botType:selectBot):
    #     self.botType = botType
    #     self.botClass = selectBot[botType]
    def __init__(self,botType):
        self.botType = botType
        pass
        

    # def send_message(self,chatID=None, userID=None, text=None):
    async def send_message(self,messageBody):
        pass

    async def reply_to(self,messageBody, botBody):
        if self.botType == 'discord':
            chatID = messageBody.channel.id
            channel = botBody.get_channel(chatID)
            print(f'{channel=}')
            # user.send('asd')
            await channel.send('hello')
            #messageBody.author.send('👋')
            # messageBody.reply(messageBody.content)
        pass

    async def send_media_group(self):
        pass

# bot = Bot('discord')
# bot.send_message('')

@logger.catch
# def any_message(text, userID, chatID, username, reply_to=None):
def any_message(botType,botBody, messageBody):
    global URL_USERS
    #print('это сообщение', message)
    #text = message.text.lower()
    # reply_to = message.reply_to_message
    username = username
    text = text
    chatID = chatID

    logger.debug(f'{username=}')
    logger.debug(f'{text=}')
    logger.debug(f'{chatID=}')
    
    # if reply_to is not None:
    #     return 0 
    #pprint(reply_to)
    
    # if chatID < 0 and text.find('?') == -1:
    #     return 0 


    try:
        payload = sql.get_payload(userID)
    except:
        row = {'id': 'Uint64', 'MODEL_DIALOG': 'String', 'TEXT': 'String'}
        sql.create_table(userID, row)
        #row = {'id': message.chat.id, 'payload': '',}
        row = {'id': userID, 'model': '', 'promt': '','nicname':username, 'payload': ''}
        sql.replace_query('user', row)

    payload = ''


    if payload == 'addmodel':
        text = text.split(' ')
        rows = {'model': text[1], 'url': text[0] }
        #sql.insert_query('model',rows)
        sql.replace_query('model',rows)
        return 0
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
        # bot.send_message(message.chat.id, answer)
        add_message_to_history(userID, 'assistant', answer)

        return [answer]
    

    add_message_to_history(userID, 'assistant', answer)
   
    prepareAnswer= answer.lower()
    b = prepareAnswer.find('спасибо за предоставленный номер') 
    b1 = prepareAnswer.find('наш менеджер свяжется с вами') 
    b2 = prepareAnswer.find('за предоставленный номер')
    print(f'{b=}')

    #выборка 
    #logger.info(f'{message_content=}')
    try:    
        #bot.send_message(message.chat.id, answer,  parse_mode='markdown')
        bot.reply_to(message, answer,  parse_mode='markdown')
    except:
        #bot.send_message(message.chat.id, answer,)
        bot.reply_to(message, answer,)
    media_group = []
    photoFolder = -1

    if answer.find('КД-') >= 0:
        #photoFolder = message_content[0].page_content.find('https://drive') 
        #logger.info(f'{photoFolder=}')
        photoFolder = 1

    if photoFolder >= 0:
        logger.info(f'{URL_USERS=}')
        pattern = r"КД-\d+"

        matches = re.findall(pattern, answer)
        matches = list(set(matches))
        #TODO удалить если нужно чтобы фото отправлялись по 1 разу
        #URL_USERS={}
        #TODO переделать чтобы один раз отвечал

        isSendMessage = True
        trueList = []
        for project in matches:
            if URL_USERS == {}: 
                trueList.append(False) 
                break
            try:
                url = urls_photo[project]
            except:
                continue
            try:
                a = url in URL_USERS[userID]
                trueList.append(a)
            except:
                trueList.append(False)
                break

        if all(trueList): isSendMessage = False
        if isSendMessage: bot.send_message(message.chat.id, 'Подождите, ищу фото проектов...',  parse_mode='markdown')

        for project in matches:
            #media_group.extend(media_group1)
            try:
                url = urls_photo[project]
                URL_USERS, media_group,nameProject = download_photo(url,URL_USERS,userID,)
                if media_group == []:
                    continue
                bot.send_message(message.chat.id, f'Отправляю фото проекта {nameProject}...',  parse_mode='markdown')
                bot.send_media_group(message.chat.id, media_group,)
            except Exception as e:
                bot.send_message(message.chat.id, f'Извините, не могу найти актуальные фото {project}',  parse_mode='markdown') 
                logger.error(e)
        
        if media_group != []:
            if len(matches) == 1: 
                mes = 'Вам понравился проект?'
            else:
                mes = 'Какой проект Вам понравился?'
            bot.send_message(message.chat.id, mes,  parse_mode='markdown')
    
    if b >= 0 or b1>=0 or b2>=0:
        print(f"{prepareAnswer.find('cпасибо за предоставленный номер')=}")
        PROMT_SUMMARY = gpt.load_prompt(PROMT_URL_SUMMARY)
        history = get_history(str(userID))
        history_answer = gpt.answer(PROMT_SUMMARY,history)[0]
        print(f'{history_answer=}')
        print(f'{answer=}')
        #bot.send_message(message.chat.id, answer)
        phone = slice_str_phone(history_answer)
        pprint(f"{phone=}")
        
        print('запиь в битрикс')
        update_deal(phone, history_answer)

    #try:
    #    bot.send_media_group(message.chat.id, media_group)
    #except Exception as e:
    #    bot.send_message(message.chat.id, e,  parse_mode='markdown')

    #if payload == 'model3':
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


# @app.route('/summary')
# def create_sum_all_dealog():
#     gpt.summari_all_dialog()


if __name__ == '__main__':
    import threading
    import multiprocessing

    flask_thread = threading.Thread(target=app.run(host='0.0.0.0',port='5006',debug=False))
    telebot_thread = threading.Thread(target=bot.infinity_polling())

    flask_process = multiprocessing.Process(target=flask_thread.start)
    telebot_process = multiprocessing.Process(target=telebot_thread.start)

    flask_process.start()
    telebot_process.start()
    print(f'[OK]')