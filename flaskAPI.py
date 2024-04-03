# -*- coding: utf-8 -*-

from flask import Flask, jsonify, request

from openai import OpenAI
from typing_extensions import override
import time
from dotenv import load_dotenv
import os

from crwalling import crawling
from searchList import searchList

app = Flask(__name__)

load_dotenv()
GPT_API_KEY = os.getenv('GPT_API_KEY')

gpt = "GPT_API_KEY"

client = OpenAI(api_key=GPT_API_KEY)
my_assistant_id = "asst_9476M4WDV4us6HhNQgbdNMeC"

items = [
    {"is-member":True},
    {"thread-id":"thread_wAzJJT9jY6CqXsDpBYZnN8T8"}
]

@app.route('/test')
def test():

    return 'test Success!!'

@app.route('/crawling')
def api_crawling():
    searchText = request.args.get('searchText')
    licPrec = request.args.get('licPrec')
    
    if searchText:
        result = crawling(licPrec, searchText)
        if result is not None:
            return result
        else:
            return 'Result is missing'
    else:
        return 'Prece parameter is missing'
    
@app.route('/searchList')
def api_crawling_List():
    prece = request.args.get('prece')
    if prece:
        result = searchList(prece)
        if result is not None:
            return result
        else:
            return 'Result is missing'
    else:
        return 'Prece parameter is missing'
    

@app.route('/page_init', methods=["POST"])
def chat_init():
    item = request.get_json()

    thread_id = item.get('thread_id')
    summary_reason = item.get('summary_reason')
    summary_reason += "\n\n이 이야기를 쉬운말로 압축해주고 결론으로 꼭 마무리해줘"

    # if not thread_id:
    #     print('쓰레드를 만든다!')

    # message = client.beta.threads.messages.create(
    #     thread_id,
    #     role="user",
    #     content=summary_reason
    # )
    
    # run = client.beta.threads.runs.create(
    # thread_id=thread_id,
    # assistant_id=my_assistant_id
    # )

    # run_id = run.id

    # while True:
    #     run = client.beta.threads.runs.retrieve(
    #     thread_id=thread_id,
    #     run_id=run_id
    #     )
    #     if run.status == "completed":
    #         break

    # thread_messages = client.beta.threads.messages.list(thread_id)
    # result_message = thread_messages.data[0].content[0].text.value

    # return result_message
    return summary_reason
    


@app.route('/chat', methods=['POST'])
def go_chat():

    items = request.get_json()

    thread_id = items.get('thread_id')
    message_content = items.get('message')

    message = client.beta.threads.messages.create(

        thread_id,
        role="user",
        content=message_content
    )

    run = client.beta.threads.runs.create(
    thread_id=thread_id,
    assistant_id=my_assistant_id
    )

    run_id = run.id


    while True:
        run = client.beta.threads.runs.retrieve(
        thread_id=thread_id,
        run_id=run_id
        )

        if run.status == "completed":
            thread_messages = client.beta.threads.messages.list(thread_id)
            answer_chatgpt = thread_messages.data[0].content[0].text.value
            break

        answer_chatgpt = "죄송해요!다시 한번 물어봐 주시겠어요?"

    return answer_chatgpt

           
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5001)   
