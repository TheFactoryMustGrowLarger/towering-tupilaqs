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
        <title>WebSocket Quiz - Bug, Feature or Tupilaqs</title>
    </head>
    <body>
        <h1>WebSocket Quiz - Bug, Feature or Tupilaqs</h1>
        <h2>Add new question</h1>
        <form action="" onsubmit="addNewQuestion(event)">
            <label>Username: <input type="text" id="itemId" autocomplete="off" value="foo"/></label>
            <label>Password: <input type="text" id="token" autocomplete="off" value="some-key-token"/></label>
            <button onclick="connect(event)">Connect</button>
            <hr>
            <label>New Question: <input type="text" id="newQuestionText" autocomplete="off"/></label>
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
                ws = new WebSocket("ws://localhost:8000/new_question/" + itemId.value + "/ws?token=" + token.value);
                ws.onmessage = function(event) {
                    console.log(event.data)
                    const data_parsed = JSON.parse(event.data)
                    switch (data_parsed.type) {
                      default:
                        var messages = document.getElementById('messages')
                        var message = document.createElement('li')
                        var content = document.createTextNode(data_parsed.data)
                        message.appendChild(content)
                        messages.appendChild(message)
                  }
                };
                event.preventDefault()
            }
            function addNewQuestion(event) {
                var input = document.getElementById("newQuestionText")
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

# Copy-paste for the quiz page
html_quiz_solve_page = """
<!DOCTYPE html>
<html>
    <head>
        <title>WebSocket Quiz - Bug, Feature or Tupilaqs</title>
    </head>
    <body>
        <h1>WebSocket Quiz - Bug, Feature or Tupilaqs</h1>
        <form action="" onsubmit="solveQuiz(event)">
            <label>Username: <input type="text" id="itemId" autocomplete="off" value="foo"/></label>
            <label>Password: <input type="text" id="token" autocomplete="off" value="some-key-token"/></label>
            <button onclick="connect(event)">Connect</button>
            <hr>
            <div id='solveQuestionText'></div>
            <label>Answer: <input type="text" id="userAnswer" autocomplete="off"/></label>
            <div id='answerFeedbackText'></div>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
        console.log("Starting")
        var ws = null;
        var solve_question_text  = document.getElementById("solveQuestionText")
        var answer_feedback_text = document.getElementById("answerFeedbackText")
        solve_question_text.innerHTML = "This is a question, pretend it is nicely formatted python code"

        function connect(event) {
          event.preventDefault()
          var itemId = document.getElementById("itemId")
          var token = document.getElementById("token")
          ws = new WebSocket("ws://localhost:8000/solve_quiz/" + itemId.value + "/ws?token=" + token.value);
          ws.onopen = function(event) {
            const request = {
              type: "serve_new_question",
            };
            ws.send(JSON.stringify(request))
          };

          ws.onmessage = function(event) {
            event.preventDefault()
            console.log(event.data)
            const data_parsed = JSON.parse(event.data)
            switch (data_parsed.type) {
              case "solve_question_text":
                solve_question_text.innerHTML = data_parsed.data
                break;
              case "answer_feedback_text":
                answer_feedback_text.innerHTML = data_parsed.data
                break;
              default:
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(data_parsed.data)
                message.appendChild(content)
                messages.appendChild(message)
            }
          };
        }

        function solveQuiz(event) {
            event.preventDefault()
            var input = document.getElementById("userAnswer")
            var question = document.getElementById("solveQuestionText")
            const response = {
              type: "new_answer",
              question: question.innerHTML,
              user_answer: input.value,
            };
            ws.send(JSON.stringify(response))
            input.value = ''

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


def process_serve_new_question(user, event):
    """Takes in a json event (content ignored for now) and requests a new question from the database"""
    question, correct_answer = database.serve_new_question(user)
    # FIXME: keep track of answer?
    return question


def process_new_answer(user, event):
    """Takes in a json event with a user answer and sends to database"""
    return database.record_user_answer(user,
                                       question=event['question'],
                                       answer=event['user_answer'])


@app.get("/")
async def get_main_page():
    """Returns the main html body"""
    return HTMLResponse(html)


@app.get("/solve_quiz")
async def get_quiz_page():
    """Returns the quiz html body,

    where the user solves the questions presented
    """
    return HTMLResponse(html_quiz_solve_page)


async def get_cookie_or_token(
    websocket: WebSocket,
    session: Union[str, None] = Cookie(default=None),
    token: Union[str, None] = Query(default=None),
):
    """Ensure we either have a valid Cookie or token"""
    if session is None and token is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
    return session or token


@app.websocket("/solve_quiz/{item_id}/ws")
async def websocket_endpoint_quiz(
    websocket: WebSocket,
    item_id: str,
    q: Union[int, None] = None,
    cookie_or_token: str = Depends(get_cookie_or_token),
):
    """Responds to messages posted by user by echoing them back with the token_id"""
    await websocket.accept()
    while True:
        try:
            data = await websocket.receive_text()
        except Exception as e:
            logger.exception('receive_text failed: %s', e)
            break

        logger.debug('received %s', data)

        # Parse what the frontend sent
        event = json.loads(data)
        if event['type'] == 'serve_new_question':
            # Fetch a new question from database and send back to frontend
            new_question = process_serve_new_question(user=item_id, event=event)
            d = dict(type="solve_question_text", data=new_question)
            await websocket.send_json(d)
        elif event['type'] == 'new_answer':
            # User has submitted a result, return if the result is correct or not
            feedback = process_new_answer(user=item_id, event=event)
            d = dict(type="answer_feedback_text", data=feedback)
            await websocket.send_json(d)
        else:
            logger.error('Unrecognized type "%s"', event['type'])


@app.websocket("/new_question/{item_id}/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    item_id: str,
    q: Union[int, None] = None,
    cookie_or_token: str = Depends(get_cookie_or_token),
):
    """Responds to new_question events from the frontend, sending the recieved data into the database"""
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        logger.debug('received %s', data)

        # For debug, echo back (TODO: Remove)
        d = dict(type="cookie", data=f"Session cookie or query token value is: {cookie_or_token}")
        await websocket.send_json(d)

        if q is not None:
            d = dict(type="query", data=f"Query parameter q is: {q}")
            await websocket.send_json(d)

        d = dict(type="message", data=f"Message text was: {data}, for item ID: {item_id}")
        await websocket.send_json(d)

        # Parse what the frontend sent
        event = json.loads(data)
        if event['type'] == 'new_question':
            process_new_question(user=item_id, event=event)
