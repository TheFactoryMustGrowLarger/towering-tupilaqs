import json
import logging
from typing import Union

from fastapi import Cookie, Depends, FastAPI, Query, WebSocket, status
from fastapi.responses import HTMLResponse

import database


def setup_logger():
    """Returns logging object that streams to file"""
    logger = logging.getLogger('tupilaqs')
    logger.setLevel(logging.DEBUG)

    ch = logging.FileHandler('tupilaqs.log')
    ch.setLevel(logging.DEBUG)
    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # add formatter to ch
    ch.setFormatter(formatter)
    # add ch to logger
    logger.addHandler(ch)
    return logger


logger = setup_logger()
app = FastAPI()

# FIXME: Should be changed to serve the frontend index.html
html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="newQuestion(event)">
            <label>Username: <input type="text" id="itemId" autocomplete="off" value="foo"/></label>
            <label>Password: <input type="text" id="token" autocomplete="off" value="some-key-token"/></label>
            <button onclick="connect(event)">Connect</button>
            <hr>
            <label>Question: <input type="text" id="questionText" autocomplete="off"/></label>
            <label>Correct answer: <input type="text" id="correctAnswer" autocomplete="off"/></label>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
        var ws = null;
            function connect(event) {
                var itemId = document.getElementById("itemId")
                var token = document.getElementById("token")
                ws = new WebSocket("ws://localhost:8000/items/" + itemId.value + "/ws?token=" + token.value);
                ws.onmessage = function(event) {
                    var messages = document.getElementById('messages')
                    var message = document.createElement('li')
                    var content = document.createTextNode(event.data)
                    message.appendChild(content)
                    messages.appendChild(message)
                };
                event.preventDefault()
            }
            function newQuestion(event) {
                var input = document.getElementById("questionText")
                var correct_answer = document.getElementById("correctAnswer")
                const response = {
                  type: "new_question",
                  question: input.value,
                  correct_answer: correct_answer.value,
                };
                ws.send(JSON.stringify(response))
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


def process_new_question(user, event):
    """Takes in a json event and extracts fields to go into database"""
    # FIXME: where do we Sanitize the input? (frontend/here/database?)
    return database.add_new_question(user,
                                     event['question'],
                                     event['correct_answer'])


@app.get("/")
async def get():
    """Returns the main html body"""
    return HTMLResponse(html)


async def get_cookie_or_token(
    websocket: WebSocket,
    session: Union[str, None] = Cookie(default=None),
    token: Union[str, None] = Query(default=None),
):
    """Ensure we either have a valid Cookie or token"""
    if session is None and token is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
    return session or token


@app.websocket("/items/{item_id}/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    item_id: str,
    q: Union[int, None] = None,
    cookie_or_token: str = Depends(get_cookie_or_token),
):
    """Responds to messages posted by user by echoing them back with the token_id"""
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        logger.debug('received %s', data)
        await websocket.send_text(
            f"Session cookie or query token value is: {cookie_or_token}"
        )
        if q is not None:
            await websocket.send_text(f"Query parameter q is: {q}")
        await websocket.send_text(f"Message text was: {data}, for item ID: {item_id}")

        event = json.loads(data)
        if event['type'] == 'new_question':
            process_new_question(user=item_id, event=event)
