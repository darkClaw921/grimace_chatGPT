
import json
import requests
from pprint import pprint
token = 'secret_vDGlOnviQsHbbQiERTXZylKPAuSEjeyHfz0ZqQoJuTL'
dateBaseID = 'fc4ee3fee3bd45af8cdb75992051cc7a'
tokenv2 = 'v02%3Auser_token_or_cookies%3AcoieB6y5s4pJ8UPst0ppC-WprwV2zvYC9fIiG8Zy1K4TkDSdBe5Az1h4g5udud1uOzgxhRONKiKHICTvcbT_BP-pjauvNAyNMZqqiZJax4q_kmabe6VCSqrwbWHlbZROwN7P'
from notion.client import NotionClient

from notion.block import TodoBlock, TextBlock


# Obtain the `token_v2` value by inspecting your browser cookies on a logged-in (non-guest) session on Notion.so
client = NotionClient(token_v2=tokenv2)

# Replace this URL with the URL of the page you want to edit
page = client.get_block("https://www.notion.so/summary-Bot-a6b32907e0094c01970d64279cf7897a")
newchild = page.children.add_new(TextBlock, title="Something to get done")
newchild.checked = True
# print("The old title is:", page.title)
# for child in page.children:
#     print(child.title)

    # print("Parent of {} is {}".format(page.id, page.parent.id))
# Note: You can use Markdown! We convert on-the-fly to Notion's internal formatted text data structure.
# page.title = "The title has now changed, and has *live-updated* in the browser!"