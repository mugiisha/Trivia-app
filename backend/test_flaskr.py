import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category
from settings import TEST_DB_NAME,DB_PASSWORD,DB_USER


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = TEST_DB_NAME
        self.database_user=DB_USER
        self.database_password=DB_PASSWORD
        self.database_path = 'postgresql://{}:{}@{}/{}'.format(self.database_user,self.database_password,'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {"question": "who is muhota", "answer": "he is the next pop start", "category": 5, "difficulty": 1}
        self.search_term={'searchTerm': 'palace'}
        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])

    def test_unallowed_method_on_categories(self):
        res = self.client().patch('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['message'], 'method not allowed')
    
    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['totalQuestions'])
        self.assertTrue(data['categories'])

    def test_unallowed_method_on_questions(self):
        res = self.client().patch('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['message'], 'method not allowed')

    def test_delete_question(self):
        res = self.client().delete('/questions/39')
        data = json.loads(res.data)
        question = Question.query.filter(Question.id == 39).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'],True)
        self.assertEqual(data['deleted'],39)
        self.assertEqual(question, None)

    def test_delete_unavailable_question(self):
        res = self.client().delete('/questions/10000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['message'], 'resource not found')


    def test_create_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['created'])

    def test_search_question(self):
        res = self.client().post('/questions/search', json=self.search_term)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['current_category'])
        self.assertTrue(data['total_questions'])

    def test_get_questions_by_category(self):
        res=self.client().get('/categories/2/questions')
        data=json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertTrue(data['questions'])
        self.assertEqual(data['current_category'],2)
        self.assertEqual(data['total_questions'],len(Question.query.filter(Question.category == 2).all()))
    
    def test_unallowed_method_on_get_questions_by_categories(self):
        res = self.client().patch('/categories/2/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['message'], 'method not allowed')
    
    def test_get_quiz(self):
        res = self.client().post('/quizzes',  json={"previous_questions": [], "quiz_category": {'id': 1, 'type': 'Science'}})
        data=json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['question'])

    def test_unprocessable__get_quiz(self):
        res = self.client().post('/quizzes',  json={})
        data=json.loads(res.data)
        self.assertEqual(res.status_code,422)
        self.assertEqual(data['message'],'unprocessable')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()