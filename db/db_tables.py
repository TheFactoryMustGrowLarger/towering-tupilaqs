questions = '''
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
answers = '''
    CREATE TABLE ANSWERS(
        ID SERIAL PRIMARY KEY,
        ANSWER TEXT NOT NULL,
        IDENT VARCHAR(100) NOT NULL
    )
'''
users = '''
    CREATE TABLE USERS(
        ID SERIAL PRIMARY KEY,
        USER_NAME VARCHAR(30) NOT NULL,
        CORRECT_ANSWERS TEXT,
        IDENT VARCHAR(100) NOT NULL
    )
'''
