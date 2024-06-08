from flask import Flask, render_template, request, redirect, url_for, session, g
from models import db, User, TutorInfo, StudentRequest, Review
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tutoring_service.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.before_first_request
def create_tables():
    db.create_all()

@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        new_user = User(username=username, password=password, role=role)
        try:
            db.session.add(new_user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return "用户名已存在"
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('home'))
        else:
            return "用户名或密码错误"
    return render_template('login.html')

@app.route('/tutor-form', methods=['GET', 'POST'])
def tutor_form():
    if not g.user:
        return redirect(url_for('login'))
    if request.method == 'POST':
        tutor_info = TutorInfo(
            user_id=g.user.id,
            name=request.form['name'],
            subject=request.form['subject'],
            grade=request.form['grade'],
            time=request.form['time'],
            rate=request.form['rate']
        )
        db.session.add(tutor_info)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('tutor_form.html')

@app.route('/student-form', methods=['GET', 'POST'])
def student_form():
    if not g.user:
        return redirect(url_for('login'))
    if request.method == 'POST':
        student_request = StudentRequest(
            user_id=g.user.id,
            name=request.form['name'],
            subject=request.form['subject'],
            grade=request.form['grade'],
            time=request.form['time'],
            budget=request.form['budget']
        )
        db.session.add(student_request)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('student_form.html')

@app.route('/tutors')
def tutors():
    tutor_infos = TutorInfo.query.all()
    return render_template('tutors.html', tutors=tutor_infos)

@app.route('/tutor/<int:tutor_id>')
def tutor_detail(tutor_id):
    tutor = TutorInfo.query.get_or_404(tutor_id)
    reviews = Review.query.filter_by(tutor_id=tutor_id).all()
    return render_template('tutor_detail.html', tutor=tutor, reviews=reviews)

@app.route('/matching')
def matching():
    if not g.user:
        return redirect(url_for('login'))
    matches = TutorInfo.query.filter(TutorInfo.subject.in_(
        [req.subject for req in StudentRequest.query.all()])).all()
    return render_template('matching.html', matches=matches)

@app.route('/review', methods=['GET', 'POST'])
def review():
    if not g.user:
        return redirect(url_for('login'))
    if request.method == 'POST':
        tutor_name = request.form['tutor_name']
        tutor = TutorInfo.query.filter_by(name=tutor_name).first()
        if tutor:
            review = Review(
                tutor_id=tutor.id,
                user_id=g.user.id,
                username=g.user.username,
                review=request.form['review']
            )
            db.session.add(review)
            db.session.commit()
            return redirect(url_for('tutor_detail', tutor_id=tutor.id))
        else:
            return "家教不存在"
    return render_template('review.html')

if __name__ == '__main__':
    app.run(debug=True)
