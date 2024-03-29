# -*- coding: utf-8 -*-

from flask import Flask, jsonify, request

from openai import OpenAI
from typing_extensions import override
import time
from dotenv import load_dotenv
import os


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

@app.route('/test5')
def test5():
    return 'gpt key : ' + gpt

@app.route('/testsec')
def testpsec():
    return 'test2 success!!!'

@app.route('/page_init', methods=["POST"])
def chat_init():
    item = request.get_json()
    print(item) 

    thread_id = item[0].get('thread_id')
    summary_reason = item[1].get('summary_reason')
    summary_reason += "\n\n이 이야기를 쉬운말로 압축해주고 결론으로 꼭 마무리해줘"

    print(thread_id)

    if not thread_id:
        print('쓰레드를 만든다!')

    message = client.beta.threads.messages.create(
        thread_id,
        role="user",
        content=summary_reason
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
            break
        else:
            print("로딩중..")
            time.sleep(2)

    thread_messages = client.beta.threads.messages.list(thread_id)
    print(thread_messages.data[0].content[0].text.value)
    result_message = thread_messages.data[0].content[0].text.value

    return result_message
    


@app.route('/chat', methods=['POST'])
def go_chat():

    items = request.get_json()

    print(items)

    thread_id = items.get('thread_id')
    message_content = items.get('message')

    print(thread_id)
    print(message_content)

    # message = client.beta.threads.messages.create(

    #     thread_id,
    #     role="user",
    #     content=message_content
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
    #     else:
    #         print("로딩중..")
    #         time.sleep(2)


    # thread_messages = client.beta.threads.messages.list(thread_id)
    # print(thread_messages.data[0].content[0].text.value)

    # answer_chatgpt = thread_messages.data[0].content[0].text.value

    # return answer_chatgpt

    return '메세지 : ' + message_content 

           
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5001)
