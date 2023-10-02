import requests
import requests, json
from pprint import pprint
token = 'secret_vDGlOnviQsHbbQiERTXZylKPAuSEjeyHfz0ZqQoJuTL'
databaseID ="56b7c3ec37c447c0b14ee5b6dc4541d9"
# databaseID ="56b7c3ec37c447c0b14ee5b6dc4541d9"
headers = {
"Authorization": "Bearer " + token,
"Content-Type": "application/json",
"Notion-Version": "2022-02-22"}

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

def create_page(page_id:str, ):
    json_data = {
        'parent': {
            # 'database_id': 'a6b32907e0094c01970d64279cf7897a',
            'page_id': page_id,
        },
        # 'cover': {
        #     'external': {
        #         'url': 'https://upload.wikimedia.org/wikipedia/commons/6/62/Tuscankale.jpg',
        #     },
        # },
        "properties": {
            "title": [
                {
                "type": "text",
                "text": {
                    "content": "Саммари на 23.09.2230",
                    "link": None
                },
            }
        ]
        }
    }



    response = requests.post('https://api.notion.com/v1/pages', headers=headers, json=json_data)
    url=eval(response.text.replace(':null', ':None').replace(':false',':False'))
    return url['url'], url['id']



urld,blockID = create_page('a6b32907e0094c01970d64279cf7897a')
add_content_to_page(blockID,'test')

