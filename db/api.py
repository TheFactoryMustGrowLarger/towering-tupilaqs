from functools import singledispatch
from uuid import uuid1

from config import config
from db_classes import Combined
from psycopg import Connection, connect, errors
from psycopg.rows import class_row


def conn_singleton() -> Connection:
    """**Returns a connection for the database.**

    :return: A Connection
    """
    conn = ""
    try:
        conn = connect(**config(section='local'))
    except errors.ConnectionDoesNotExist as e:
        print(e)
    return conn


def initiate_database() -> bool:
    """**Initiates database.**

    Initiates database with two tables for 'questions' and 'answers'
    all questions and answers have a unique ID and
    an identifier using UUID for join.

    This should only run once to make necessary tables or if
    you want to recreate it for any reason.

    :return: if everything was successful
    """
    questions_table = '''
        CREATE TABLE QUESTIONS(
            ID SERIAL PRIMARY KEY,
            TXT TEXT NOT NULL,
            TITLE CHAR(25) NOT NULL,
            EXPL CHAR(30) NOT NULL,
            DIFFICULTY SMALLINT NOT NULL,
            IDENT VARCHAR(100) NOT NULL,
            VOTES SMALLINT
        )
    '''
    answers_table = '''
        CREATE TABLE ANSWERS(
            ID SERIAL PRIMARY KEY,
            ANSWER TEXT NOT NULL,
            IDENT VARCHAR(100) NOT NULL
        )
    '''
    users_table = '''
        CREATE TABLE USERS(
            ID SERIAL PRIMARY KEY,
            USER_NAME VARCHAR(30) NOT NULL,
            CORRECT_ANSWERS TEXT,
            IDENT VARCHAR(100) NOT NULL
        )
    '''
    with conn_singleton() as conn:
        print("Connecting to DB")
        with conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS QUESTIONS")
            cur.execute("DROP TABLE IF EXISTS ANSWERS")
            cur.execute("DROP TABLE IF EXISTS USERS")
            cur.execute(questions_table)
            print("Added `questions` table to DB.")
            cur.execute(answers_table)
            print("Added `answers` table to DB.")
            cur.execute(users_table)
            print("Added `users` table to DB.")

    return True


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
    unique_id = uuid1()
    with conn_singleton() as conn:
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
            return "Added `{0}` to the database with UUID {1}.".format(title, unique_id)


def delete_question(uuid: str) -> bool:
    """**Deletes a record from the DB.**

    :param uuid: Needs to be in string format for comparison
    :return:
    """
    with conn_singleton() as conn:
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
                return True
            else:
                return False


def update_question_text(uuid: str, text: str) -> bool:
    """**Update QUESTION `TEXT`**

    :param uuid: Needs to be in string format for comparison
    :param text:
    :return:
    """
    with conn_singleton() as conn:
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
    with conn_singleton() as conn:
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
    with conn_singleton() as conn:
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
    with conn_singleton() as conn:
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
    with conn_singleton() as conn:
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
    with conn_singleton() as conn:
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


def get_question(uuid: str) -> Combined:
    """**Return a question based on uuid**

    :param uuid: Needs to be in string format for comparison
    :return: A list with the question corresponding to the uuid provided
    """
    # with conn_singleton() as conn:
    #     cur = conn.cursor(row_factory=class_row(Combined))
    #     v = cur.execute("SELECT * FROM answers JOIN questions ON answers.ident = questions.ident").fetchall()
    #     print(v)
    with conn_singleton() as conn:
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


def get_all_questions() -> list[Combined]:
    """**Returns all questions+answers from database.**

    :return:
    """
    with conn_singleton() as conn:
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
        """
        ).fetchall()
        return results


def add_user(user_name: str) -> str:
    """**Add a new user to the database.**

    :param user_name: it's a username
    :return: A string - if it successfully added a row
    """
    unique_id = uuid1()
    with conn_singleton() as conn:
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
            return "Added `{0}` to the database with UUID {1}".format(user_name, unique_id)


@singledispatch
def delete_user(uuid: str) -> bool:
    """**Delete a user by UUID.**

    :param uuid: Needs to be in string format for comparison
    :return:
    """
    with conn_singleton() as conn:
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
                return True
            else:
                return False


@delete_user.register
def _(user_name: str) -> bool:
    """**Delete a user by USERNAME.**

    :param user_name: Needs to be in string format for comparison
    :return:
    """
    with conn_singleton() as conn:
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
                return True
            else:
                return False


# initiate_database()

# for i in range(1, 10):
#     print(insert_question(
#         question="question{0}".format(i),
#         answer="answer{0}".format(i),
#         title="title{0}".format(i),
#         expl="expl{0}".format(i),
#     ))

# print(add_user("testing"))
# if delete_user("testing"):
#     print("yeeted")

# print(delete_question("0a19adb5-0a10-11ed-a7ee-f6aec268b9bd"))
