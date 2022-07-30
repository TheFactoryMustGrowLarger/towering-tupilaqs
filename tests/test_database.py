import logging
import random
import unittest

import db.api

logger = logging.getLogger('tupilaqs.db.test')


class TestDatabase(unittest.TestCase):
    """Test database"""

    def setUp(self):
        """Initialize database with dummy data"""
        db.api.initiate_database()
        self.db = db.api  # lets pretend code is OO
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


if __name__ == '__main__':
    from utilites.logger_utility import setup_logger
    setup_logger()

    unittest.main()
