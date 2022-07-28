# standard library imports
import logging
import random
from uuid import uuid1

# third party imports
from psycopg import Connection, connect, errors
from psycopg.rows import class_row

# This project
from db.db_config.config import config
from db.utils.db_classes import Combined, Question, User, UserCA, UserIA
from db.utils.db_tables import (
    create_questions_table, create_users_table, creater_answers_table
)

logger = logging.getLogger('tupilaqs.db')


def __conn_singleton() -> Connection:
    conn = ""
    conf = config()
    try:
        conn = connect(**conf)
    except errors.ConnectionDoesNotExist as e:
        print(e)
    except errors.OperationalError as e:
        logger.exception('db connect failed %s', conf)
        raise e
    return conn


def initiate_database() -> None:
    """**Initiates database.**

    Initiates database with two tables for 'questions' and 'answers'
    all questions and answers have a unique ID and
    an identifier using UUID for join.

    This should only run once to make necessary tables or if
    you want to recreate it for any reason.

    :return: if everything was successful
    """
    with __conn_singleton() as conn:
        print("Connecting to DB")
        with conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS QUESTIONS")
            cur.execute("DROP TABLE IF EXISTS ANSWERS")
            cur.execute("DROP TABLE IF EXISTS USERS")
            cur.execute(create_questions_table)
            logger.info("Added `questions` table to DB.")
            cur.execute(creater_answers_table)
            logger.info("Added `answers` table to DB.")
            cur.execute(create_users_table)
            logger.info("Added `users` table to DB.")


def insert_question(
        question: str,
        answer: str,
        title: str,
        expl: str,
        diff: int = 0,
        votes: int = 0
) -> str:
    """**Insert a record database.**

    :param question:
    :param answer:
    :param title:
    :param expl:
    :param diff:
    :param votes:
    """
    # FIXME: Can this updated to check for duplicate question text?
    # Not sure if it should be rejected or allowed to update.
    unique_id = uuid1()
    with __conn_singleton() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO
                    questions (TXT, TITLE, EXPL, DIFFICULTY, VOTES, IDENT)
                VALUES
                    ( %(question)s, %(title)s, %(expl)s, %(diff)s, %(votes)s, %(ident)s )
            """, {
                    'question': question,
                    'title': title,
                    'expl': expl,
                    'diff': diff,
                    'votes': votes,
                    'ident': unique_id,
                }
            )
            cur.execute(
                """
                INSERT INTO
                    answers ( ANSWER, IDENT )
                VALUES
                    ( %(answer)s, %(ident)s )
            """, {
                    'answer': answer,
                    'ident': unique_id,
                }
            )
            return f"Added `{title}` to the database with UUID {unique_id}."


def delete_question(uuid: str) -> tuple:
    """**Deletes a record from the DB.**

    :param uuid: Needs to be in string format for comparison
    :return:
    """
    with __conn_singleton() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                DELETE
                FROM
                    questions
                WHERE
                    ident = %(ident)s
            """, {
                    'ident': uuid,
                }
            )
            cur.execute(
                """
                DELETE
                FROM
                    answers
                WHERE
                    ident = %(ident)s
            """, {
                    'ident': uuid,
                }
            )
            if cur.rowcount > 0:
                return True, cur.rowcount
            else:
                return False, cur.rowcount


def update_question_text(uuid: str, text: str) -> bool:
    """**Update QUESTION `TEXT`**

    :param uuid: Needs to be in string format for comparison
    :param text:
    :return:
    """
    with __conn_singleton() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE
                    questions
                SET
                    txt = %(text)s
                WHERE
                    ident = %(ident)s
            """, {
                    'text': text,
                    'ident': uuid,
                }
            )
            return True


def update_question_title(uuid: str, title: str) -> bool:
    """**Update QUESTION `TITLE`.**

    :param uuid: Needs to be in string format for comparison
    :param title:
    :return:
    """
    with __conn_singleton() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE
                    questions
                SET
                    title = %(title)s
                WHERE
                    ident = %(ident)s
            """, {
                    'title': title,
                    'ident': uuid,
                }
            )
            return True


def update_question_explanation(uuid: str, expl: str) -> bool:
    """**Update QUESTION `EXPLANATION`.**

    :param uuid: Needs to be in string format for comparison
    :param expl:
    :return:
    """
    with __conn_singleton() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE
                    questions
                SET
                    expl = %(expl)s
                WHERE
                    ident = %(ident)s
            """, {
                    'expl': expl,
                    'ident': uuid,
                }
            )
            return True


def update_question_difficulty(uuid: str, diff: int) -> bool:
    """**Update QUESTION `DIFFICULTY`.**

    :param uuid: Needs to be in string format for comparison
    :param diff:
    :return:
    """
    with __conn_singleton() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE
                    questions
                SET
                    difficulty = %(diff)s
                WHERE
                    ident = %(ident)s
            """, {
                    'diff': diff,
                    'ident': uuid,
                }
            )
            return True


def update_question_votes(uuid: str, votes: int) -> bool:
    """**Update QUESTION `VOTES`.**

    :param uuid: Needs to be in string format for comparison
    :param votes:
    :return:
    """
    with __conn_singleton() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE
                    questions
                SET
                    votes = %(votes)s
                WHERE
                    ident = %(ident)s
            """, {
                    'votes': votes,
                    'ident': uuid,
                }
            )
            return True


def update_answer_text(uuid: str, text: str) -> bool:
    """**Update ANSWER `TEXT`.**

    :param uuid: Needs to be in string format for comparison
    :param text:
    :return:
    """
    with __conn_singleton() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE
                    answers
                SET
                    answer = %(text)s
                WHERE
                    ident = %(ident)s
            """, {
                    'text': text,
                    'ident': uuid,
                }
            )
            return True


def update_user_ca_by_uuid(uuid: str, ca: str) -> bool:
    """**Update users `correct_answers` with their `user_name`**...

    :param uuid:
    :param ca:
    :return:
    """
    # Add delimiter
    ca = ', ' + ca  # HACK: Better to skip this if correct_answers is empty

    with __conn_singleton() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE
                    users
                SET
                    correct_answers = CONCAT(correct_answers, %(ca)s::text)
                WHERE
                    ident = %(uuid)s
            """, {
                    'ca': ca,
                    'uuid': uuid,
                }
            )
            return True


def update_user_ia_by_uuid(uuid: str, ca: str) -> bool:
    """**Update users `incorrect_answers` with their `user_name`**...

    :param uuid:
    :param ca:
    :return:
    """
    # Add delimiter
    ca = ', ' + ca  # HACK: Better to skip this if correct_answers is empty

    with __conn_singleton() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE
                    users
                SET
                    incorrect_answers = CONCAT(incorrect_answers, %(ca)s::text)
                WHERE
                    ident = %(uuid)s
            """, {
                    'ca': ca,
                    'uuid': uuid,
                }
            )
            return True


def get_single_question(uuid: str) -> Combined:
    """**Return a question based on uuid**

    :param uuid: Needs to be in string format for comparison
    :return: A list with the question corresponding to the uuid provided
    """
    with __conn_singleton() as conn:
        cur = conn.cursor(row_factory=class_row(Combined))
        results = cur.execute(
            """
            SELECT
                questions.id,
                questions.title,
                questions.expl,
                questions.txt,
                answers.answer,
                questions.difficulty,
                questions.votes,
                questions.ident
            from
                answers
            JOIN
                questions
            ON
                answers.ident = questions.ident
            AND
                answers.ident = %(ident)s
        """, {
                'ident': uuid,
            }
        ).fetchone()
        return results


def get_single_question_by_votes(desc: bool = True) -> Combined:
    """**Returns highest voted questions**...

    :param desc: Ordering by Descending votes always unless specified
    :return:
    """
    order = 'DESC'
    if not desc:
        order = 'ASC'

    with __conn_singleton() as conn:
        cur = conn.cursor(row_factory=class_row(Combined))
        results = cur.execute(
            """
            SELECT
                questions.id,
                questions.title,
                questions.expl,
                questions.txt,
                answers.answer,
                questions.difficulty,
                questions.votes,
                questions.ident
            FROM
                questions
            JOIN
                answers
            ON
                questions.ident = answers.ident
            ORDER BY questions.votes %s
        """ % order
        ).fetchone()
        return results


def get_all_questions(limit: int = 10) -> list[Combined]:
    """**Returns all questions+answers from database.**

    :return:
    """
    with __conn_singleton() as conn:
        cur = conn.cursor(row_factory=class_row(Combined))
        results = cur.execute(
            """
            SELECT
                questions.id,
                questions.title,
                questions.expl,
                questions.txt,
                answers.answer,
                questions.difficulty,
                questions.votes,
                questions.ident
            FROM
                questions
            INNER JOIN
                answers
            ON
                answers.ident = questions.ident
            LIMIT %(limit)s
        """, {
                'limit': limit
            }
        ).fetchall()
        return results


def get_ca_by_uuid(uuid: str) -> list[Question]:
    """**Returns players already correct answers by uuid**...

    :param uuid: User uuid aka ident
    :return:
    """
    with __conn_singleton() as conn:
        cur = conn.cursor(row_factory=class_row(UserCA))
        user_ca = cur.execute(
            """
            SELECT
                correct_answers
            FROM
                users
            WHERE
                ident = %(uuid)s
            """, {
                'uuid': uuid,
            }
        ).fetchone()
        cur.close()
        cur = conn.cursor(row_factory=class_row(Question))
        ca = list(user_ca.correct_answers.split(', '))  # Split correct answers from STR into a tuple
        ca = list(filter(lambda x: x != '', ca))  # remove empty items
        logger.debug('get_ca_by_uuid, correct answers = %d: %s', len(ca), ca)
        all_questions = cur.execute(
            """
            SELECT
                *
            FROM
                questions as q
            ORDER BY
                q.id
            """
        ).fetchall()
        return [result for result in all_questions if result.ident in ca]


def get_ia_by_uuid(uuid: str) -> list[Question]:
    """**Returns players already incorrect answers by uuid**...

    :param uuid: User uuid aka ident
    :return:
    """
    with __conn_singleton() as conn:
        cur = conn.cursor(row_factory=class_row(UserIA))
        user_ca = cur.execute(
            """
            SELECT
                incorrect_answers
            FROM
                users
            WHERE
                ident = %(uuid)s
            """, {
                'uuid': uuid,
            }
        ).fetchone()
        cur.close()
        cur = conn.cursor(row_factory=class_row(Question))
        ca = list(user_ca.incorrect_answers.split(', '))  # Split incorrect answers from STR into a tuple
        ca = list(filter(lambda x: x != '', ca))  # remove empty items
        logger.debug('get_ia_by_uuid, incorrect answers = %d: %s', len(ca), ca)
        all_questions = cur.execute(
            """
            SELECT
                *
            FROM
                questions as q
            ORDER BY
                q.id
            """
        ).fetchall()
        return [result for result in all_questions if result.ident in ca]


def get_new_question_for_user(uuid: str) -> list[Question]:
    """**Returns a new question for player, ensuring it has not been answered before**...

    :param uuid: User uuid aka ident
    :return:

    :raises IndexError if no more questions are available
    """
    with __conn_singleton() as conn:
        cur = conn.cursor(row_factory=class_row(User))
        user_ca = cur.execute(
            """
            SELECT
                id,
                user_name,
                correct_answers,
                incorrect_answers,
                ident
            FROM
                users
            WHERE
                ident = %(uuid)s
            """, {
                'uuid': uuid,
            }
        ).fetchone()
        cur.close()

        answers = list()
        answers.extend(user_ca.correct_answers.split(', '))  # Split correct answers from STR into a tuple
        answers.extend(user_ca.incorrect_answers.split(', '))  # Split correct answers from STR into a tuple

        answers = list(filter(lambda x: x != '', answers))  # remove empty items

        logger.debug('get_new_question_for_user, answers = %d: %s', len(answers), answers)

        cur = conn.cursor(row_factory=class_row(Question))
        all_questions = cur.execute(
            """
            SELECT
                *
            FROM
                questions as q
            ORDER BY
                q.id
            """
        ).fetchall()

        applicable_questions = [result for result in all_questions if result.ident not in answers]

        return applicable_questions[0]


def get_ca_by_name(user_name: str) -> list[Question]:
    """**Returns players already correct answers by user_name**...

    :param user_name: Username
    :return:
    """
    with __conn_singleton() as conn:
        cur = conn.cursor(row_factory=class_row(UserCA))
        user_ca = cur.execute(
            """
            SELECT
                correct_answers
            FROM
                users
            WHERE
                user_name = %(user_name)s
            """, {
                'user_name': user_name,
            }
        ).fetchone()
        cur.close()
        cur = conn.cursor(row_factory=class_row(Question))
        ca = list(user_ca.correct_answers.split(', '))  # Split correct answers from STR into a tuple
        results = cur.execute(
            """
            SELECT
                *
            FROM
                questions as q
            ORDER BY
                q.id
            """
        ).fetchall()
        return [result for result in results if result.ident in ca]


def add_user(user_name: str) -> str:
    """**Add a new user to the database.**

    :param user_name: it's a username
    :return: unique_uuid of the added user
    """
    unique_id = uuid1()
    with __conn_singleton() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO
                    users (USER_NAME, CORRECT_ANSWERS, IDENT)
                VALUES
                    ( %(user_name)s, %(correct_answers)s, %(ident)s )

            """, {
                    'user_name': user_name,
                    'correct_answers': "",
                    'ident': unique_id,
                }
            )
            return str(unique_id)


def delete_user_by_uuid(uuid: str) -> tuple:
    """**Delete a user by UUID.**

    :param uuid: Needs to be in string format for comparison
    :return:
    """
    with __conn_singleton() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                DELETE
                FROM
                    users
                WHERE
                    ident = %(ident)s
            """, {
                    'ident': uuid,
                }
            )
            if cur.rowcount > 0:
                return True, cur.rowcount
            else:
                return False, cur.rowcount


def delete_user_by_name(user_name: str) -> tuple:
    """**Delete a user by USERNAME.**

    :param user_name: Needs to be in string format for comparison
    :return:
    """
    with __conn_singleton() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                DELETE
                FROM
                    users
                WHERE
                    user_name = %(user_name)s
            """, {
                    'user_name': user_name,
                }
            )
            if cur.rowcount > 0:
                return True, cur.rowcount
            else:
                return False, cur.rowcount


def get_user_by_uuid(uuid: str) -> User:
    """Get user by UUID"""
    with __conn_singleton() as conn:
        cur = conn.cursor(row_factory=class_row(User))
        results = cur.execute(
            """
            SELECT
                id,
                user_name,
                correct_answers,
                incorrect_answers,
                ident
            FROM
                users
            WHERE
                ident = %(ident)s
        """, {
                'ident': uuid,
            }
        ).fetchone()
        return results


def get_user_by_name(user_name: str) -> User:
    """Get User by username"""
    with __conn_singleton() as conn:
        cur = conn.cursor(row_factory=class_row(User))
        results = cur.execute(
            """
            SELECT
                id,
                user_name,
                correct_answers,
                incorrect_answers,
                ident
            FROM
                users
            WHERE
                user_name = %(user_name)s
        """, {
                'user_name': user_name,
            }
        ).fetchone()
        return results


if __name__ == '__main__':
    from utilites.logger_utility import setup_logger
    setup_logger()

    initiate_database()

    for i in range(1, 20):
        print(insert_question(
            question=f"question{i}",
            answer=f"answer{i}",
            title=f"title{i}",
            expl=f"expl{i}",
            votes=random.randrange(1, 100),
            diff=random.randrange(1, 5)
        ))
        print(add_user(user_name=f"username{i}"))

    print(get_single_question_by_votes())
    print(delete_user_by_name("username9"))
    print(get_ca_by_name("username1"))

    user_id = get_user_by_name('username1').ident
    questions = get_all_questions()
    assert len(questions) == 10

    # User answered correctly
    number_of_correct_questions = 5
    number_of_incorrect_questions = 3
    for q in questions[:number_of_correct_questions]:
        update_user_ca_by_uuid(user_id, ca=q.ident)

    start = number_of_correct_questions
    end = number_of_correct_questions+number_of_incorrect_questions
    for q in questions[start:end]:
        update_user_ia_by_uuid(user_id, ca=q.ident)

    correct_answers = get_ca_by_uuid(user_id)
    incorrect_answers = get_ia_by_uuid(user_id)

    expected = 'expected length %d, got %s' % (number_of_correct_questions, len(correct_answers))
    assert len(correct_answers) == number_of_correct_questions, expected

    expected = 'expected length %d, got %s' % (number_of_incorrect_questions, len(incorrect_answers))
    assert len(incorrect_answers) == number_of_incorrect_questions, expected

    correct_answers_ident = list()
    incorrect_answers_ident = list()
    for item in correct_answers:
        print('Correct answers', item.txt)
        correct_answers_ident.append(item.ident)

    for item in incorrect_answers:
        incorrect_answers_ident.append(item.ident)
        print('Incorrect answers', item.txt)

    q = get_new_question_for_user(user_id)
    assert q.ident not in correct_answers_ident, 'vops, wanted a new question got %s' % q.ident
    assert q.ident not in incorrect_answers_ident, 'vops, wanted a new question got %s' % q.ident
    print('New question', q)

    # print(delete_question("0a19adb5-0a10-11ed-a7ee-f6aec268b9bd"))
    #
    # _id = "abdff6b1-0a4d-11ed-8eb0-f6aec268b9bd"
    # update_question_text(_id, text="testdad")
    # update_answer_text(_id, text="testing")
    # update_question_votes(_id, votes=10)
    # update_question_title(_id, title="new title")
    # update_question_difficulty(_id, diff=4)
    # update_question_explanation(_id, expl="new expl")
