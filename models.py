from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Time = db.Column(db.String(50), nullable=False)
    Lesson = db.Column(db.String(100), nullable=False)
    Teacher = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Schedule {self.Lesson} by {self.Teacher} at {self.Time}>'

class Teachers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Teacher = db.Column(db.String(50), nullable=False)
    Lesson = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Teachers {self.Teacher} by {self.Lesson}>'

class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(255), nullable=True)  # Поле для изображения
    pub_date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<News {self.title}>'