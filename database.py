"""This is just a mock database, so that main.py has something to call, should call an actuall database"""
import logging

logger = logging.getLogger('tupilaqs.database')

global questions
questions = list()
questions.append(("This is a question", 'Bug'))


def add_new_question(user, msg, correct_answer):
    """Add a new question to the database, if not present, set score to 0.

    Keep track of which user added the question.
    """
    global questions
    logger.info('Adding question by user %s, correct answer %s:\n"""%s"""', user, correct_answer, msg)
    questions.append(msg)


def serve_new_question(user):
    """Serve a new question to user, ensure user has not already seen this question

    Returns question, correct_answer
    """
    question, correct_answer = questions[0]
    return question, correct_answer


def record_user_answer(user, question, answer):
    """Record what the user selected, answer can be:

    'Bug',
    'Feature',
    'Upvote'
    """
    print('record_user_answer(%s, %s)' % (user, answer))
