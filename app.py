import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime # Import datetime for explicit timestamp handling if needed

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
app.config['SECRET_KEY'] = 'your_super_secret_key_here' # Add a secret key for flash messages

db = SQLAlchemy(app)
migrate = Migrate(app, db) # Initialize Flask-Migrate

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
    # Redirect users from the homepage to the new ticket form
    return redirect(url_for('new_ticket_route'))

# --- New Ticket Form Route ---
@app.route('/new')
def new_ticket_route():
    return render_template('new_ticket.html')

# --- New Ticket Submission Route ---
# This route handles the POST request from the new_ticket.html form
@app.route('/submit_ticket', methods=['POST'])
def submit_ticket():
    if request.method == 'POST':
        try:
            # Get data from the form using request.form
            submitter_name = request.form['submitter_name']
            submitter_email = request.form['submitter_email']
            department = request.form['department']
            issue_title = request.form['issue_title']
            description = request.form['description']
            urgency = request.form['urgency']

            # Create a new Ticket instance
            new_ticket = Ticket(
                submitter_name=submitter_name,
                submitter_email=submitter_email,
                department=department,
                issue_title=issue_title,
                description=description,
                urgency=urgency,
                status='Open' # Default status for new tickets
            )

            # Add the new ticket to the database session
            db.session.add(new_ticket)
            # Commit the transaction to save the ticket to the database
            db.session.commit()

            # Use flash messages to give feedback to the user
            flash('Your ticket has been submitted successfully!', 'success')

            # Redirect to a confirmation page or back to the new ticket form
            # For now, redirecting back to the new ticket form, which will show the flash message
            return redirect(url_for('new_ticket_route'))

        except Exception as e:
            # Rollback the session in case of an error to prevent inconsistent state
            db.session.rollback()
            # Log the error for debugging purposes
            print(f"Error submitting ticket: {e}")
            # Flash an error message to the user
            flash(f'An error occurred: {e}', 'error')
            # Redirect back to the form to allow resubmission or display error
            return redirect(url_for('new_ticket_route'))

# --- Example Route for Listing Tickets (You'll expand on this later) ---
@app.route('/tickets')
def list_tickets():
    # Fetch all tickets from the database
    # For a real app, you'd add filtering, pagination, etc.
    tickets = Ticket.query.all()
    return render_template('tickets.html', tickets=tickets) # You'll need to create tickets.html

# --- Main entry point for running the Flask app ---
if __name__ == '__main__':
    # This block is for local development.
    # On Render, your web server (like Gunicorn) will handle running the app.
    with app.app_context():
        db.create_all() # Create database tables if they don't exist
    app.run(debug=True) # Run in debug mode for development
