from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, login_required, logout_user, current_user, LoginManager
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize the Flask app and configure the database
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'  # Adjust as necessary
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy and Flask-Login
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    tasks = db.relationship('Task', backref='owner', lazy=True)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(300), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# User loader callback
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Route for Home Page (Task Listing)
@app.route('/')
@login_required
def home():
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return render_template('tasks.html', tasks=tasks)

# Route for Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html')

# Route for Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

# Route for Register Page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)  # Default method

        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# Route for Task Listing Page
@app.route('/tasks')
@login_required
def tasks():
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return render_template('tasks.html', tasks=tasks)

# Route to Add or Edit a Task (Both for creating and updating)
@app.route('/task_form', methods=['GET', 'POST'])
@app.route('/task_form/<int:task_id>', methods=['GET', 'POST'])
@login_required
def task_form(task_id=None):
    task = None
    if task_id:
        task = Task.query.get_or_404(task_id)

    if request.method == 'POST':
        content = request.form['task']
        completed = 'completed' in request.form

        if task:
            task.content = content
            task.completed = completed
        else:
            task = Task(content=content, completed=completed, user_id=current_user.id)
            db.session.add(task)

        db.session.commit()
        flash('Task saved successfully!', 'success')
        return redirect(url_for('home'))

    return render_template('task_form.html', task=task)

# Route to Update a Task's Completed Status
@app.route('/update_task/<int:task_id>')
@login_required
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id == current_user.id:
        task.completed = not task.completed
        db.session.commit()
        flash('Task updated successfully!', 'success')
    else:
        flash('You can only update your own tasks.', 'danger')
    return redirect(url_for('home'))

# Route to Delete a Task
@app.route('/delete_task/<int:task_id>')
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id == current_user.id:
        db.session.delete(task)
        db.session.commit()
        flash('Task deleted successfully!', 'success')
    else:
        flash('You can only delete your own tasks.', 'danger')
    return redirect(url_for('home'))

# Route for About Page
@app.route('/about')
def about():
    return render_template('about.html')

# Main entry point to run the application
if __name__ == '__main__':
    # Create all the tables in the database (only needed once)
    with app.app_context():
        db.create_all()
    app.run(debug=True)
