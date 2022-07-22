from uuid import UUID, uuid1

import psycopg
from config import config


def initiate_database() -> None:
    """**Initiates database.**

    Initiates database with two tables for 'questions' and 'answers'
    all questions and answers have a unique ID and
    an identifier using UUID for join.
    """
    questions_table = '''
        CREATE TABLE QUESTIONS(
            ID SERIAL PRIMARY KEY,
            TEXT VARCHAR(500) NOT NULL,
            TITLE CHAR(50) NOT NULL,
            EXPL CHAR(200) NOT NULL,
            DIFFICULTY SMALLINT NOT NULL,
            IDENT VARCHAR(100) NOT NULL,
            VOTES SMALLINT
        )
    '''
    answers_table = '''
        CREATE TABLE ANSWERS(
            ID SERIAL PRIMARY KEY,
            ANSWER VARCHAR(500) NOT NULL,
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
        title: str = "title",
        expl: str = "explanation",
        diff: int = 0,
        votes: int = 0) -> None:
    """**Insert a record database.**

    :param question:
    :param answer:
    :param title:
    :param expl:
    :param diff:
    :param votes:
    """
    q_sql = '''
        INSERT INTO questions (TEXT, TITLE, EXPL, DIFFICULTY, IDENT, VOTES)
        VALUES (%s, %s, %s, %s, %s, %s)
    '''
    a_sql = '''
        INSERT INTO answers (ANSWER, IDENT)
        VALUES (%s, %s)
    '''
    unique_id = uuid1()

    q_data = (question, unique_id, votes)
    a_data = (answer, unique_id)

    try:
        with psycopg.connect(**config()) as conn:
            with conn.cursor() as cur:
                cur.execute(q_sql, q_data)
                cur.execute(a_sql, a_data)
                conn.commit()
    except psycopg.DatabaseError as e:
        print(e)


def delete_question(uuid: UUID) -> bool:
    """**Deletes a record from the DB.**

    :param uuid:
    :return:
    """
    pass


def update_question(uuid: UUID) -> str:
    """**Update a record in the DB.**

    :param uuid:
    :return:
    """
    pass


def get_question() -> None:
    """**Return a question based on ??**

    :return:
    """
    pass


def add_user() -> None:
    """**Add a new user to the database.**

    :return:
    """
    pass


def delete_user(uuid: UUID) -> bool:
    """**Delete a user by UUID.**

    :return:
    """
    pass


initiate_database()
insert_question("test", "test", 0)
