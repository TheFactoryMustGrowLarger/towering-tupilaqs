import psycopg
from config import config


def init():
    """**Initiates database.**

    Initiates database with two tables for 'questions' and 'answers'
    all questions and answers have a unique ID and
    an identifier using UUID for join.
    """
    params = config()
    questions_table = '''
        CREATE TABLE QUESTIONS(
            ID SERIAL PRIMARY KEY,
            QUESTION VARCHAR(500) NOT NULL,
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
    with psycopg.connect(**params) as conn:
        print("Connecting to DB")
        with conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS QUESTIONS")
            cur.execute("DROP TABLE IF EXISTS ANSWERS")
            cur.execute(questions_table)
            print("Added questions table to DB.")
            cur.execute(answers_table)
            print("Added answers table to DB.")
            conn.commit()


init()
