import json
import random
import secrets
from typing import Union

import psycopg
from fastapi import Cookie, Depends, FastAPI, Query, WebSocket, status
from fastapi.responses import HTMLResponse

import db.api
from utilites.logger_utility import setup_logger


def __read_file(file_path):
    with open(file_path, 'r') as file:
        file_as_string = file.read()
    return file_as_string


logger = setup_logger()
app = FastAPI()
# FIXME: Should only be done once, clears the database
db.api.initiate_database()
problems_keywords = [("problem_1_multiplication.py", 'Feature', 'Multiplication', "problem_1_explanation.md", 0),
                     ("problem_2_square_of_a_number.py", 'Bug', 'Square of a number', "problem_2_explanation.md", 0),
                     ("problem_3_slot_machine.py", 'Bug', 'Slot machine', "problem_3_explanation.md", 1),
                     ("problem_4_double_base_palindrome.py", 'Bug', 'Double base palindrome',
                      "problem_4_explanation.md", 1),
                     ("problem_5_count_ways_to_make_number.py", 'Feature',
                      'Count Ways to make a number', "problem_5_explanation.md", 2)
                     ]

for script, answer, title, explanation, difficulty in problems_keywords:
    script = __read_file(f"problems/scripts/{script}")
    explanation = __read_file(f"problems/explanations/{explanation}")
    try:
        db.api.insert_question(script, answer, title, explanation, difficulty)
    except psycopg.errors.StringDataRightTruncation as e:
        logger.error('Too long! %s, script=%s, answer=%s, title=%s, explanation=%s, difficulty=%s',
                     e, script, answer, title, explanation, difficulty)

# FIXME: move to App.js
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
            <div id='solveQuestionTitle'></div>
            <div id='solveQuestionText'></div>

            <div style="display:none;" id='solveQuestionUUID'></div>
            <label>Answer: <input type="text" id="userAnswer" autocomplete="off"/></label>
            <div id='answerFeedbackText'></div>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
        console.log("Starting")
        var ws = null;
        ws = new WebSocket("ws://localhost:8000/ws")
        ws.onopen = function(event) {
            const request = {
              type: "serve_new_question",
            };
            ws.send(JSON.stringify(request))
          };

        var solve_question_text  = document.getElementById("solveQuestionText")
        var solve_question_title = document.getElementById("solveQuestionTitle")
        var answer_feedback_text = document.getElementById("answerFeedbackText")
        var solve_question_uuid = document.getElementById("solveQuestionUUID")
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
                solve_question_title.innerHTML = data_parsed.title
                solve_question_text.innerHTML = data_parsed.txt
                solve_question_uuid.innerHTML = data_parsed.uuid
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
            const response = {
              type: "new_answer",
              question_uuid: solve_question_uuid.innerHTML,
              user_answer: input.value,
            };
            ws.send(JSON.stringify(response))
            input.value = ''

        }

        </script>
    </body>
</html>
"""


def get_or_create_user(user):
    """Returns user uuid, if the user does not exist, it will be created"""
    u = db.api.get_user_by_name(user)
    if u is not None:
        user_uuid = u.ident
    else:
        user_uuid = db.api.add_user(user)  # FIXME: password?

    return user_uuid


def process_new_question(event) -> str:
    """Takes in a json event and extracts fields to go into database

    Note: assumes frontend takes care of input sanitization
    """
    user_uuid = get_or_create_user(event['user'])

    # FIXME: add difficulty to event
    difficulty = 0

    database_insert = dict(question=event['question'],
                           answer=event['correct_answer'],
                           title=event['new_question_title'],
                           expl=event['new_question_explanation'],
                           diff=difficulty)

    logger.info('Inserting %s by user uuid %s', database_insert, user_uuid)

    # FIXME: add question to user_uuid to give user a score for submitting good questions
    return db.api.insert_question(**database_insert)


def process_serve_new_question(user, event):
    """Takes in a json event (content ignored for now) and requests a new question from the database"""
    # FIXME: avoid showing the same question twice
    # user_uuid = get_or_create_user(user)
    result = db.api.get_all_questions()  # FIXME: avoid fetching for all questions

    ret = dict(txt='This is a question, pretend it is nicely formatted',
               title='Question Title',
               uuid='Default')
    # FIXME: Add difficulty
    if len(result) > 0:
        combined = random.choice(result)
        ret = dict(txt=combined.txt,
                   title=combined.title,
                   uuid=combined.ident)

    logger.info('serve_new_question -> %s', ret)
    return ret


def process_new_answer(user, event):
    """Takes in a json event with a user answer and sends to database"""
    # user_uuid = get_or_create_user(user)
    question_uuid = event['question_uuid']

    question = db.api.get_question(question_uuid)
    if question is None:
        raise Exception('Bug, could not find question corresponding to %s' % question_uuid)

    user_answer = event['user_answer']
    correct_answer = question.answer

    if user_answer.lower() == correct_answer.lower():
        ret = 'Correct!'
    else:
        ret = 'Sorry, this was a "%s".' % correct_answer

    ret += '\n%s' % question.expl

    # FIXME: update user, with both correct and incorrect answers

    logger.info('process_new_answer(%s, %s, """%s""") -> %s' % (user, user_answer, question.txt, ret))
    return ret


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


@app.websocket("/quiz")
async def websocket_echo(
        websocket: WebSocket,
):
    """Handle all the shizz"""
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        logger.debug('quiz-received-data: %s', data)
        event = json.loads(data)
        if event['type'] == 'token_pls':
            await websocket.send_json(
                {
                    'type': 'auth',
                    'data': {
                        'token': secrets.token_urlsafe()
                    }
                }
            )
        elif event['type'] == 'new_question':
            print(event['data'])
            a = process_new_question(event=event['data'])
            await websocket.send_json(
                {
                    'type': 'return',
                    'data': a
                }
            )


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
            d = dict(type="solve_question_text")
            d.update(new_question)

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
