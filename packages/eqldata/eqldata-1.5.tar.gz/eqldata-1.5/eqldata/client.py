import json
import requests
from websocket import create_connection
import time

class DataClient:
    def __init__(self, auth_token, topics):
        self.uri = 'wss://api.equalsolution.net'
        self.headers = {"token": auth_token}
        self.topics = topics
        self.websocket = None
        self.is_listening = False

        self._start()

    def _start(self):
        self.connect()
        self.subscribe_to_topics(self.topics)

    def connect(self):
        self.websocket = create_connection(self.uri, header=self.headers)
        login_response = self.websocket.recv()
        try:
            login_data = json.loads(login_response)
            if login_data.get("status") == "Successfully Login!":
                print(login_response)
                return True
        except json.JSONDecodeError as e:
            print("JSON decode error:", e)
        return False

    def subscribe_to_topics(self, topics):
        if self.websocket is not None:
            subscribe_request = {
                "action": "subscribe",
                "topics": topics
            }
            self.websocket.send(json.dumps(subscribe_request))
        else:
            raise ValueError("WebSocket connection is not established.")

    def listen(self):
        while True:
            try:
                response = self.websocket.recv()
                if response is not None:
                    return response
            except Exception as e:
                print("Error:", e)
                self.reconnect()

    def reconnect(self):
        print("Connection lost. Reconnecting...")
        self.disconnect()
        time.sleep(5)  # Wait for a moment before reconnecting
        self.connect()

    def stop_listening(self):
        self.is_listening = False

    def disconnect(self):
        if self.websocket:
            self.websocket.close()

def generate_auth_token(username, password):
    auth_url = 'https://rt.equalsolution.net/client/client_api_tocken'
    payload = {
        'email': username,
        'password': password
    }
    response = requests.post(auth_url, json=payload)
    if response.status_code == 200:
        return response.json().get('token')
    else:
        return response.json().get('detail')

def get_instrument_list(auth_token):
    instrument_url = 'https://rt.equalsolution.net/client/get_instrument/'
    headers = {
        'Authorization': f'Bearer {auth_token}'
    }
    response = requests.post(instrument_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return response.json().get('detail')
