import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime

app = Flask(__name__)

# --- DATABASE CONFIGURATION ---
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///tickets.db')
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'a_very_secret_and_random_key_for_flash_messages')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# --- DATABASE MODEL ---
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

    def __repr__(self):
        return f"<Ticket {self.id}: {self.issue_title}>"

# --- Homepage Route ---
@app.route('/')
def index():
    return redirect(url_for('new_ticket_route'))

# --- New Ticket Form Route ---
@app.route('/new')
def new_ticket_route():
    return render_template('new_ticket.html')

# --- New Ticket Submission Route (Now expecting JSON) ---
@app.route('/submit_ticket', methods=['POST'])
def submit_ticket():
    data = request.get_json()

    print("--- Received JSON Data ---")
    print(data)
    print("--------------------------")

    if not data:
        print("No JSON data received.")
        return jsonify({"message": "Invalid JSON or no data provided"}), 400

    try:
        submitter_name = data.get('submitter_name')
        submitter_email = data.get('submitter_email')
        department = data.get('department')
        issue_title = data.get('issue_title')
        description = data.get('description')
        urgency = data.get('urgency')

        if not submitter_name or not submitter_email or not issue_title or not description or not urgency:
            missing_fields = []
            if not submitter_name: missing_fields.append('submitter_name')
            if not submitter_email: missing_fields.append('submitter_email')
            if not issue_title: missing_fields.append('issue_title')
            if not description: missing_fields.append('description')
            if not urgency: missing_fields.append('urgency')

            error_message = f'Missing required fields: {", ".join(missing_fields)}.'
            print(error_message)
            return jsonify({"message": error_message}), 400

        new_ticket = Ticket(
            submitter_name=submitter_name,
            submitter_email=submitter_email,
            department=department,
            issue_title=issue_title,
            description=description,
            urgency=urgency,
            status='Open'
        )

        db.session.add(new_ticket)
        db.session.commit()

        return jsonify({"message": "Ticket submitted successfully!"}), 200

    except Exception as e:
        db.session.rollback()
        print(f"An unexpected error occurred during ticket submission: {e}")
        return jsonify({"message": f"Server error: {e}"}), 500

# --- Example Route for Listing Tickets ---
@app.route('/tickets')
def list_tickets():
    tickets = Ticket.query.all()
    return render_template('tickets.html', tickets=tickets)

# --- Main entry point for running the Flask app ---
if __name__ == '__main__':
    # This block is for local development.
    # On Render, your web server (like Gunicorn) will handle running the app,
    # and migrations (flask db upgrade) will handle table creation.
    with app.app_context(): # This will now only run when app.py is executed directly
        db.create_all() # Good for initial local setup if not using migrations yet
    app.run(debug=True)
