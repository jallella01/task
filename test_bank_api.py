import unittest
from bank_api import app, db, Bank, Branch

class BankAPITestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = app.test_client()
        with app.app_context():
            db.create_all()
            # Clear any existing data
            db.session.query(Branch).delete()
            db.session.query(Bank).delete()
            # Add test data
            bank = Bank(name="Test Bank")  # Remove explicit id to let SQLAlchemy auto-increment
            db.session.add(bank)
            db.session.flush()  # Ensure bank gets an ID
            branch = Branch(
                ifsc="TEST0001234",
                bank_id=bank.id,
                branch="Test Branch",
                address="123 Test Road",
                city="Test City",
                district="Test District",
                state="Test State"
            )
            db.session.add(branch)
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_get_banks(self):
        response = self.client.get('/api/banks')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], "Test Bank")
        self.assertEqual(len(data[0]['branches']), 1)
        self.assertEqual(data[0]['branches'][0]['ifsc'], "TEST0001234")

    def test_get_branch(self):
        response = self.client.get('/api/branches/TEST0001234')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['ifsc'], "TEST0001234")
        self.assertEqual(data['branch'], "Test Branch")
        self.assertEqual(data['bank']['name'], "Test Bank")

    def test_get_branch_not_found(self):
        response = self.client.get('/api/branches/INVALID1234')
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertEqual(data['error'], "Branch not found")

if __name__ == '__main__':
    unittest.main()