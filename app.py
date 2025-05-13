from flask import Flask, render_template, request, flash, redirect, url_for
from flask_admin import Admin, AdminIndexView, expose
from werkzeug.utils import secure_filename
from models import db, Schedule, News, Teachers
from ipaddress import ip_address

from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///schedule.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.secret_key = 'TLL0515kTKMMGKTtatTawoOOOOwatwat121444kr123456789'

db.init_app(app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

with app.app_context():
    db.create_all()  # Создание таблиц

def is_local_request():
    """Проверяет, является ли запрос локальным (с localhost/127.0.0.1)."""
    try:
        # Проверяем request.remote_addr, который содержит IP-адрес клиента.
        # request.remote_addr может быть None, если сервер не может определить IP-адрес.
        if request.remote_addr:
            client_ip = ip_address(request.remote_addr)
            return client_ip.is_loopback
        else:
            return False
    except ValueError:
        return False

class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        # Здесь можно добавить любую логику, которую вы хотите
        return self.render('admin/index.html')

admin = Admin(app, index_view=MyAdminIndexView(), name='Админ Панель(127.0.0.1)', template_mode='bootstrap3')

@app.route('/', methods=['GET', 'POST'])
def index():
    news = News.query.order_by(News.pub_date.desc()).all()
    for item in news:
        item.image_filename = os.path.basename(item.image)
    if request.method == 'POST':
        return render_template('index.html', success=True, news=news) # Передаем флаг об успехе
    return render_template('index.html', news=news)

@app.route('/teachers')
def teachers():
    teachers = Teachers.query.all()
    return render_template('teachers.html', teachers=teachers)

@app.route('/schedule')
def schedule():
    schedules = Schedule.query.all() # Получение всех записей расписания
    return render_template('schedule.html', schedules=schedules)

@app.route('/admin/add_news', methods=['GET', 'POST'])
def admin_add_news():
    if not is_local_request():
        flash('Доступ запрещен. Пожалуйста, используйте локальный адрес.', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        # Обработка изображения
        if 'image' not in request.files:
            flash('Нет файла изображения', 'error')
            return render_template('admin/admin_add_news.html')  # Возвращаем шаблон с ошибкой

        file = request.files['image']
        if file.filename == '':
            flash('Файл не выбран', 'error')
            return render_template('admin/admin_add_news.html')  # Возвращаем шаблон с ошибкой

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Уникальное имя файла, чтобы избежать перезаписи
            filename = datetime.now().strftime("%Y%m%d%H%M%S_") + filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # Сохраняем только имя файла
            new_news = News(title=title, content=content, image=filename)
            db.session.add(new_news)
            db.session.commit()
            return redirect(url_for('index'))
        else:
            flash('Недопустимый формат файла', 'error')
            return render_template('admin/admin_add_news.html')

    return render_template('admin/admin_add_news.html')

@app.route('/act')
def act():
    return render_template('act.html')

# Редактировать Расписание
@app.route('/admin/schedule', methods=['GET', 'POST'])
def admin_schedule():
    if not is_local_request():
        flash('Доступ запрещен. Пожалуйста, используйте локальный адрес.', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        new_schedule = Schedule(
            Time=request.form['time'],
            Lesson=request.form['subject'],
            Teacher=request.form['teacher']
        )
        db.session.add(new_schedule)
        db.session.commit()
        return redirect(url_for('admin_schedule'))

    schedules = Schedule.query.all()
    return render_template('admin/schedule.html', schedules=schedules)

@app.route('/admin/schedule/edit/<int:id>', methods=['GET', 'POST'])
def edit_schedule(id):
    if not is_local_request():
        flash('Доступ запрещен. Пожалуйста, используйте локальный адрес.', 'error')
        return redirect(url_for('index'))

    schedule = Schedule.query.get(id)
    if request.method == 'POST':
        schedule.Time = request.form['time']
        schedule.Lesson = request.form['subject']
        schedule.Teacher = request.form['teacher']
        db.session.commit()
        return redirect(url_for('admin_schedule'))

    return render_template('admin/edit_schedule.html', schedule=schedule)

@app.route('/admin/schedule/delete/<int:id>', methods=['POST'])
def delete_schedule(id):
    if not is_local_request():
        flash('Доступ запрещен. Пожалуйста, используйте локальный адрес.', 'error')
        return redirect(url_for('index'))

    schedule = Schedule.query.get(id)
    db.session.delete(schedule)
    db.session.commit()
    return redirect(url_for('admin_schedule'))

# Редактировать Учителей
@app.route('/admin/teachers', methods=['GET', 'POST'])
def admin_teachers():
    if not is_local_request():
        flash('Доступ запрещен. Пожалуйста, используйте локальный адрес.', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        new_teachers = Teachers(
            Teacher=request.form['teacher'],
            Lesson=request.form['lesson'],
        )
        db.session.add(new_teachers)
        db.session.commit()
        return redirect(url_for('admin_teachers'))

    teachers = Teachers.query.all()
    return render_template('admin/teachers.html', teachers=teachers)

@app.route('/admin/teachers/edit/<int:id>', methods=['GET', 'POST'])
def edit_teachers(id):
    if not is_local_request():
        flash('Доступ запрещен. Пожалуйста, используйте локальный адрес.', 'error')
        return redirect(url_for('index'))

    teachers = Teachers.query.get(id)
    if request.method == 'POST':
        teachers.Teacher = request.form['teacher']
        teachers.Lesson = request.form['lesson']
        db.session.commit()
        return redirect(url_for('admin_teachers'))

    return render_template('admin/edit_teachers.html', teachers=teachers)

@app.route('/admin/teachers/delete/<int:id>', methods=['POST'])
def delete_teachers(id):
    if not is_local_request():
        flash('Доступ запрещен. Пожалуйста, используйте локальный адрес.', 'error')
        return redirect(url_for('index'))

    teachers = Teachers.query.get(id)
    db.session.delete(teachers)
    db.session.commit()
    return redirect(url_for('admin_teachers'))

# Подтверждение Заявки
@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']

        print(f"Получены данные: Имя - {name}, Email - {email}, Телефон - {phone}")

        return render_template('index.html', success=True)

    return render_template('index.html')  # Если метод GET, возвращаем обычную форму

@app.errorhandler(403)
def forbidden(e):
    return "Доступ к админ-панели запрещен.", 403


if __name__ == '__main__':
    app.run(debug=True) # host="0.0.0.0"
