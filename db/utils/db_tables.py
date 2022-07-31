create_questions_table = '''
        CREATE TABLE QUESTIONS(
            ID SERIAL PRIMARY KEY,
            TXT TEXT NOT NULL,
            TITLE VARCHAR(100) NOT NULL,
            EXPL TEXT NOT NULL,
            DIFFICULTY SMALLINT NOT NULL,
            IDENT VARCHAR(100) NOT NULL,
            VOTES SMALLINT
        )
    '''

create_answers_table = '''
    CREATE TABLE ANSWERS(
        ID SERIAL PRIMARY KEY,
        ANSWER TEXT NOT NULL,
        IDENT VARCHAR(100) NOT NULL
    )
'''


create_users_table = '''
    CREATE TABLE USERS(
        ID SERIAL PRIMARY KEY,
        USER_NAME VARCHAR(30) NOT NULL,
        PASSWORD VARCHAR(100) NOT NULL,
        CORRECT_ANSWERS TEXT,
        INCORRECT_ANSWERS TEXT,
        SUBMITTED_QUESTIONS TEXT,
        SUBMITTED_ADD_VOTES TEXT,
        IDENT VARCHAR(100) NOT NULL
    )
'''
