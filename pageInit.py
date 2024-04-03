# -*- coding: utf-8 -*-

from openai import OpenAI
from typing_extensions import override
import time
from dotenv import load_dotenv
import os

from crwaling import crawling
from searchList import searchList


load_dotenv()
GPT_API_KEY = os.getenv('GPT_API_KEY')

gpt = "GPT_API_KEY"

client = OpenAI(api_key=GPT_API_KEY)
my_assistant_id = "asst_9476M4WDV4us6HhNQgbdNMeC"
thread_id_sample = "thread_wAzJJT9jY6CqXsDpBYZnN8T8"

def page_init(contents):

    thread_id = thread_id_sample
    summary_reason = contents
    summary_reason += "\n\n이 이야기를 쉬운말로 압축해주고 결론으로 꼭 마무리해줘"

    if not thread_id:
        print('쓰레드를 만든다!')

    client.beta.threads.messages.create(
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
    result_message = thread_messages.data[0].content[0].text.value

    return result_message