import os
from PIL import Image

from flask import Flask, render_template, request, redirect, url_for, session, g, flash
from werkzeug.utils import secure_filename

from models import db, User, TutorInfo, StudentRequest, Review
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tutoring_service.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/users'


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


# ---------------------------------------------------注册-----------------------------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        phoneNumber = request.form['phoneNumber']
        role = request.form['role']

        if password != confirm_password:
            flash("两次输入的密码不一致，请重新输入")
            return redirect(url_for('register'))

        if len(phoneNumber) != 11:
            flash("请输入正确的电话号码")
            return redirect(url_for('register'))

        # 其他注册逻辑，例如检查用户名是否已存在、保存用户到数据库等
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("用户名已存在，请选择另一个用户名")
            return redirect(url_for('register'))

        new_user = User(username=username, password=password, role=role, phoneNumber=phoneNumber)
        db.session.add(new_user)
        db.session.commit()
        flash("注册成功，请登录")
        if role == "tutor":
            return redirect(url_for('login_tutor'))
        else:
            return redirect(url_for('login_student'))

    return render_template('register.html')


# ---------------------------------------------------登录-----------------------------------------------

@app.route('/login_student', methods=['GET', 'POST'])
def login_student():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            if user.role == "student":
                session['user_id'] = user.id
                return redirect(url_for('student_home'))
            else:
                flash("用户名或密码错误，请重新输入")
                return redirect(url_for('login_student'))
        else:
            flash("用户名或密码错误，请重新输入")
            return redirect(url_for('login_student'))
    return render_template('login_student.html')


@app.route('/student_home')
def student_home():
    if not g.user:
        return redirect(url_for('student_login'))
    return render_template('student_home.html')


@app.route('/login_tutor', methods=['GET', 'POST'])
def login_tutor():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            if user.role == "tutor":
                session['user_id'] = user.id
                return redirect(url_for('tutor_home'))
            else:
                flash("用户名或密码错误，请重新输入")
                return redirect(url_for('login_tutor'))
        else:
            flash("用户名或密码错误，请重新输入")
            return redirect(url_for('login_tutor'))
    return render_template('login_tutor.html')


@app.route('/tutor_home')
def tutor_home():
    if not g.user:
        return redirect(url_for('tutor_login'))
    return render_template('tutor_home.html')


# ---------------------------------------------------家教操作--------------------------------------------------
# -------------------------1查看、编辑个人中心-------------------------
@app.route('/tutor_profile/<int:user_id>')
def tutor_profile(user_id):
    user = User.query.get(user_id)
    reviews = Review.query.filter_by(tutor_id=user_id).all()
    return render_template('tutor_profile.html', user=user, visitor=g.user, reviews=reviews)


@app.route('/student_profile/<int:user_id>')
def student_profile(user_id):
    user = User.query.get(user_id)
    return render_template('student_profile.html', user=user, visitor=g.user)


@app.route('/tutor_profile/<int:user_id>/edit', methods=['GET', 'POST'])
def edit_tutor_profile(user_id):
    user = User.query.get(user_id)
    if request.method == 'POST':
        user.username = request.form['username']
        user.phoneNumber = request.form['phoneNumber']
        user.location = request.form['location']
        if 'photo' in request.files:
            photo = request.files['photo']
            if photo.filename != '':
                filename = f"{user.id}.png"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                photo.save(file_path)
                with Image.open(file_path) as img:
                    # 设置缩放的宽度和高度
                    max_width = 150
                    max_height = 200
                    # 缩放图片，保持宽高比
                    img.thumbnail((max_width, max_height))
                    # 保存缩放后的图片
                    img.save(file_path)

                user.photo = filename
        db.session.commit()
        flash('信息已更新')
        return redirect(url_for('tutor_profile', user_id=user.id))
    return render_template('edit_tutor_profile.html', user=user)


@app.route('/student_profile/<int:user_id>/edit', methods=['GET', 'POST'])
def edit_student_profile(user_id):
    user = User.query.get(user_id)
    if request.method == 'POST':
        user.username = request.form['username']
        user.phoneNumber = request.form['phoneNumber']
        user.location = request.form['location']
        if 'photo' in request.files:
            photo = request.files['photo']
            if photo.filename != '':
                filename = f"{user.id}.png"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                photo.save(file_path)
                with Image.open(file_path) as img:
                    # 设置缩放的宽度和高度
                    max_width = 150
                    max_height = 200
                    # 缩放图片，保持宽高比
                    img.thumbnail((max_width, max_height))
                    # 保存缩放后的图片
                    img.save(file_path)
                user.photo = filename
        db.session.commit()
        flash('信息已更新')
        return redirect(url_for('student_profile', user_id=user.id))
    return render_template('edit_student_profile.html', user=user)
# -------------------------2发布家教信息-------------------------
@app.route('/tutor-form', methods=['GET', 'POST'])
def tutor_form():
    if not g.user:
        return redirect(url_for('login'))
    if request.method == 'POST':
        user_id = session.get('user_id')
        user = User.query.get(user_id)
        tutor_info = TutorInfo(
            user_id=g.user.id,
            name=g.user.username,
            subject=request.form['subject'],
            grade=request.form['grade'],
            time=request.form['time'],
            rate=request.form['rate'],
            phoneNumber=user.phoneNumber,
            information=request.form['information']
        )
        db.session.add(tutor_info)
        db.session.commit()
        return redirect(url_for('tutors'))
    return render_template('tutor_form.html')
# -------------------------3查看家教信息-------------------------
# -----------------------4管理我的家教信息------------------------
# -------------------------5查看学生需求-------------------------
# -------------------------6查看系统推荐-------------------------
# -------------------------7查看我的评价-------------------------
# ---------------------------8回到首页--------------------------完成


# ---------------------------------------------------学生操作--------------------------------------------------
# ---------------------------------对家教进行评价--------------------------------
@app.route('/review', methods=['GET', 'POST'])
def review():
    if not g.user:
        return redirect(url_for('login'))
    if request.method == 'POST':
        tutor_name = request.form['tutor_name']
        tutor = User.query.filter_by(username=tutor_name).first()
        if tutor:
            review = Review(
                tutor_id=tutor.id,
                user_id=g.user.id,
                username=g.user.username,
                review=request.form['review']
            )
            db.session.add(review)
            db.session.commit()
            return redirect(url_for('tutor_profile', user_id=tutor.id))
        else:
            return "家教不存在"
    return render_template('review.html')
# ---------------------------------------------------发布家教内容-----------------------------------------------

# ---------------------------------------------------发布学生需求-----------------------------------------------

@app.route('/student-form', methods=['GET', 'POST'])
def student_form():
    if not g.user:
        return redirect(url_for('login'))
    if request.method == 'POST':
        user_id = session.get('user_id')
        user = User.query.get(user_id)
        student_request = StudentRequest(
            user_id = user_id,
            name=g.user.username,
            subject = request.form['subject'],
            grade = request.form['grade'],
            time = request.form['time'],
            budget = request.form['budget'],
            phoneNumber = user.phoneNumber,
            information = request.form['information']

        )
        db.session.add(student_request)
        db.session.commit()
        return redirect(url_for('students'))
    return render_template('student_form.html')


# ---------------------------------------------------查看家教信息-----------------------------------------------

@app.route('/tutors')
def tutors():
    tutor_infos = TutorInfo.query.all()
    return render_template('tutors.html', tutors=tutor_infos, user=g.user)


# ---------------------------------------------------查看学生需求-----------------------------------------------

@app.route('/students')
def students():
    student_requests = StudentRequest.query.all()
    return render_template('students.html', students=student_requests, user=g.user)


# ---------------------------------------------------查看家教信息-----------------------------------------------



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


# ----------------------------------------------------管理员操作-------------------------------------------

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        password = request.form['password']
        if password == 'pengjielun':
            session['admin'] = True
            return redirect(url_for('admin_home'))
        else:
            flash("密码错误")
            return redirect(url_for('admin'))
    return render_template('admin.html')


@app.route('/admin/home')
def admin_home():
    if 'admin' not in session:
        return redirect(url_for('admin'))
    # users = User.query.all()
    # tutors = TutorInfo.query.all()
    # students = StudentRequest.query.all()
    # reviews = Review.query.all()
    return render_template('admin_home.html')


@app.route('/admin_users')
def admin_users():
    if 'admin' not in session:
        return redirect(url_for('admin'))
    users = User.query.all()
    return render_template('admin_users.html', users=users)


@app.route('/admin_tutors')
def admin_tutors():
    if 'admin' not in session:
        return redirect(url_for('admin'))
    tutors = TutorInfo.query.all()
    return render_template('admin_tutors.html', tutors=tutors)


@app.route('/admin_students')
def admin_students():
    if 'admin' not in session:
        return redirect(url_for('admin'))
    students = StudentRequest.query.all()
    return render_template('admin_students.html', students=students)


@app.route('/admin_reviews')
def admin_reviews():
    if 'admin' not in session:
        return redirect(url_for('admin'))
    reviews = Review.query.all()
    return render_template('admin_reviews.html', reviews=reviews)


@app.route('/admin/delete/<string:entity>/<int:id>')
def delete_entity(entity, id):
    if 'admin' not in session:
        return redirect(url_for('admin'))

    if entity == 'user':
        user = User.query.get_or_404(id)

        # 删除用户对应的照片文件
        if user.photo:
            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], user.photo)
            if os.path.exists(photo_path):
                os.remove(photo_path)

        # 删除与该用户相关的评价（包括该用户发送和接收的评价）
        Review.query.filter((Review.user_id == user.id) | (Review.tutor_id == user.id)).delete()

        # 如果用户是学生，删除该学生发布的学生需求
        if user.role == 'student':
            StudentRequest.query.filter_by(user_id=user.id).delete()

        # 如果用户是家教，删除该家教发布的家教信息
        if user.role == 'tutor':
            TutorInfo.query.filter_by(user_id=user.id).delete()

        db.session.delete(user)
        db.session.commit()
        flash("已成功将用户信息从系统中删除!")
        return redirect(url_for('admin_users'))

    elif entity == 'tutor':
        tutor_info = TutorInfo.query.get_or_404(id)
        db.session.delete(tutor_info)
        db.session.commit()
        flash("已成功将一条家教发布信息从系统中删除!")
        return redirect(url_for('admin_tutors'))

    elif entity == 'student':
        student_request = StudentRequest.query.get_or_404(id)
        db.session.delete(student_request)
        db.session.commit()
        flash("已成功将一条学生需求信息从系统中删除!")
        return redirect(url_for('admin_students'))

    elif entity == 'review':
        review = Review.query.get_or_404(id)
        db.session.delete(review)
        db.session.commit()
        flash("已成功将一条评价信息从系统中删除!")
        return redirect(url_for('admin_reviews'))

    else:
        flash("无效的实体")
        return redirect(url_for('admin_home'))


# ------------------------个人主页-------------------------------


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
