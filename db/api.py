# standard library imports
import logging
import random
from uuid import uuid4

# third party imports
from psycopg import Connection, connect, errors
from psycopg.rows import class_row

# This project
from db.db_config.config import config
from db.utils.db_classes import (
    Combined, QuestionInsert, QuestionPull, User, UserCA, UserIA, UserSQ,
    UserSV
)
from db.utils.db_tables import (
    create_answers_table, create_questions_table, create_users_table
)
from db.utils.official_questions import official_questions

logger = logging.getLogger('tupilaqs.db')


def read_file(file_path):
    """Returns file content"""
    with open(file_path, 'r') as file:
        file_as_string = file.read()
    return file_as_string


class TupilaqsDB:
    """Wrapper around the tupilaqs quiz database"""

    def __init__(self, conf=None):
        """Initialize database from config

        :param conf: Optional, defaults to reading configuration from db/db_config/database.ini
        """
        if conf is None:
            self.conf = config()
        else:
            self.conf = conf

        if self.conf['should_initialize_database']:
            self.__initiate_database()

    def __conn_singleton(self) -> Connection:
        conn = ""
        conf = self.conf
        try:
            conn = connect(
                host=conf['host'],
                dbname=conf['dbname'],
                user=conf['user'],
                password=conf['password'])
        except errors.ConnectionDoesNotExist as e:
            logger.exception('db connect failed %s', conf)
            print(e)
        except errors.OperationalError as e:
            logger.exception('db connect failed %s', conf)
            raise e
        return conn

    def __add_official_questions(self, initial_votes=10):
        """Adds some intial questions to the database from the problems/ folder"""
        for script, answer, title, explanation, difficulty in official_questions:
            script = read_file(script)
            explanation = read_file(explanation)
            try:
                self.insert_question(script, answer, title, explanation, difficulty, votes=initial_votes)
            except errors.StringDataRightTruncation as e:
                logger.error('Too long! %s, script=%s, answer=%s, title=%s, explanation=%s, difficulty=%s',
                             e, script, answer, title, explanation, difficulty)

    def __initiate_database(self) -> None:
        """**Initiates database.**

        Initiates database with two tables for 'questions' and 'answers'
        all questions and answers have a unique ID and
        an identifier using UUID for join.

        This should only run once to make necessary tables or if
        you want to recreate it for any reason.

        :return: if everything was successful
        """
        with self.__conn_singleton() as conn:
            logger.info("Connecting to DB")
            with conn.cursor() as cur:
                cur.execute("DROP TABLE IF EXISTS QUESTIONS")
                cur.execute("DROP TABLE IF EXISTS ANSWERS")
                cur.execute("DROP TABLE IF EXISTS USERS")
                cur.execute(create_questions_table)
                logger.info("Added `questions` table to DB.")
                cur.execute(create_answers_table)
                logger.info("Added `answers` table to DB.")
                cur.execute(create_users_table)
                logger.info("Added `users` table to DB.")

        self.__add_official_questions()

    def insert_question(
            self,
            question: str,
            answer: str,
            title: str,
            expl: str,
            diff: int = 0,
            votes: int = 0) -> QuestionInsert:
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
        unique_id = uuid4()
        question = QuestionInsert(
            txt=question,
            title=title,
            expl=expl,
            difficulty=diff,
            votes=votes,
            ident=str(unique_id))

        with self.__conn_singleton() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO
                        questions (TXT, TITLE, EXPL, DIFFICULTY, VOTES, IDENT)
                    VALUES
                        ( %(txt)s, %(title)s, %(expl)s, %(difficulty)s, %(votes)s, %(ident)s )
                """, question.__dict__
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
                logger.debug('Added question %s: %s', question.title, question.ident)
                return question

    def delete_question(self, uuid: str) -> tuple:
        """**Deletes a record from the DB.**

        :param uuid: Needs to be in string format for comparison
        :return:
        """
        with self.__conn_singleton() as conn:
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

    def update_question_text(self, uuid: str, text: str) -> bool:
        """**Update QUESTION `TEXT`**

        :param uuid: Needs to be in string format for comparison
        :param text:
        :return:
        """
        with self.__conn_singleton() as conn:
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

    def update_question_title(self, uuid: str, title: str) -> bool:
        """**Update QUESTION `TITLE`.**

        :param uuid: Needs to be in string format for comparison
        :param title:
        :return:
        """
        with self.__conn_singleton() as conn:
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

    def update_question_explanation(self, uuid: str, expl: str) -> bool:
        """**Update QUESTION `EXPLANATION`.**

        :param uuid: Needs to be in string format for comparison
        :param expl:
        :return:
        """
        with self.__conn_singleton() as conn:
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

    def update_question_difficulty(self, uuid: str, diff: int) -> bool:
        """**Update QUESTION `DIFFICULTY`.**

        :param uuid: Needs to be in string format for comparison
        :param diff:
        :return:
        """
        with self.__conn_singleton() as conn:
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

    def update_question_votes(
            self,
            question_uuid: str,
            user_uuid: str,
            votes: str = 'add',
            new_vote_override: int = -1) -> int:
        """**Update QUESTION `VOTES`.**

        :param user_uuid:
        :param question_uuid: Needs to be in string format for comparison
        :param votes: Either 'add' or 'sub' / Add or Subtract
        :param new_vote_override: Allows setting a absolute value, ignores votes param. Usefull for testing.
        :return: the updated number of votes
        """
        # FIXME: Support downvote, maybe only as a 'remove' upvote?
        with self.__conn_singleton() as conn:
            with conn.cursor() as cur:
                current_votes = self.get_single_question(question_uuid).votes
                vote_success = self.update_user_sv_up_by_uuid(user_uuid, sv=question_uuid)
                logger.info(
                    'update_question_votes(%s, %s, %s). Current votes %d, vote_success = %s',
                    question_uuid, user_uuid, votes, current_votes, vote_success)

                if new_vote_override != -1:
                    new_votes = new_vote_override
                else:
                    # Has the user already voted?
                    if vote_success is False:
                        return current_votes

                    new_votes = 0
                    if votes == 'add':
                        new_votes = current_votes + 1
                    elif votes == 'sub' and current_votes > 0:
                        new_votes = current_votes - 1
                    else:
                        new_votes = current_votes

                cur.execute(
                    """
                    UPDATE
                        questions
                    SET
                        votes = %(votes)s
                    WHERE
                        ident = %(ident)s
                """, {
                        'votes': new_votes,
                        'ident': question_uuid,
                    }
                )
                return new_votes

    def update_answer_text(self, uuid: str, text: str) -> bool:
        """**Update ANSWER `TEXT`.**

        :param uuid: Needs to be in string format for comparison
        :param text:
        :return:
        """
        with self.__conn_singleton() as conn:
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

    def update_user_ca_by_uuid(self, uuid: str, ca: str) -> bool:
        """**Update users `correct_answers` with their `uuid`**...

        :param uuid:
        :param ca:
        :return:
        """
        logger.debug('Adding to correct answer list for user %s: %s', uuid, ca)

        # Add delimiter
        ca = ', ' + ca  # HACK: Better to skip this if correct_answers is empty
        with self.__conn_singleton() as conn:
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

    def update_user_ia_by_uuid(self, uuid: str, ia: str) -> bool:
        """**Update users `incorrect_answers` with their `uuid`**...

        :param uuid:
        :param ia:
        :return:
        """
        logger.debug('Adding to incorrect answer list for user %s: %s', uuid, ia)

        # Add delimiter
        ia = ', ' + ia  # HACK: Better to skip this if correct_answers is empty
        with self.__conn_singleton() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE
                        users
                    SET
                        incorrect_answers = CONCAT(incorrect_answers, %(ia)s::text)
                    WHERE
                        ident = %(uuid)s
                """, {
                        'ia': ia,
                        'uuid': uuid,
                    }
                )
                return True

    def update_user_sq_by_uuid(self, uuid: str, sq: str) -> bool:
        """**Update users `submitted question` with their `uuid`**...

        :param uuid:
        :param sq: submitted question
        :return:
        """
        # Add delimiter
        sq = ', ' + sq  # HACK: Better to skip this if submitted_questions is empty

        with self.__conn_singleton() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE
                        users
                    SET
                        submitted_questions = CONCAT(submitted_questions, %(sq)s::text)
                    WHERE
                        ident = %(uuid)s
                """, {
                        'sq': sq,
                        'uuid': uuid,
                    }
                )
                return True

    def update_user_sv_up_by_uuid(self, uuid: str, sv: str) -> bool:
        """**Update users `submitted add votes` with their `uuid`**...

        :param uuid:
        :param sv: question the user has voted up
        :returns True if question was upvoted and False if the question was already upvoted.
        """
        with self.__conn_singleton() as conn:
            with conn.cursor(row_factory=class_row(UserSV)) as cur:
                user_sv = cur.execute(
                    """
                SELECT
                    submitted_add_votes
                FROM
                    users
                WHERE
                    ident = %(uuid)s
                    """, {
                        'uuid': uuid,
                    }
                ).fetchone()

                already_voted_up = list()
                if user_sv is not None:
                    already_voted_up.extend(user_sv.as_list('submitted_add_votes'))

                logger.debug('already_voted_up by %s: %s', uuid, already_voted_up)
                if sv in already_voted_up:
                    return False

            with conn.cursor() as cur:
                # Add delimiter
                sv = ', ' + sv  # HACK: Better to skip this if submitted_questions is empty
                cur.execute(
                    """
                    UPDATE
                        users
                    SET
                        submitted_add_votes = CONCAT(submitted_add_votes, %(sv)s::text)
                    WHERE
                        ident = %(uuid)s
                """, {
                        'sv': sv,
                        'uuid': uuid,
                    }
                )
                return True

    def get_single_question(self, uuid: str) -> Combined:
        """**Return a question based on uuid**

        :param uuid: Needs to be in string format for comparison
        :return: A list with the question corresponding to the uuid provided
        """
        with self.__conn_singleton() as conn:
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

    def get_single_question_by_votes(self, desc: bool = True) -> Combined:
        """**Returns highest voted questions**...

        :param desc: Ordering by Descending votes always unless specified
        :return:
        """
        order = 'DESC'
        if not desc:
            order = 'ASC'

        with self.__conn_singleton() as conn:
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

    def get_all_questions(self, limit: int = 10) -> list[Combined]:
        """**Returns all questions+answers from database.**

        :return:
        """
        with self.__conn_singleton() as conn:
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

    def get_total_votes_questions(self, questions: list[str]) -> int:
        """**Returns number of votes for given list of questions uuids**...

        :param questions: List of question uuids
        :return: total vote
        """
        # FIXME: future improvement, do this in sql for improved performance
        votes = 0
        for question_uuid in questions:
            question = self.get_single_question(question_uuid)
            votes += question.votes

        logger.info('get_total_votes_questions(%s) -> %s', questions, votes)
        return votes

    def get_ca_by_uuid(self, uuid: str) -> list[QuestionPull]:
        """**Returns players already correct answers by uuid**...

        :param uuid: User uuid aka ident
        :return:
        """
        with self.__conn_singleton() as conn:
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
            cur = conn.cursor(row_factory=class_row(QuestionPull))

            ca = list()
            if user_ca is not None:
                ca.extend(user_ca.as_list('correct_answers'))

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

    def get_ia_by_uuid(self, uuid: str) -> list[QuestionPull]:
        """**Returns players already incorrect answers by uuid**...

        :param uuid: User uuid aka ident
        :return:
        """
        with self.__conn_singleton() as conn:
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
            cur = conn.cursor(row_factory=class_row(QuestionPull))
            ca = list()
            if user_ca is not None:
                ca.extend(user_ca.as_list('incorrect_answers'))

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

    def get_sq_by_uuid(self, uuid: str) -> list[QuestionPull]:
        """**Returns players submitted questions by uuid**...

        :param uuid: User uuid aka ident
        :return:
        """
        with self.__conn_singleton() as conn:
            cur = conn.cursor(row_factory=class_row(UserSQ))
            user_ca = cur.execute(
                """
                SELECT
                    submitted_questions
                FROM
                    users
                WHERE
                    ident = %(uuid)s
                """, {
                    'uuid': uuid,
                }
            ).fetchone()
            cur.close()
            cur = conn.cursor(row_factory=class_row(QuestionPull))
            ca = list()
            if user_ca is not None:
                ca.extend(user_ca.as_list('submitted_questions'))

            logger.debug('get_sq_by_uuid, submitted questions = %d: %s', len(ca), ca)
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

    def get_new_question_for_user(self, uuid: str, desc: bool = True) -> QuestionPull:
        """**Returns a new question for player, ensuring it has not been answered before**...

        :param desc:
        :param uuid: User uuid aka ident
        :return:

        :raises IndexError if no more questions are available
        """
        order = 'DESC'
        if not desc:
            order = 'ASC'

        with self.__conn_singleton() as conn:
            cur = conn.cursor(row_factory=class_row(User))
            user_ca = cur.execute(
                """
                SELECT
                    *
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
            if user_ca is not None:
                answers.extend(user_ca.as_list('correct_answers'))
                answers.extend(user_ca.as_list('incorrect_answers'))

            logger.debug('get_new_question_for_user, answers = %d: %s', len(answers), answers)

            cur = conn.cursor(row_factory=class_row(QuestionPull))
            all_questions = cur.execute(
                """
                SELECT
                    *
                FROM
                    questions
                ORDER BY
                    questions.votes %s
                """ % order
            ).fetchall()

            applicable_questions = [result for result in all_questions if result.ident not in answers]

            return applicable_questions[0]

    def get_ca_by_name(self, user_name: str) -> list[QuestionPull]:
        """**Returns players already correct answers by user_name**...

        :param user_name: Username
        :return:
        """
        with self.__conn_singleton() as conn:
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
            cur = conn.cursor(row_factory=class_row(QuestionPull))
            ca = list()
            if user_ca is not None:
                ca.extend(user_ca.as_list('correct_answers'))

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

    def add_user(self, user_name: str, password: str) -> str or bool:
        """**Add a new user to the database.**

        :param password:
        :param user_name: it's a username
        :return: unique_uuid of the added user
        """
        unique_id = uuid4()
        with self.__conn_singleton() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO
                        users (
                        USER_NAME,
                        PASSWORD,
                        CORRECT_ANSWERS,
                        INCORRECT_ANSWERS,
                        SUBMITTED_QUESTIONS,
                        SUBMITTED_ADD_VOTES,
                        IDENT
                        )
                    VALUES
                        (
                        %(user_name)s,
                        %(password)s,
                        %(correct_answers)s,
                        %(incorrect_answers)s,
                        %(submitted_questions)s,
                        %(submitted_add_votes)s,
                        %(ident)s
                        )

                """, {
                        'user_name': user_name,
                        'password': password,
                        'correct_answers': "",
                        'incorrect_answers': "",
                        'submitted_questions': "",
                        'submitted_add_votes': "",
                        'ident': unique_id,
                    }
                )
                return str(unique_id)

    def delete_user_by_uuid(self, uuid: str) -> tuple:
        """**Delete a user by UUID.**

        :param uuid: Needs to be in string format for comparison
        :return:
        """
        with self.__conn_singleton() as conn:
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

    def delete_user_by_name(self, user_name: str) -> tuple:
        """**Delete a user by USERNAME.**

        :param user_name: Needs to be in string format for comparison
        :return:
        """
        with self.__conn_singleton() as conn:
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

    def get_user_by_uuid(self, uuid: str) -> User:
        """Get user by UUID"""
        with self.__conn_singleton() as conn:
            cur = conn.cursor(row_factory=class_row(User))
            results = cur.execute(
                """
                SELECT
                    *
                FROM
                    users
                WHERE
                    ident = %(ident)s
            """, {
                    'ident': uuid,
                }
            ).fetchone()
            return results

    def get_user_by_name(self, u_name: str) -> User or None:
        """Get User by username"""
        with self.__conn_singleton() as conn:
            with conn.cursor(row_factory=class_row(User)) as cur:
                sql = "select * from users where user_name = %s"
                results = cur.execute(sql, (u_name,)).fetchone()
                logger.info("get_user results: %s", results)
                if results is not None:
                    return results
                return None

    def check_password(self, user_name: str, password: str) -> bool:
        """**Checks password**...

        :param password:
        :param user_name:
        :return:
        """
        with self.__conn_singleton() as conn:
            with conn.cursor(row_factory=class_row(User)) as cur:
                sql = "select * from users where user_name = %s"
                results = cur.execute(sql, (user_name,)).fetchone()

                if results is not None:
                    password_match = results.password == password
                    logger.debug(
                        'password check %s == %s: %s', results.password, password,
                        password_match)
                    return password_match

                return False


if __name__ == '__main__':
    from utilites.logger_utility import setup_logger

    setup_logger()

    conf = config()
    conf['should_initialize_database'] = True  # No matter what, ensure we clear for testing

    db = TupilaqsDB(conf=conf)

    for i in range(1, 20):
        print(
            db.insert_question(
                question=f"question{i}",
                answer=f"answer{i}",
                title=f"title{i}",
                expl=f"expl{i}",
                votes=random.randrange(1, 100),
                diff=random.randrange(1, 5)
            )
        )
        print(db.add_user(user_name=f"username{i}", password="123"))

    print(db.get_single_question_by_votes())
    print(db.delete_user_by_name("username9"))
    print(db.get_ca_by_name("username1"))

    user_id = db.get_user_by_name('username1').ident

    # FIXME:
    # update_question_votes(question_uuid=q.ident,
    #                       user_uuid=user_id, votes='sub')

    # print(delete_question("0a19adb5-0a10-11ed-a7ee-f6aec268b9bd"))
    #
    # _id = "abdff6b1-0a4d-11ed-8eb0-f6aec268b9bd"
    # update_question_text(_id, text="testdad")
    # update_answer_text(_id, text="testing")
    # update_question_votes(_id, votes=10)
    # update_question_title(_id, title="new title")
    # update_question_difficulty(_id, diff=4)
    # update_question_explanation(_id, expl="new expl")
