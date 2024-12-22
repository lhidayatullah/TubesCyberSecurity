from flask import Flask, render_template, request, redirect, url_for, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import sqlite3

app = Flask(__name__)
app.secret_key = b'\x13\x8c\xfb\xcf\x1b\xe4\xb8\x8a\x10\x93\xcf\x89\x98\x1f\x1d\xd8\x8a\x9b\xcb\xe1'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

AUTHORIZED_USER = {
    'username': 'admin',
    'password': 'admin123'
}

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    grade = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return f'<Student {self.name}>'

# Login route
@app.route('/login')
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin123':
            session['role'] = 'admin'
            return redirect(url_for('dashboard'))
        elif username == 'viewer' and password == 'viewer123':
            session['role'] = 'viewer'
            return redirect(url_for('dashboard'))
        else:
            return "Invalid credentials", 401
    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if 'role' in session:
        role = session['role']
        if role == 'admin':
            return render_template('dashboard.html')
        elif role == 'viewer':
            return render_template('viewer_dashboard.html')
    return redirect(url_for('login'))



# Logout route
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# Authorization decorator
def login_required(f):
    def wrapper(*args, **kwargs):
        if 'user' not in session:
            flash('You must be logged in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper


@app.route('/')
def index():
    # RAW Query
    students = db.session.execute(text('SELECT * FROM student')).fetchall()
    return render_template('viewer_dashboard.html', students=students)

@app.route('/add', methods=['POST'])
def add_student():
    name = request.form['name']
    age = request.form['age']
    grade = request.form['grade']
    

    connection = sqlite3.connect('instance/students.db')
    cursor = connection.cursor()

    # RAW Query
    # db.session.execute(
    #     text("INSERT INTO student (name, age, grade) VALUES (:name, :age, :grade)"),
    #     {'name': name, 'age': age, 'grade': grade}
    # )
    # db.session.commit()
    query = f"INSERT INTO student (name, age, grade) VALUES ('{name}', {age}, '{grade}')"
    cursor.execute(query)
    connection.commit()
    connection.close()
    return redirect(url_for('index'))


@app.route('/delete/<string:id>') 
def delete_student(id):
    # RAW Query
    db.session.execute(text(f"DELETE FROM student WHERE id={id}"))
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_student(id):
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        grade = request.form['grade']
        
        # RAW Query
        db.session.execute(text(f"UPDATE student SET name=:name, age=:age, grade=:grade WHERE id=:id"), 
                           {'name': name, 'age': age, 'grade': grade, 'id': id})
        db.session.commit()
        flash('Student updated successfully!', 'success')
        return redirect(url_for('index'))
    else:
        # RAW Query
        student = db.session.execute(text("SELECT * FROM student WHERE id=:id"), {'id': id}).fetchone()
        if not student:
            flash('Student not found!', 'danger')
            return redirect(url_for('index'))
        return render_template('edit.html', student=student)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)

