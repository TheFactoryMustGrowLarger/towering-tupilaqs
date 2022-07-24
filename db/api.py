from uuid import uuid1

from config import config
from db_classes import Combined, User
from db_tables import answers, questions, users
from psycopg import Connection, connect, errors
from psycopg.rows import class_row


def __conn_singleton() -> Connection:
    conn = ""
    try:
        conn = connect(**config(section='local'))
    except errors.ConnectionDoesNotExist as e:
        print(e)
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
            cur.execute(questions)
            print("Added `questions` table to DB.")
            cur.execute(answers)
            print("Added `answers` table to DB.")
            cur.execute(users)
            print("Added `users` table to DB.")


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


def get_question(uuid: str) -> Combined:
    """**Return a question based on uuid**

    :param uuid: Needs to be in string format for comparison
    :return: A list with the question corresponding to the uuid provided
    """
    # with __conn_singleton() as conn:
    #     cur = conn.cursor(row_factory=class_row(Combined))
    #     v = cur.execute("SELECT * FROM answers JOIN questions ON answers.ident = questions.ident").fetchall()
    #     print(v)
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


def get_all_questions() -> list[Combined]:
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
        """
        ).fetchall()
        return results


def add_user(user_name: str) -> str:
    """**Add a new user to the database.**

    :param user_name: it's a username
    :return: A string - if it successfully added a row
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
            return f"Added `{user_name}` to the database with UUID {unique_id}"


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
    initiate_database()

    for i in range(1, 10):
        print(insert_question(
            question=f"question{i}",
            answer=f"answer{i}",
            title=f"title{i}",
            expl=f"expl{i}"
        ))
        print(add_user(user_name=f"username{i}"))

    print(add_user("testingaa"))
    print(delete_user_by_name("testingaa"))

    print(delete_question("0a19adb5-0a10-11ed-a7ee-f6aec268b9bd"))

    _id = "abdff6b1-0a4d-11ed-8eb0-f6aec268b9bd"
    update_question_text(_id, text="testdad")
    update_answer_text(_id, text="testing")
    update_question_votes(_id, votes=10)
    update_question_title(_id, title="new title")
    update_question_difficulty(_id, diff=4)
    update_question_explanation(_id, expl="new expl")
