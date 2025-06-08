from flask import Flask, request, jsonify
import requests
import openai
import os

app = Flask(__name__)

# 設定金鑰（請於部署時改用環境變數）
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_TOKEN")
LINE_REPLY_ENDPOINT = 'https://api.line.me/v2/bot/message/reply'
openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route("/webhook", methods=['POST'])
def webhook():
data = request.get_json()
try:
for event in data['events']:
if event['type'] == 'message' and event['message']['type'] == 'text':
user_message = event['message']['text']
reply_token = event['replyToken']

gpt_response = ask_gpt(user_message)
reply_to_line(reply_token, gpt_response)
except Exception as e:
print("錯誤：", e)
return jsonify({"status": "ok"})

def ask_gpt(message):
try:
response = openai.ChatCompletion.create(
model="gpt-4",
messages=[
{"role": "system", "content": "你是鄭語皓醫師的智能助手，專業但親切，擅長回答減重與代謝醫學問題。"},
{"role": "user", "content": message}
]
)
return response['choices'][0]['message']['content'].strip()
except Exception as e:
print("GPT 錯誤：", e)
return "目前系統忙碌中，稍後回覆您。"

def reply_to_line(reply_token, text):
headers = {
"Content-Type": "application/json",
"Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
}
body = {
"replyToken": reply_token,
"messages": [
{
"type": "text",
"text": text
}
]
}
r = requests.post(LINE_REPLY_ENDPOINT, headers=headers, json=body)
print("LINE 回應：", r.status_code)

if __name__ == '__main__':
app.run(host='0.0.0.0', port=5000)
