import os
from locust import User, task, events
from locust.env import Environment
from locust.runners import STATE_STOPPING, STATE_STOPPED, STATE_CLEANUP
from websocket import create_connection
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

WS_URL = os.getenv("WS_URL", "ws://localhost:8080/ws")

class WebSocketUser(User):
    abstract = True

    def on_start(self):
        self.ws = create_connection(WS_URL)

    def on_stop(self):
        self.ws.close()

class ChatUser(WebSocketUser):
    @task
    def send_and_receive(self):
        msg = "hello from locust"
        self.ws.send(msg)
        _ = self.ws.recv()

# Graceful shutdown for WebSocket connections
@events.test_stop.add_listener
def _(environment, **kwargs):
    for user in environment.runner.user_classes:
        if hasattr(user, 'ws'):
            try:
                user.ws.close()
            except Exception:
                pass
