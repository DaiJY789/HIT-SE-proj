from flask import Flask, render_template, request, redirect, url_for, session, g, flash
from models import db, User, TutorInfo, StudentRequest, Review
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tutoring_service.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


# @app.before_request 是 Flask 中的一个装饰器，用于注册一个在每次请求处理之前执行的函数
@app.before_request
def create_tables():
    if not hasattr(g, 'first_request'):  # 保证该函数只在第一次访问时执行
        g.first_request = True
        db.create_all()  # 创建所有在模型中定义的数据库表格


@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])


@app.route('/')
def home():
    return render_template('new_home.html')


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
            user_id = g.user.id,
            name = request.form['name'],
            subject = request.form['subject'],
            grade = request.form['grade'],
            time = request.form['time'],
            budget = request.form['budget']

        )
        db.session.add(student_request)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('student_form.html')


@app.route('/tutors')
def tutors():
    tutor_infos = TutorInfo.query.all()
    return render_template('tutors.html', tutors=tutor_infos)


@app.route('/students')
def students():
    student_requests = StudentRequest.query.all()
    return render_template('students.html', students=student_requests)


@app.route('/tutor/<int:tutor_id>')
def tutor_detail(tutor_id):
    tutor = TutorInfo.query.get_or_404(tutor_id)
    reviews = Review.query.filter_by(tutor_id=tutor_id).all()
    return render_template('tutor_detail.html', tutor=tutor, reviews=reviews)


@app.route('/matching')
def matching():
    if not g.user:
        return redirect(url_for('login'))
    student_requests = StudentRequest.query.filter_by(user_id=g.user.id).all()
    matched_tutors = []
    for student_request in student_requests:
        tutors = TutorInfo.query.filter_by(subject=student_request.subject, grade=student_request.grade).all()
        matched_tutors.extend(tutors)
    return render_template('matching.html', matches=matched_tutors)


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


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        password = request.form['password']
        if password == 'renqianhao':
            session['admin'] = True
            return redirect(url_for('admin_panel'))
        else:
            flash("密码错误")
            return redirect(url_for('admin'))
    return render_template('admin.html')


@app.route('/admin/panel')
def admin_panel():
    if 'admin' not in session:
        return redirect(url_for('admin'))
    users = User.query.all()
    tutors = TutorInfo.query.all()
    students = StudentRequest.query.all()
    reviews = Review.query.all()
    return render_template('admin_panel.html', users=users, tutors=tutors, students=students, reviews=reviews)


@app.route('/admin/delete/<string:entity>/<int:id>')
def delete_entity(entity, id):
    if 'admin' not in session:
        return redirect(url_for('admin'))
    if entity == 'user':
        obj = User.query.get_or_404(id)
    elif entity == 'tutor':
        obj = TutorInfo.query.get_or_404(id)
    elif entity == 'student':
        obj = StudentRequest.query.get_or_404(id)
    elif entity == 'review':
        obj = Review.query.get_or_404(id)
    else:
        flash("无效的实体")
        return redirect(url_for('admin_panel'))

    db.session.delete(obj)
    db.session.commit()
    flash(f"{entity} 已被删除")
    return redirect(url_for('admin_panel'))


if __name__ == '__main__':
    app.run(debug=True)
