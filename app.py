import os
import re
from datetime import datetime

import requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from openai import OpenAI

app = Flask(__name__)
load_dotenv()

WEBEX_BOT_TOKEN = os.getenv('WEBEX_BOT_TOKEN')
WEBEX_BOT_EMAIL = os.getenv('WEBEX_BOT_EMAIL')
ASSISTANT_ID = os.getenv('ASSISTANT_ID')
WEBEX_URL = 'https://webexapis.com/v1/messages'

threads = []

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.json
    message_id = req['data'].get('id')
    room_id = req['data'].get('roomId')
    person_email = req['data']['personEmail']

    if not req or 'data' not in req or 'personEmail' not in req['data']:
        return jsonify({'message': 'Invalid data received'}), 400

    if person_email.lower() == WEBEX_BOT_EMAIL.lower():
        return jsonify({'message': 'Message from self ignored'}), 200

    message_details_response = requests.get(f'{WEBEX_URL}/{message_id}',
                                            headers={'Authorization': f'Bearer {WEBEX_BOT_TOKEN}'})
    if message_details_response.status_code != 200:
        return jsonify({'error': 'Failed to fetch message content from Webex',
                        'details': message_details_response.text}), 500
    message_content = message_details_response.json().get('text')
    if not message_content:
        return jsonify({'error': 'No text content in message'}), 400
    print(message_content)
    client = OpenAI()
    thread = None
    for t in threads:
        if t['person_email'] == person_email:
            thread = t['thread']
            break
    if not thread:
        thread = client.beta.threads.create()
        threads.append({'person_email': person_email, 'thread': thread, 'startTime': datetime.now()})
    print(threads)
    try:
        message_for_gpt = client.beta.threads.messages.create(
            thread_id=thread.id,
            role='user',
            content=message_content
        )
        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=ASSISTANT_ID,
        )
        if run.status == 'completed': 
            messages = client.beta.threads.messages.list(
                thread_id=thread.id
            )
            assistant_messages = [msg for msg in messages.data if msg.role == 'assistant']

            if assistant_messages:
                first_assistant_message = assistant_messages[0]
                text_blocks = [content for content in first_assistant_message.content if content.type == 'text']
                if text_blocks:
                    assistant_response = re.sub(r'\*\*(.*?)\*\*', r'\1', text_blocks[0].text.value)
                    print("Assistant's Response:", assistant_response)
                else:
                    print("No text content found in the assistant's message.")
            else:
                print("No messages from the assistant found.")

        else:
            print(run.status)
    except Exception as e:
        print(f'Error with OpenAI: {str(e)}')  # Make sure this is being logged
        return jsonify({'error': 'Failed to communicate with OpenAI',
                        'details': str(e)}), 500

    # Send response back to Webex
    headers = {'Authorization': f'Bearer {WEBEX_BOT_TOKEN}',
               'Content-Type': 'application/json'}
    payload = {'roomId': room_id, 'text': assistant_response if assistant_response else 'No response from assistant'}
    response = requests.post(WEBEX_URL, headers=headers, json=payload)
    if response.status_code != 200:
        return jsonify({'error': 'Failed to send message to Webex',
                        'details': response.text}), 500

    return jsonify({'message': 'Response sent to Webex'}), 200

if __name__ == '__main__':
    app.run(port=5001)
