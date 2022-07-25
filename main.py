import json
import random
from typing import Union

from fastapi import Cookie, Depends, FastAPI, Query, WebSocket, status
from fastapi.responses import HTMLResponse

import db.api
from utilites.logger_utility import setup_logger

logger = setup_logger()
app = FastAPI()
# FIXME: Should only be done once, clears the database
db.api.initiate_database()
db.api.insert_question(
    question='''def multiplication(a, b):
    """This function multiplies 2 numbers"""
    return a*b''',
    answer='Feature',
    title='Multiplication',
    expl='There is not that much to say, * operator multiples 2 numbers!',
    diff=0)
db.api.insert_question(
    question='''def square_of_a_number(a):
    """This function calculates the square of a number."""
    return a ^ 2''',
    answer='Bug',
    title='Square_of_a_number',
    expl='''Almost everyone has made this mistake once! In Python `^` is the[XOR operator]
("https://docs.python.org/3/reference/expressions.html#binary-bitwise-operations") \
while the power of a number is represented by `**`.
# Corrected code
```
5 return a ** 2
```''',
    diff=0)
db.api.insert_question(
    question='''import random


def slot_machine():
    """The following simulates a slot machine with 3 entries.

    Each entry shows a number between 0 and 9.
    It will always return the numbers rolled and a message.
    If all the numbers are the same, the message is "Jackpot!",
    if 2 numbers are the same, the message is "Good roll"" and
    if they are all different, the message is "Try again, you will be luckier".
    """
    digits = range(10)
    first_n = random.choice(digits)
    second_n = random.choice(digits)
    third_n = random.choice(digits)
    roll = [first_n, second_n, third_n]
    if __all_numbers_are_the_same(roll):
        return roll, "Jackpot!"
    elif __two_numbers_are_the_same(roll):
        return roll, "Good roll!"
    else:
        return roll, "Try again, you will be luckier!"


def __all_numbers_are_the_same(numbers):
    return set(numbers) == 1


def __two_numbers_are_the_same(numbers):
    return set(numbers) == 2


print(slot_machine())''',
    answer='Bug',
    title='Slot machine',
    expl='''The first 2 conditional statements will always be False, \
we are comparing a set and an integer they will always be different!
The code can be fixed by applying a len() function to the set of each function.
Now we're comparing 2 integers as it was intended!
#### Corrected code
```
26 def all_numbers_are_the_same(numbers):
27     return len(set(numbers)) == 1
28
29
30 def two_numbers_are_the_same(numbers):
31     return len(set(numbers)) == 2
```''', diff=1)

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
            <label>Question title: <input type="text" id="newQuestionTitle" autocomplete="off"/></label>
            <label>Question explanation (shown after user has answered): <input type="text"
                   id="newQuestionExplanation" autocomplete="off"/></label>
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
                var new_question_text = document.getElementById("newQuestionText")
                var correct_answer = document.getElementById("correctAnswer")
                var new_question_title = document.getElementById("newQuestionTitle")
                var new_question_explanation = document.getElementById("newQuestionExplanation")
                const response = {
                  type: "new_question",
                  question: new_question_text.value,
                  correct_answer: correct_answer.value,
                  new_question_title: new_question_title.value,
                  new_question_explanation: new_question_explanation.value
                };
                ws.send(JSON.stringify(response))
                new_question_text.value = ''
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
        db.api.add_user(user)  # FIXME: password?
        user_uuid = db.api.get_user_by_name(user)

    return user_uuid


def process_new_question(user, event):
    """Takes in a json event and extracts fields to go into database

    Note: assumes frontend takes care of input sanitization
    """
    user_uuid = get_or_create_user(user)

    # FIXME: add difficulty to event
    difficulty = 0

    database_insert = dict(question=event['question'],
                           answer=event['correct_answer'],
                           title=event['new_question_title'],
                           expl=event['new_question_explanation'],
                           diff=difficulty)

    logger.info('Inserting %s by user uuid %s', database_insert, user_uuid)

    # FIXME: add question to user_uuid to give user a score for submitting good questions
    db.api.insert_question(**database_insert)


def process_serve_new_question(user, event):
    """Takes in a json event (content ignored for now) and requests a new question from the database"""
    # FIXME: avoid showing the same question twice
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


@ app.get("/")
async def get_main_page():
    """Returns the main html body"""
    return HTMLResponse(html)


@ app.get("/solve_quiz")
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


@ app.websocket("/solve_quiz/{item_id}/ws")
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


@ app.websocket("/new_question/{item_id}/ws")
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
