import json

from fastapi import FastAPI, WebSocket

from db.api import TupilaqsDB
from utilites.logger_utility import setup_logger

logger = setup_logger()
app = FastAPI()
db = TupilaqsDB()


class WrongPasswordException(Exception):
    """raised if the password is incorrect"""

    def __init__(self, message='Wrong password, try again.'):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return {'error': self.message}


class InvalidQuestionIDException(Exception):
    """raised if the question ID is not found in the database, this indicates a bug."""


def get_or_create_user(user: str, password: str) -> str:
    """Returns user uuid, if the user does not exist, it will be created"""
    u = db.get_user_by_name(user)
    if u is not None:
        if db.check_password(user, password):
            return u.ident
        else:
            raise WrongPasswordException()
    else:
        return db.add_user(user, password)


def process_new_question(user_uuid, event) -> str:
    """Takes in a json event and extracts fields to go into database

    Note: assumes frontend takes care of input sanitization
    """
    assert user_uuid is not None

    # FIXME: add difficulty to event
    difficulty = 0

    database_insert = dict(question=event['question'],
                           answer=event['correct_answer'],
                           title=event['new_question_title'],
                           expl=event['new_question_explanation'],
                           diff=difficulty)

    logger.info('Inserting %s by user uuid %s', database_insert, user_uuid)

    question = db.insert_question(**database_insert)

    # add question uuid to User, so we know who submitted it and can calculate score based on good questions
    db.update_user_sq_by_uuid(user_uuid, sq=str(question.ident))

    ret = "Added `{title}` to the database with UUID {unique_id}.".format(title=question.title,
                                                                          unique_id=question.ident)
    return ret


def process_serve_new_question(user_uuid, event) -> dict:
    """Takes in a json event, assumed to contain 'user_name' field and requests a new question from the database"""
    try:
        question = db.get_new_question_for_user(user_uuid)
        result = {'txt': question.txt,
                  'title': question.title,
                  'votes': question.votes,
                  'ident': question.ident}
    except IndexError:
        result = {'txt': '',
                  'title': 'You have answered all questions, add more to the database!',
                  'votes': 0,
                  'ident': 'INVALID'}

    logger.info('serving new question %s', result)
    return result


def process_new_answer(user_uuid, event) -> str:
    """Takes in a json event with a user answer and sends to database

    :returns: a string containing user feedback (either "Correct!" or "Sorry this was a <Bug/Feature>") and
              answer explanation
    """
    assert user_uuid is not None

    question_uuid = event['question_uuid']
    user_answer = event['user_answer']

    question = db.get_single_question(question_uuid)
    if question is None:
        raise InvalidQuestionIDException('Bug, could not find question corresponding to %s' % question_uuid)

    correct_answer = question.answer
    if user_answer.lower() == correct_answer.lower():
        ret = 'Correct!'
        db.update_user_ca_by_uuid(user_uuid, ca=question.ident)
    else:
        ret = 'Sorry, this was a "%s".' % correct_answer
        db.update_user_ia_by_uuid(user_uuid, ia=question.ident)

    ret += '\n%s' % question.expl

    logger.debug('process_new_answer(%s, %s, """%s""") -> %s' % (user_uuid, user_answer, question.txt, ret))
    return ret


def process_vote_question(user_uuid, event) -> dict[str, int]:
    """Takes in a json event with a user vote and sends to database,

    :returns: a dictonary with question_id and current vote.
    """
    assert user_uuid is not None
    question_id = event['question_uuid']
    vote = event['vote']

    number_of_votes = db.update_question_votes(question_id, user_uuid, vote)

    logger.info('process_vote_question(%s, %s) -> %s' % (question_id, vote, number_of_votes))
    return {'ident': question_id, 'votes': number_of_votes}


def get_user_info(user_uuid) -> dict[str, int]:
    """Returns additional information about a user, e.g. current Score"""
    assert user_uuid is not None

    correct_answers_count = len(db.get_ca_by_uuid(user_uuid))
    incorrect_answers_count = len(db.get_ia_by_uuid(user_uuid))
    answer_count = correct_answers_count + incorrect_answers_count
    if answer_count != 0:
        user_score = 100*correct_answers_count/answer_count
        user_score_str = '{}/{} = {:.3g}%'.format(correct_answers_count,
                                                  answer_count,
                                                  user_score)
    else:
        user_score = 0
        user_score_str = '0'

    submitted_questions = db.get_sq_by_uuid(user_uuid)
    user_submitted_questions_count = len(submitted_questions)

    submitted_questions_uuids = [item.ident for item in submitted_questions]
    user_submitted_questions_votes = db.get_total_votes_questions(submitted_questions_uuids)

    ret = {'user_score': user_score_str,
           'user_submitted_questions_count': user_submitted_questions_count,
           'user_submitted_questions_votes': user_submitted_questions_votes}

    logger.info('get_user_info(%s) -> %s', user_uuid, ret)
    return ret


@app.websocket("/quiz")
async def websocket_echo(
        websocket: WebSocket,
):
    """Handle all requests from frontend"""
    await websocket.accept()
    while True:
        try:
            data = await websocket.receive_text()
        except Exception as e:
            logger.info('receive_text failed %s', e)
            break

        logger.debug('quiz-received-data: %s', data)
        event = json.loads(data)
        user_uuid = None
        if 'data' in event and 'password' in event['data']:
            try:
                user_uuid = get_or_create_user(event['data']['user_name'],
                                               event['data']['password'])
                logger.info('user_uuid %s', user_uuid)
            except WrongPasswordException as e:
                await websocket.send_json(
                    {
                        'type': 'error',
                        'data': {
                            'message': e.message
                        }
                    }
                )
                return

        event_type = event['type']
        if event_type == 'insert_new_question':
            a = process_new_question(user_uuid, event=event['data'])
            await websocket.send_json(
                {
                    'type': 'return_new_question',
                    'data': a
                }
            )
        elif event_type == 'get_question':
            ret = process_serve_new_question(user_uuid, event['data'])
            await websocket.send_json(
                {
                    'type': 'return_question',
                    'data': json.dumps(ret)
                }
            )
            if user_uuid is not None:
                user_info_ret = get_user_info(user_uuid)
                await websocket.send_json(
                    {
                        'type': 'return_user_info',
                        'data': json.dumps(user_info_ret)
                    }
                )
        elif event_type == 'answered_question':
            ret = process_new_answer(user_uuid, event['data'])
            await websocket.send_json(
                {
                    'type': 'answered_question_feedback',
                    'data': ret
                }
            )
            if user_uuid is not None:
                user_info_ret = get_user_info(user_uuid)
                await websocket.send_json(
                    {
                        'type': 'return_user_info',
                        'data': json.dumps(user_info_ret)
                    }
                )
        elif event_type == 'vote_question':
            ret = process_vote_question(user_uuid, event['data'])
            await websocket.send_json(
                {
                    'type': 'vote_feedback',
                    'data': ret
                }
            )
        else:
            logger.error('Unknown event type %s', event_type)
