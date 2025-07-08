# Bank API Service

## Overview
This REST API server, built with Flask and SQLAlchemy, provides access to Indian bank and branch information based on the [Indian Bank IFSC Codes dataset](https://github.com/snarayanank2/indian_banks). It includes endpoints to retrieve a list of all banks with their branches and specific branch details by IFSC code, fulfilling the requirements of the REST API assignment. The project includes unit tests, error handling, and deployment instructions for Heroku.

## Time Taken
- **Total**: ~5 hours
- **Breakdown**:
  - Environment setup and data preparation: 0.5 hours
  - Database design and data loading: 1 hour
  - API implementation: 1.5 hours
  - Testing: 1 hour
  - Documentation and deployment setup: 0.5 hours
  - Debugging (application context error, invalid bank reference, test UNIQUE constraint): 0.5 hours (completed by 10:13 PM IST, July 08, 2025)
  - Note: Time includes iterative fixes for data integrity and test issues.

## Project Structure
```
bank-api/
├── data/
│   ├── bank_branches.csv           # Full CSV dump (optional, large)
│   ├── bank_branches_small.csv     # Subset for local testing
│   └── indian_banks.sql            # PostgreSQL dump
├── bank_api.py                     # Flask app with API endpoints
├── test_bank_api.py                # Unit tests
├── README.md                       # Documentation
├── requirements.txt                # Dependencies
├── Procfile                        # Heroku configuration
└── .gitignore                      # Git ignore file
```

## Setup Instructions
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/bank-api.git
   cd bank-api
   ```

2. **Set Up Virtual Environment**:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Linux/Mac
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Prepare Data**:
   - Place `bank_branches_small.csv` in the `data/` directory (subset of `bank_branches.csv` for testing).
   - Optionally, download `bank_branches.csv` or `indian_banks.sql` from [https://github.com/snarayanank2/indian_banks](https://github.com/snarayanank2/indian_banks).
   - To create a small CSV:
     ```python
     import pandas as pd
     df = pd.read_csv('data/bank_branches.csv')
     df.head(100).to_csv('data/bank_branches_small.csv', index=False)
     ```

5. **Run the Application**:
   ```bash
   python bank_api.py
   ```

6. **Run Tests**:
   ```bash
   python test_bank_api.py
   ```

## API Endpoints
- **GET /api/banks**:
  - Returns a list of all banks with their branches.
  - Example:
    ```bash
    curl http://localhost:5000/api/banks
    ```
  - Response:
    ```json
    [
      {
        "id": 1,
        "name": "ABHYUDAYA COOPERATIVE BANK LIMITED",
        "branches": [
          {
            "ifsc": "ABHY0065001",
            "branch": "MAIN BRANCH",
            "address": "K.K. TOWERS, ABHYUDAYA BANK BLDG., MUMBAI",
            "city": "MUMBAI",
            "district": "MUMBAI",
            "state": "MAHARASHTRA"
          },
          ...
        ]
      },
      ...
    ]
    ```

- **GET /api/branches/<ifsc>**:
  - Returns details for a specific branch by IFSC code.
  - Example:
    ```bash
    curl http://localhost:5000/api/branches/ABHY0065001
    ```
  - Response:
    ```json
    {
      "ifsc": "ABHY0065001",
      "branch": "MAIN BRANCH",
      "address": "K.K. TOWERS, ABHYUDAYA BANK BLDG., MUMBAI",
      "city": "MUMBAI",
      "district": "MUMBAI",
      "state": "MAHARASHTRA",
      "bank": {
        "id": 1,
        "name": "ABHYUDAYA COOPERATIVE BANK LIMITED"
      }
    }
    ```
  - Error Responses:
    - `404`: `{"error": "Branch not found"}`
    - `400`: `{"error": "Branch has invalid bank reference"}`

## Implementation Details
- **Framework**: Flask with Flask-SQLAlchemy for ORM.
- **Database**:
  - Local: SQLite with `bank.db`.
  - Production: PostgreSQL (e.g., Heroku).
  - Schema:
    - `banks`: `id` (Integer, PK), `name` (String(49)).
    - `branches`: `ifsc` (String(11), PK), `bank_id` (FK to `banks.id`), `branch` (String(74)), `address` (String(195)), `city` (String(50)), `district` (String(50)), `state` (String(26)).
- **Data Loading**:
  - Uses `pandas` to load `bank_branches_small.csv` or `bank_branches.csv`.
  - Cleans bank names (strip whitespace, uppercase, handle nulls).
  - Logs skipped branches with invalid bank references.
- **Features**:
  - Error handling for missing branches or invalid bank references.
  - SQLite foreign key enforcement to ensure data integrity.
  - Logging for debugging data loading issues.
- **Testing**:
  - Unit tests in `test_bank_api.py` cover:
    - Retrieving all banks (`test_get_banks`).
    - Retrieving a branch by IFSC (`test_get_branch`).
    - Handling invalid IFSC codes (`test_get_branch_not_found`).
  - Tests use an in-memory SQLite database for isolation.
- **Deployment**: Configured for Heroku with PostgreSQL support.

## Debugging and Fixes
- **Application Context Error**: Fixed by moving SQLite foreign key registration into `init_db` function.
- **Invalid Bank Reference**: Addressed by cleaning bank names and skipping branches with missing banks during data loading.
- **Test UNIQUE Constraint Error**: Resolved by clearing the database in `test_bank_api.py` `setUp` and using auto-incremented IDs.
- **Data Issues**: Ensured `ABHY0065001` loads correctly by verifying CSV content.

## Deployment on Heroku
1. **Install Heroku CLI**:
   ```bash
   heroku login
   ```

2. **Create a Heroku App**:
   ```bash
   heroku create
   ```

3. **Add PostgreSQL Add-on**:
   ```bash
   heroku addons:create heroku-postgresql:hobby-dev
   ```

4. **Set Environment Variable**:
   ```bash
   heroku config:set DATABASE_URL=$(heroku config:get DATABASE_URL)
   ```

5. **Push to Heroku**:
   ```bash
   git push heroku main
   ```

6. **Load Data into PostgreSQL**:
   ```bash
   psql $(heroku config:get DATABASE_URL) < data/indian_banks.sql
   ```

7. **Test Deployed App**:
   ```bash
   heroku open
   curl https://<app-name>.herokuapp.com/api/banks
   ```

## Future Improvements
- Add pagination for `/api/banks` to handle large datasets (127,857 branches).
- Implement caching for performance.
- Add input validation for IFSC code format.
- Generate API documentation with Swagger.

## Data Source
- [Indian Bank IFSC Codes](https://github.com/snarayanank2/indian_banks)
- Contains 170 banks and 127,857 branches.

## Notes
- Ensure `bank_branches_small.csv` includes `ABHY0065001` with `bank_name="ABHYUDAYA COOPERATIVE BANK LIMITED"`.
- For production, use `indian_banks.sql` to avoid CSV loading issues.
- The project avoids using prohibited names and includes tests for bonus points.
