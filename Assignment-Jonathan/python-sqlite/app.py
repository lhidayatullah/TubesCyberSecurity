from flask import Flask, render_template, request, redirect, url_for, session, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import bleach
import secrets

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = secrets.token_hex(16)  # Secure session handling

db = SQLAlchemy(app)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    grade = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return f'<Student {self.name}>'

@app.after_request
def set_csp(response):
    response.headers['Content-Security-Policy'] = "script-src 'self';"
    return response

@app.route('/')
def index():
    students = Student.query.all()
    return render_template('index.html', students=students)

@app.route('/add', methods=['POST'])
def add_student():
    name = bleach.clean(request.form['name'])
    age = request.form['age']
    grade = bleach.clean(request.form['grade'])

    if not age.isdigit() or int(age) <= 0:
        return "Invalid age", 400

    new_student = Student(name=name, age=int(age), grade=grade)
    db.session.add(new_student)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:id>', methods=['POST'])
def delete_student(id):
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    student = Student.query.get_or_404(id)

    if request.method == 'POST':
        name = bleach.clean(request.form['name'])
        age = request.form['age']
        grade = bleach.clean(request.form['grade'])

        if not age.isdigit() or int(age) <= 0:
            return "Invalid age", 400

        # Simulate an error page if an edit attempt is made
        abort(403)  # Forbidden

    # Use a session token to validate edit access
    session['edit_token'] = secrets.token_hex(16)
    return render_template('edit.html', student=student, token=session['edit_token'])

@app.route('/update/<int:id>', methods=['POST'])
def update_student(id):
    student = Student.query.get_or_404(id)

    # Verify the session token to prevent direct URL access
    token = request.form.get('token')
    if not token or token != session.get('edit_token'):
        abort(403)  # Forbidden

    name = bleach.clean(request.form['name'])
    age = request.form['age']
    grade = bleach.clean(request.form['grade'])

    if not age.isdigit() or int(age) <= 0:
        return "Invalid age", 400

    student.name = name
    student.age = int(age)
    student.grade = grade
    db.session.commit()

    session.pop('edit_token', None)  # Invalidate the token after use
    return redirect(url_for('index'))

@app.errorhandler(403)
def forbidden_error(error):
    return render_template('403.html'), 403

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)