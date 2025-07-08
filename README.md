Bank API Service
Overview
This REST API server, built with Flask and SQLAlchemy, provides access to Indian bank and branch information based on the Indian Bank IFSC Codes dataset. It includes endpoints to retrieve bank lists and specific branch details by IFSC code.
Time Taken

Total: ~4.5 hours
Breakdown:
Environment setup and data preparation: 0.5 hours
Database design and data loading: 1 hour
API implementation: 1.5 hours
Testing: 1 hour
Documentation and deployment setup: 0.5 hours



Setup Instructions

Clone the repository.
Install dependencies:pip install -r requirements.txt


Place bank_branches.csv (or a subset) in a data/ directory.
Run the application:python bank_api.py


Run tests:python test_bank_api.py



API Endpoints

GET /api/banks: Returns all banks with their branches.
GET /api/branches/<ifsc>: Returns details for a branch by IFSC code.

Implementation Details

Framework: Flask with SQLAlchemy.
Database: SQLite (local), PostgreSQL (production).
Data Model:
banks: id (Integer), name (String).
branches: ifsc (String, PK), bank_id (FK), branch, address, city, district, state (Strings).


Data Loading: Uses pandas to load bank_branches.csv.
Features:
Clean code with modular structure.
Error handling for invalid IFSC codes.
Unit tests with unittest.


Testing: Covers success and error cases.
Deployment: Configured for Heroku with PostgreSQL.

Deployment on Heroku

Install Heroku CLI and log in:heroku login


Create a Heroku app:heroku create


Add PostgreSQL add-on:heroku addons:create heroku-postgresql:hobby-dev


Set environment variable:heroku config:set DATABASE_URL=$(heroku config:get DATABASE_URL)


Push to Heroku:git push heroku main


Load data into PostgreSQL (see below).

PostgreSQL Setup (Production)

Import the SQL dump:psql $DATABASE_URL < data/indian_banks.sql


Update bank_api.py to use PostgreSQL URI:app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///bank.db')


Disable CSV loading in production (comment out load_data()).

Future Improvements

Add pagination for /api/banks.
Implement caching for performance.
Add input validation for IFSC format.
Generate API documentation with Swagger.

Data Source

Indian Bank IFSC Codes
Contains 170 banks and 127,857 branches.
