import json
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


def get_or_create_user(user: str, password: str) -> str:
    """Returns user uuid, if the user does not exist, it will be created"""
    u = db.api.get_user_by_name(user)
    if u is not None:
        if db.api.check_password(user, password):
            return u.ident
        else:
            return "wrong password"
    else:
        return db.api.add_user(user, password)


def process_new_question(event) -> str:
    """Takes in a json event and extracts fields to go into database

    Note: assumes frontend takes care of input sanitization
    """
    user_uuid = get_or_create_user(event['user_name'], event['password'])

    # FIXME: add difficulty to event
    difficulty = 0

    database_insert = dict(question=event['question'],
                           answer=event['correct_answer'],
                           title=event['new_question_title'],
                           expl=event['new_question_explanation'],
                           diff=difficulty)

    logger.info('Inserting %s by user uuid %s', database_insert, user_uuid)

    question = db.api.insert_question(**database_insert)

    # add question uuid to User, so we know who submitted it and can calculate score based on good questions
    db.api.update_user_sq_by_uuid(user_uuid, sq=str(question.ident))

    ret = "Added `{title}` to the database with UUID {unique_id}.".format(title=question.title,
                                                                          unique_id=question.ident)
    return ret


def process_serve_new_question(event) -> dict:
    """Takes in a json event, assumed to contain 'user_name' field and requests a new question from the database"""
    user_uuid = get_or_create_user(event['user_name'], event['password'])
    if user_uuid.lower() == 'already exists':
        return {'error': 'Username already exists'}
    elif user_uuid.lower() == 'wrong password':
        return {'error': 'Wrong password, nice try.'}
    try:
        result = db.api.get_new_question_for_user(user_uuid)
        result = result.__dict__
    except IndexError:
        default = 'You have answered all questions, add more to the database!'
        result = {'txt': default,
                  'title': default,
                  'expl': default,
                  'votes': 0,
                  'ident': 'INVALID'}

    logger.info('serving new question %s', result)
    return result


def process_new_answer(event) -> str:
    """Takes in a json event with a user answer and sends to database"""
    user_uuid = get_or_create_user(event['user_name'], event['password'])
    question_uuid = event['question_uuid']
    user_answer = event['user_answer']

    question = db.api.get_single_question(question_uuid)
    if question is None:
        raise Exception('Bug, could not find question corresponding to %s' % question_uuid)

    correct_answer = question.answer
    if user_answer.lower() == correct_answer.lower():
        ret = 'Correct!'
        db.api.update_user_ca_by_uuid(user_uuid, ca=question.ident)
    else:
        ret = 'Sorry, this was a "%s".' % correct_answer
        db.api.update_user_ia_by_uuid(user_uuid, ia=question.ident)

    ret += '\n%s' % question.expl

    logger.debug('process_new_answer(%s, %s, """%s""") -> %s' % (user_uuid, user_answer, question.txt, ret))
    return ret


def process_vote_question(event) -> str:
    """Takes in a json event with a user vote and sends to database,

    :returns: a dictonary with question_id and current vote.
    """
    user_uuid = get_or_create_user(event['user_name'])
    question_id = event['question_uuid']
    vote = event['vote']

    number_of_votes = db.api.update_question_votes(question_id, user_uuid, vote)

    logger.info('process_vote_question(%s, %s) -> %s' % (question_id, vote, number_of_votes))
    return {'ident': question_id, 'votes': number_of_votes}


@app.websocket("/quiz")
async def websocket_echo(
        websocket: WebSocket,
):
    """Handle all the shizz"""
    await websocket.accept()
    while True:
        try:
            data = await websocket.receive_text()
        except Exception as e:
            logger.info('receive_text failed %s', e)
            break

        logger.debug('quiz-received-data: %s', data)
        event = json.loads(data)
        event_type = event['type']
        if event_type == 'token_pls':
            await websocket.send_json(
                {
                    'type': 'auth',
                    'data': {
                        'token': secrets.token_urlsafe()
                    }
                }
            )
        elif event_type == 'insert_new_question':
            a = process_new_question(event=event['data'])
            await websocket.send_json(
                {
                    'type': 'return',
                    'data': a
                }
            )
        elif event_type == 'get_question':
            ret = process_serve_new_question(event['data'])
            await websocket.send_json(
                {
                    'type': 'serve_question',
                    'data': json.dumps(ret)
                }
            )
        elif event_type == 'answered_question':
            ret = process_new_answer(event['data'])
            await websocket.send_json(
                {
                    'type': 'answered_question_feedback',
                    'data': ret
                }
            )
        elif event_type == 'vote_question':
            ret = process_vote_question(event['data'])
            await websocket.send_json(
                {
                    'type': 'vote_feedback',
                    'data': ret
                }
            )
        else:
            logger.error('Unknown event type %s', event_type)


async def get_cookie_or_token(
    websocket: WebSocket,
    session: Union[str, None] = Cookie(default=None),
    token: Union[str, None] = Query(default=None),
):
    """Ensure we either have a valid Cookie or token"""
    if session is None and token is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
    return session or token
