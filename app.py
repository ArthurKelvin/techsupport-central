import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)

# --- DATABASE CONFIGURATION ---
# Get the database URL from the environment variable.
# If it's not set, default to a local SQLite database.
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///tickets.db')
# This replaces the postgres:// protocol with postgresql:// which SQLAlchemy needs.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Optional: to suppress a warning

db = SQLAlchemy(app)
migrate = Migrate(app, db) # Initialize Flask-Migrate

# --- DATABASE MODEL ---
# This replaces our old data model description. It's now a Python class.
class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    submitter_name = db.Column(db.String(100), nullable=False)
    submitter_email = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100))
    issue_title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    urgency = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Open')
    technician_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    
    # --- Homepage Route ---
@app.route('/')
def index():
    # Redirect users from the homepage to the new ticket form
    return redirect(url_for('new_ticket_route')) 

# --- Make sure your new ticket route has a function name ---
@app.route('/new')
def new_ticket_route(): # give it a name like this
    return render_template('new_ticket.html')

# ... your other routes

# --- Your Flask Routes (@app.route(...)) will go here ---
# You will need to change your database logic from raw SQL
# to SQLAlchemy commands. For example:
# To get all open tickets: tickets = Ticket.query.filter_by(status='Open').all()
# To create a new ticket:
# new_ticket = Ticket(...)
# db.session.add(new_ticket)
# db.session.commit()