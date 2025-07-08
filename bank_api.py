from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///bank.db').replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Models
class Bank(db.Model):
    __tablename__ = 'banks'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(49), nullable=False)
    branches = db.relationship('Branch', backref='bank', lazy=True)

class Branch(db.Model):
    __tablename__ = 'branches'
    ifsc = db.Column(db.String(11), primary_key=True)
    bank_id = db.Column(db.Integer, db.ForeignKey('banks.id'), nullable=False)
    branch = db.Column(db.String(74), nullable=False)
    address = db.Column(db.String(195), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    district = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(26), nullable=False)

# Enable SQLite foreign key constraints and create database
def init_db():
    with app.app_context():
        db.create_all()
        if app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite'):
            @db.event.listens_for(db.engine, "connect")
            def set_sqlite_pragma(dbapi_connection, connection_record):
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()

# Load data from CSV
def load_data(csv_file='data/bank_branches_small.csv'):
    with app.app_context():
        if Bank.query.first():
            logger.info("Database already populated, skipping data load.")
            return
        try:
            df = pd.read_csv(csv_file)
            # Clean bank names
            df['bank_name'] = df['bank_name'].str.strip().str.upper()
            # Handle missing bank names
            df['bank_name'] = df['bank_name'].fillna('UNKNOWN_BANK')
            # Ensure unique banks
            banks = df[['bank_name']].drop_duplicates().reset_index(drop=True)
            banks['id'] = banks.index + 1
            # Insert banks
            bank_id_map = {}
            for _, row in banks.iterrows():
                bank = Bank(id=row['id'], name=row['bank_name'])
                db.session.add(bank)
                bank_id_map[row['bank_name']] = row['id']
            db.session.flush()
            # Insert branches
            skipped_branches = []
            for _, row in df.iterrows():
                bank_name = row['bank_name']
                if bank_name not in bank_id_map:
                    logger.warning(f"Skipping branch {row['ifsc']} with missing bank: {bank_name}")
                    skipped_branches.append(row['ifsc'])
                    continue
                branch = Branch(
                    ifsc=row['ifsc'],
                    bank_id=bank_id_map[bank_name],
                    branch=str(row['branch']),
                    address=str(row['address']),
                    city=str(row['city']),
                    district=str(row['district']),
                    state=str(row['state'])
                )
                try:
                    db.session.add(branch)
                except Exception as e:
                    logger.warning(f"Failed to add branch {row['ifsc']}: {str(e)}")
                    skipped_branches.append(row['ifsc'])
            db.session.commit()
            logger.info(f"Loaded {len(banks)} banks and {Branch.query.count()} branches.")
            if skipped_branches:
                logger.info(f"Skipped {len(skipped_branches)} branches: {skipped_branches[:5]}...")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error loading data: {str(e)}")
            raise

# API Endpoints
@app.route('/api/banks', methods=['GET'])
def get_banks():
    banks = Bank.query.all()
    return jsonify([{
        'id': bank.id,
        'name': bank.name,
        'branches': [{
            'ifsc': branch.ifsc,
            'branch': branch.branch,
            'address': branch.address,
            'city': branch.city,
            'district': branch.district,
            'state': branch.state
        } for branch in bank.branches]
    } for bank in banks])

@app.route('/api/branches/<ifsc>', methods=['GET'])
def get_branch(ifsc):
    branch = Branch.query.get(ifsc)
    if not branch:
        return jsonify({'error': 'Branch not found'}), 404
    if not branch.bank:
        logger.error(f"Branch {ifsc} has invalid bank_id: {branch.bank_id}")
        return jsonify({'error': 'Branch has invalid bank reference'}), 400
    return jsonify({
        'ifsc': branch.ifsc,
        'branch': branch.branch,
        'address': branch.address,
        'city': branch.city,
        'district': branch.district,
        'state': branch.state,
        'bank': {
            'id': branch.bank.id,
            'name': branch.bank.name
        }
    })

if __name__ == '__main__':
    init_db()
    load_data()
    app.run(debug=True)