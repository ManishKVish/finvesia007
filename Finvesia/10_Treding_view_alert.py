from flask import Flask, request
import requests

app = Flask(__name__)

@app.route('/tradingview', methods=['GET','POST'])
def receive_webhook():
    alert_data = request.get_json()
    symbol = alert_data['symbol']
    message = alert_data['message']
    print("symbol "+ symbol+ " "+message)
   # process_alert(alert_data)  # Call a function to process the alert data
    return 'OK'


@app.route('/1', methods=['GET'])
def get_resource():
    # Logic to fetch the resource
    return 'ok'

if __name__ == '__main__':
    app.run()

def process_alert(alert_data):
    # Extract relevant information from alert_data
    symbol = alert_data['symbol']
    message = alert_data['message']
    print("symbol "+ symbol+ " "+message)

    # Send message to Telegram using bot token
    bot_token = 'YOUR_BOT_TOKEN'
    chat_id = 'YOUR_CHAT_ID'
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    params = {'chat_id': chat_id, 'text': f'{symbol}: {message}'}
    response = requests.post(url, json=params)

    if response.status_code == 200:
        print('Message sent successfully to Telegram.')
    else:
        print('Failed to send message to Telegram.')
