
import json
import requests
from pprint import pprint
from datetime import datetime, timezone
from dotenv import load_dotenv
import requests, json
import os
from chat import GPT
from flask_restx import Api, Resource, fields
from flask import Flask 

app = Flask(__name__)
api = Api(app, version='1.0', title='Strategies',
    description=f'Strategies API',
)

load_dotenv()


token = os.getenv('secret_notion')
# databaseID ="56b7c3ec37c447c0b14ee5b6dc4541d9"
databaseID ="44d8434d60e547e38720d7736fc3074f"
headers = {
    "Authorization": "Bearer " + token,
    "Content-Type": "application/json",
    "Notion-Version": "2022-02-22"}
gpt = GPT()
GPT.set_key(os.getenv('KEY_AI'))

def add_content_to_page(blockID:str, text:str):
    json_data = {
        'children': [
            {
                'object': 'block',
                'type': 'heading_2',
                'heading_2': {
                    'rich_text': [
                        {
                            'type': 'text',
                            'text': {
                                'content': ':',
                            },
                        },
                    ],
                },
            },
            {
                'object': 'block',
                'type': 'paragraph',
                'paragraph': {
                    'rich_text': [
                        {
                            'type': 'text',
                            'text': {
                                'content': text,
                                
                            },
                        },
                    ],
                },
            },
        ],
    }
    response = requests.patch(
        f'https://api.notion.com/v1/blocks/{blockID}/children',
        headers=headers,
        json=json_data,
    )
    pprint(response.json())

def create_page(page_id:str, title:str):
    json_data = {
        'parent': {
            # 'database_id': 'a6b32907e0094c01970d64279cf7897a',
            'page_id': page_id,
        },
        "properties": {
            "title": [
                {
                "type": "text",
                "text": {
                    "content": title,
                    "link": None
                },
            }
        ]
        }
    }

    response = requests.post('https://api.notion.com/v1/pages', headers=headers, json=json_data)
    pprint(response.json())
    url=eval(response.text.replace(':null', ':None').replace(':false',':False'))
    return url['url'], url['id']

def add_content_db(title,allQuest, url):
    # Initialisation
    
#https://www.notion.so/summary-Bot-a6b32907e0094c01970d64279cf7897a
    #https://www.notion.so/56b7c3ec37c447c0b14ee5b6dc4541d9?v=7ae17d16a0d141c8953615f7153b1c11&pvs=13
    createUrl = 'https://api.notion.com/v1/pages'
    newPageData = {
        "parent": { "database_id": databaseID },
        "properties": {
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": f"{title}",
                            "link": { "url": url }

                        }
                    }
                ]
            },
            # "Text": {
            #         "rich_text": [
            #             {
            #                 "text": {
            #                     "content": text,
            #                     # "link": { "url": "https://en.wikipedia.org/wiki/Lacinato_kale" }
            #                 },
            #             }
            #         ]
            #     },
            "Total Questions": {
                "number": allQuest 
            }
            # "Number":{
            #     "id": "23",
            #     "name": "Total Questions",
            #     "type": "number",
                
            # }
            
    
            }
        }
    data = json.dumps(newPageData)
    res = requests.request("POST", createUrl, headers=headers, data=data)
    pprint(res.json())

def date_now():
    patern = '%Y-%m-%d'
    # patern = '%Y-%m-%dT%H:%M:%S'
    current_date = datetime.now().strftime(patern)
    return current_date

def main(textSummary, allQuest):
    dateNow = date_now()
    title = f'Cаммари на {dateNow}'
    url,blockID = create_page('610743c8e17b4b498682e17cd1923ef5',title)
    # url,blockID = create_page('a6b32907e0094c01970d64279cf7897a',title)
    add_content_to_page(blockID,textSummary)
    add_content_db(f'{dateNow}',allQuest,url)

@api.route('/summary')
@api.doc(description='Делает саммари из всех сообщений в базе за этот день и отправляет в notion')
class Create_summry(Resource):
    def post(self):
        summ, allQuest = gpt.summari_all_dialog()
        # print(f'{summ=}')
        main(summ,allQuest)
        return 'OK'

if __name__ == '__main__':
    # create_page(data)
    # add_content_db('18-32-24','test txt')
    summ, allQuest = gpt.summari_all_dialog()
    # print(f'{summ=}')
    main(summ,allQuest)
    # add_content_db('test',12,'google.com')
    # add_content_to_page('5ea60083f2e044539f2f76e2c6ce2b52', 'test2')
    # main('summ',123)


    