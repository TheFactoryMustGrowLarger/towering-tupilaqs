import logging
import random
import unittest

from db.api import TupilaqsDB
from db.db_config.config import config

logger = logging.getLogger('tupilaqs.db.test')


class TestDatabase(unittest.TestCase):
    """Test database"""

    def setUp(self):
        """Initialize database with dummy data"""
        conf = config()
        conf['should_initialize_database'] = True  # No matter what, ensure we clear for testing

        self.db = TupilaqsDB(conf)
        for i in range(1, 20):
            q = self.db.insert_question(
                question=f"question{i}",
                answer=f"answer{i}",
                title=f"title{i}",
                expl=f"expl{i}",
                votes=random.randrange(1, 100),
                diff=random.randrange(1, 5)
            )
            logger.info('setting up database, added %s', q)

            u = self.db.add_user(user_name=f"username{i}", password='123')
            logger.info('setting up database, added user %s', u)

    def tearDown(self):
        """Do nothing for now"""
        pass

    def test_number_of_questions(self):
        """Check setup added 10 question"""
        questions = self.db.get_all_questions()
        self.assertEqual(len(questions), 10)

    def add_correct_answers(self, user_id, number_of_correct_questions, start=0):
        """Add N correct answers"""
        user_id = self.db.get_user_by_name('username1').ident
        questions = self.db.get_all_questions()

        # Add correct answers:
        for q in questions[:number_of_correct_questions]:
            self.db.update_user_ca_by_uuid(user_id, ca=q.ident)

    def add_incorrect_answers(self, user_id, number_of_incorrect_questions, start=0):
        """Add N incorrect answers"""
        questions = self.db.get_all_questions()

        # add incorrect answers:
        end = start + number_of_incorrect_questions
        for q in questions[start:end]:
            self.db.update_user_ia_by_uuid(user_id, ia=q.ident)

    def add_submitted_questions(self, user_id, number_of_submitted_questions, start=0):
        """Add N submitteed questions"""
        questions = self.db.get_all_questions()

        # add submitted questions:
        end = start + number_of_submitted_questions
        for q in questions[start:end]:
            self.db.update_user_sq_by_uuid(user_id, sq=q.ident)

    def test_add_questions_answers(self, number_of_correct_questions=5, number_of_incorrect_questions=3):
        """Check that we can add both correct and incorrect questions to a user"""
        user_id = self.db.get_user_by_name('username1').ident

        self.add_correct_answers(user_id, number_of_correct_questions)
        self.add_incorrect_answers(user_id, number_of_incorrect_questions, start=number_of_correct_questions)

        correct_answers = self.db.get_ca_by_uuid(user_id)
        incorrect_answers = self.db.get_ia_by_uuid(user_id)

        self.assertEqual(len(correct_answers), number_of_correct_questions)
        self.assertEqual(len(incorrect_answers), number_of_incorrect_questions)

    def test_new_answer_is_new(self, number_of_correct_questions=5, number_of_incorrect_questions=3):
        """Check that get_new_question_for_user does not return any of the already answered questions"""
        user_id = self.db.get_user_by_name('username1').ident

        self.add_correct_answers(user_id, number_of_correct_questions)
        self.add_incorrect_answers(user_id, number_of_incorrect_questions, start=number_of_correct_questions)

        correct_answers = self.db.get_ca_by_uuid(user_id)
        incorrect_answers = self.db.get_ia_by_uuid(user_id)

        correct_answers_ident = [item.ident for item in correct_answers]
        incorrect_answers_ident = [item.ident for item in incorrect_answers]

        q = self.db.get_new_question_for_user(user_id)
        self.assertNotIn(q.ident, correct_answers_ident)
        self.assertNotIn(q.ident, incorrect_answers_ident)
        print('New question', q)

    def test_user_submitted_questions(self, number_of_submitted_questions=2):
        """Test submitted questions"""
        user_id = self.db.get_user_by_name('username1').ident
        submitted = self.db.get_sq_by_uuid(user_id)
        self.assertEqual(len(submitted), 0)

        self.add_submitted_questions(user_id, number_of_submitted_questions)

        submitted = self.db.get_sq_by_uuid(user_id)
        self.assertEqual(len(submitted), number_of_submitted_questions)

    def test_voted_up_questions(self):
        """Test voted up questions"""
        questions = self.db.get_all_questions()
        user_id1 = self.db.get_user_by_name('username1').ident

        q = questions[0]
        update_success = self.db.update_user_sv_up_by_uuid(user_id1, sv=q.ident)
        self.assertTrue(update_success)

        update_success = self.db.update_user_sv_up_by_uuid(user_id1, sv=q.ident)
        self.assertFalse(update_success, msg='Already added, not did expect this to work the second time around')

        # Let the second user upvote
        user_id2 = self.db.get_user_by_name('username2').ident
        self.assertNotEqual(user_id1, user_id2)

        update_success = self.db.update_user_sv_up_by_uuid(user_id2, sv=q.ident)
        self.assertTrue(update_success)

        update_success = self.db.update_user_sv_up_by_uuid(user_id2, sv=q.ident)
        self.assertFalse(update_success, msg='Already added, not did expect this to work the second time around')

    def test_user_submitted_questions_votes(self, nr_questions_to_upvote=3, upvotes=10):
        """Test total votes for user-submitted questions"""
        questions = self.db.get_all_questions()
        user_id = self.db.get_user_by_name('username1').ident

        # Assign questions to user
        self.add_submitted_questions(user_id, nr_questions_to_upvote, start=0)

        # Set fixed votes:
        for ix in range(nr_questions_to_upvote):
            self.db.update_question_votes(question_uuid=questions[ix].ident,
                                          user_uuid=user_id,
                                          new_vote_override=upvotes)

        user_questions = self.db.get_sq_by_uuid(user_id)
        question_uuids = [item.ident for item in user_questions]
        votes = self.db.get_total_votes_questions(question_uuids)

        expected_votes = nr_questions_to_upvote*upvotes
        self.assertEqual(votes, expected_votes)


if __name__ == '__main__':
    from utilites.logger_utility import setup_logger
    setup_logger()

    unittest.main()
