# -*- coding: utf-8 -*-
from flask import request
from app.services.crwalling import crawling
from app.services.searchList import searchList

from openai import OpenAI
from dotenv import load_dotenv
import os

def init_routes(app):

    load_dotenv()
    GPT_API_KEY = os.getenv('GPT_API_KEY')

    client = OpenAI(api_key=GPT_API_KEY)
    my_assistant_id = "asst_9476M4WDV4us6HhNQgbdNMeC"

    @app.route('/test')
    def test():

        return 'test \n Success!!!'

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

        thread =client.beta.threads.create()
        summary_reason = item.get('summary_reason')
        summary_reason+= "\n\n 위에서 나온 내용을 알기 쉬운 말로 기승전결로 말하고 결론을 말해"

        client.beta.threads.messages.create(
            thread.id,
            role="user",
            content=summary_reason
        )
    
        run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=my_assistant_id
        )

        run_id = run.id

        while True:
            run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run_id
            )
            if run.status == "completed":
                break

        thread_messages = client.beta.threads.messages.list(thread.id)
        result_message = thread_messages.data[0].content[0].text.value

        data = {
            "thread_id": thread.id,
            "summary": result_message,
        }

        return data
    


    @app.route('/chat', methods=["POST"])
    def go_chat():

        item = request.get_json()

        thread_id = item.get('thread_id')
        message_content = item.get('message')
        client.beta.threads.messages.create(

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

