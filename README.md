# Finance Data Processing and Access Control Backend

A backend API for managing financial records with role-based access control. Built with FastAPI and SQLite.

## Tech Stack

- Python
- FastAPI
- SQLAlchemy
- SQLite
- JWT Authentication

## Project Structure

```
finance-backend/
├── app/
│   ├── database.py             # database connection setup
│   ├── models/
│   │   ├── user.py             # user table model
│   │   └── financial.py        # financial records table model
│   ├── routes/
│   │   ├── auth.py             # register and login routes
│   │   ├── users.py            # user management routes
│   │   ├── records.py          # financial records routes
│   │   └── dashboard.py        # summary and analytics routes
│   └── services/
│       ├── auth.py             # password hashing and JWT logic
│       └── access_control.py   # role based access control
├── main.py                     # app entry point
├── .env                        # environment variables
└── README.md
```

## Setup Instructions

1. Clone the repository
2. Create a virtual environment
   ```
   python -m venv venv
   venv\Scripts\activate
   ```
3. Install dependencies
   ```
   pip install fastapi uvicorn sqlalchemy python-jose passlib python-multipart python-dotenv email-validator
   ```
4. Create a `.env` file in the root folder with the following:
   ```
   DATABASE_URL=sqlite:///./finance.db
   SECRET_KEY=mysecretkey123
   ```
5. Run the server
   ```
   uvicorn main:app --reload
   ```
6. Open API docs at `http://127.0.0.1:8000/docs`

## Roles

| Role | Permissions |
|------|-------------|
| Admin | Full access - create, update, delete records and manage users |
| Analyst | Can view records and access dashboard insights |
| Viewer | Can only view basic dashboard summary |

## API Endpoints

### Auth
| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| POST | /auth/register | Register a new user | Public |
| POST | /auth/login | Login and get token | Public |

### Users
| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | /users/ | Get all users | Admin |
| GET | /users/me | Get my profile | All |
| PUT | /users/{id}/role | Update user role | Admin |
| PUT | /users/{id}/status | Activate or deactivate user | Admin |
| DELETE | /users/{id} | Delete user | Admin |

### Financial Records
| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| POST | /records/ | Create a record | Admin |
| GET | /records/ | Get all records with filters | All |
| GET | /records/{id} | Get single record | All |
| PUT | /records/{id} | Update a record | Admin |
| DELETE | /records/{id} | Soft delete a record | Admin |

### Dashboard
| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | /dashboard/summary | Total income, expense, balance | All |
| GET | /dashboard/categories | Category wise totals | Analyst, Admin |
| GET | /dashboard/recent | Last 10 transactions | All |
| GET | /dashboard/trends | Monthly trends for last 6 months | Analyst, Admin |

## Assumptions

- Admin is the only role that can create, update or delete financial records
- Soft delete is used for financial records so history is preserved
- SQLite is used for simplicity since this is a local development setup
- Passwords are hashed using SHA256 before storing in the database
- JWT tokens expire after 30 minutes

## How Authentication Works

1. Register a user using `/auth/register`
2. Login using `/auth/login` to get a JWT token
3. Use that token in the Authorization header as `Bearer <token>` for all protected routes

## Tradeoffs

- Used SQLite instead of PostgreSQL to keep setup simple
- Used SHA256 for password hashing instead of bcrypt due to Python 3.14 compatibility issues
- No pagination implemented to keep the code simple and readable
