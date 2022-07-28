import json
import random
import secrets
from typing import Union

import psycopg
from fastapi import Cookie, FastAPI, Query, WebSocket, status

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
                     ("problem_3_slot_machine.py", 'Bug', 'Slot machine', "problem_3_explanation.md", 1)]


for script, answer, title, explanation, difficulty in problems_keywords:
    script = __read_file(f"problems/scripts/{script}")
    explanation = __read_file(f"problems/explanations/{explanation}")
    try:
        db.api.insert_question(script, answer, title, explanation, difficulty)
    except psycopg.errors.StringDataRightTruncation as e:
        logger.error('Too long! %s, script=%s, answer=%s, title=%s, explanation=%s, difficulty=%s',
                     e, script, answer, title, explanation, difficulty)


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


def process_serve_new_question(event) -> list:
    """Takes in a json event (content ignored for now) and requests a new question from the database"""
    # FIXME: avoid showing the same question twice
    user_uuid = get_or_create_user(event['user_name'])
    result = db.api.get_ca_by_uuid(user_uuid)
    if len(result) > 0:
        return [i.__dict__ for i in result]

    result = db.api.get_all_questions()
    if len(result) > 0:
        return [i.__dict__ for i in result]

    return []


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
        elif event['type'] == 'insert_new_question':
            a = process_new_question(event=event['data'])
            await websocket.send_json(
                {
                    'type': 'return',
                    'data': a
                }
            )
        elif event['type'] == 'get_question':
            ret = process_serve_new_question(event['data'])
            # Only serving ONE question out of the 10 limit for testing purpose
            # Should be changed down the line?
            await websocket.send_json(
                {
                    'type': 'serve_question',
                    'data': ret[random.randrange(0, len(ret))]
                }
            )
        elif event['type'] == 'answered_question':
            # TODO:
            pass


async def get_cookie_or_token(
    websocket: WebSocket,
    session: Union[str, None] = Cookie(default=None),
    token: Union[str, None] = Query(default=None),
):
    """Ensure we either have a valid Cookie or token"""
    if session is None and token is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
    return session or token
