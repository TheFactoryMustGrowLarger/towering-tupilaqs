from uuid import uuid1

import psycopg
from config import config


def initiate_database() -> None:
    """**Initiates database.**

    Initiates database with two tables for 'questions' and 'answers'
    all questions and answers have a unique ID and
    an identifier using UUID for join.

    This should only be ran once to make necessary tables or if
    you want to recreate it for any reason.
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
            CORRECT_ANSWERS VARCHAR(500)
        )
    '''
    with psycopg.connect(**config()) as conn:
        print("Connecting to DB")
        with conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS QUESTIONS")
            cur.execute("DROP TABLE IF EXISTS ANSWERS")
            cur.execute("DROP TABLE IF EXISTS USERS")
            cur.execute(questions_table)
            print("Added questions table to DB.")
            cur.execute(answers_table)
            print("Added answers table to DB.")
            cur.execute(users_table)
            print("Added users table to DB.")
            conn.commit()


def insert_question(
        question: str,
        answer: str,
        title: str,
        expl: str,
        diff: int = 0,
        votes: int = 0
) -> None:
    """**Insert a record database.**

    :param question:
    :param answer:
    :param title:
    :param expl:
    :param diff:
    :param votes:
    """
    unique_id = uuid1()

    try:
        with psycopg.connect(**config()) as conn:
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
                conn.commit()
                print("Added {0} to the database with UUID {1}.".format(title, unique_id))
    except psycopg.DataError as e:
        # Better error handling needed
        print(e)


def delete_question(uuid: str) -> bool:
    """**Deletes a record from the DB.**

    :param uuid: Needs to be in string format for comparison
    :return:
    """
    try:
        with psycopg.connect(**config()) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    DELETE
                    FROM
                        questions
                    WHERE
                        ident= %(ident)s
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
                        ident= %(ident)s
                """, {
                        'ident': uuid,
                    }
                )
                conn.commit()
                if cur.rowcount > 0:
                    return True
                else:
                    return False
    except psycopg.DataError as e:
        # Better error handling needed
        print(e)
        return False


def update_question(uuid: str) -> bool:
    """**Update a record in the DB.**

    :param uuid: Needs to be in string format for comparison
    :return:
    """
    try:
        with psycopg.connect(**config()) as conn:
            with conn.cursor() as cur:
                cur.execute("")
                conn.commit()
                return True
    except psycopg.DataError as e:
        # Better error handling needed
        print(e)
        return False


def get_question(uuid: str) -> list:
    """**Return a question based on uuid**

    :param uuid: Needs to be in string format for comparison
    :return: A list with the question corresponding to the uuid provided
    """
    try:
        with psycopg.connect(**config()) as conn:
            with conn.cursor() as cur:
                v = cur.execute(
                    """
                    SELECT
                        questions.title,
                        questions.expl,
                        questions.txt,
                        answers.answer,
                        questions.difficulty,
                        questions.votes
                    from
                        questions
                    INNER JOIN
                        answers
                    ON
                        questions.ident=answers.ident
                    AND
                        questions.ident = %(ident)s
                """, {
                        'ident': uuid,
                    }
                ).fetchone()
                return v
    except psycopg.DataError as e:
        # Better error handling needed
        print(e)


def get_all_questions() -> list:
    """**Returns all questions+answers from database.**

    :return:
    """
    try:
        with psycopg.connect(**config()) as conn:
            with conn.cursor() as cur:
                v = cur.execute(
                    """
                    SELECT
                        questions.title,
                        questions.expl,
                        questions.txt,
                        answers.answer,
                        questions.difficulty,
                        questions.votes
                    FROM
                        questions
                    INNER JOIN
                        answers
                    ON
                        answers.ident = questions.ident
                """
                ).fetchall()
                return v
    except psycopg.DataError as e:
        # Better error handling needed
        print(e)


def add_user() -> None:
    """**Add a new user to the database.**

    :return:
    """
    try:
        with psycopg.connect(**config()) as conn:
            with conn.cursor() as cur:
                cur.execute("")
                conn.commit()
    except psycopg.DataError as e:
        # Better error handling needed
        print(e)


def delete_user(uuid: str) -> bool:
    """**Delete a user by UUID.**

    :param uuid: Needs to be in string format for comparison
    :return:
    """
    try:
        with psycopg.connect(**config()) as conn:
            with conn.cursor() as cur:
                cur.execute("")
                conn.commit()
                return True
    except psycopg.DataError as e:
        # Better error handling needed
        print(e)
        return False


# initiate_database()
#
# for i in range(1, 10):
#     insert_question(
#         question="question{0}".format(i),
#         answer="answer{0}".format(i),
#         title="title{0}".format(i),
#         expl="expl{0}".format(i),
#     )


# delete_question("0a19adb5-0a10-11ed-a7ee-f6aec268b9bd")
