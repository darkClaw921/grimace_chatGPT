
import json
import requests
from pprint import pprint
token = 'secret_vDGlOnviQsHbbQiERTXZylKPAuSEjeyHfz0ZqQoJuTL'
dateBaseID = 'fc4ee3fee3bd45af8cdb75992051cc7a'
tokenv2 = 'v02%3Auser_token_or_cookies%3AcoieB6y5s4pJ8UPst0ppC-WprwV2zvYC9fIiG8Zy1K4TkDSdBe5Az1h4g5udud1uOzgxhRONKiKHICTvcbT_BP-pjauvNAyNMZqqiZJax4q_kmabe6VCSqrwbWHlbZROwN7P'
from notion.client import NotionClient

from notion.block import TodoBlock, TextBlock, ColumnBlock


# # Obtain the `token_v2` value by inspecting your browser cookies on a logged-in (non-guest) session on Notion.so
# client = NotionClient(token_v2=tokenv2)

# cv = client.get_collection_view("https://www.notion.so/56b7c3ec37c447c0b14ee5b6dc4541d9?v=7ae17d16a0d141c8953615f7153b1c11")
# print(cv.name)
# row = cv.collection.add_row()
# row.name = "https://www.notion.so/summary-Bot-a6b32907e0094c01970d64279cf7897a"
# row.text = 'a12s'
# row.tags = ["A", "C"]


def create_page(date,text):
    # Initialisation
    import requests, json
    token = 'secret_vDGlOnviQsHbbQiERTXZylKPAuSEjeyHfz0ZqQoJuTL'
    databaseID ="56b7c3ec37c447c0b14ee5b6dc4541d9"
    headers = {
    "Authorization": "Bearer " + token,
    "Content-Type": "application/json",
    "Notion-Version": "2022-02-22"
}
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
                            "content": f"{date}"
                        }
                    }
                ]
            },
            "Text": {
                    "rich_text": [
                        {
                            "text": {
                                "content": text
                            },
                        }
                    ]
                },
    
            }
        }
    data = json.dumps(newPageData)
    res = requests.request("POST", createUrl, headers=headers, data=data)
    print(res.text)


if __name__ == '__main__':
    create_page('18-32-24','test txt')