from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import subqueryload
from datetime import datetime
db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    areas = db.relationship('Area', backref='user', lazy='select')
    sensors = db.relationship('Sensor', backref='user', lazy='select')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Area(db.Model):
    __tablename__ = 'areas'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    sensors = db.relationship('Sensor', backref='area', lazy='dynamic')

class Sensor(db.Model):
    __tablename__ = 'sensors'

    id = db.Column(db.Integer, primary_key=True)
    identifier = db.Column(db.String(64), unique=True)
    area_id = db.Column(db.Integer, db.ForeignKey('areas.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    data = db.relationship('SensorData', backref='sensor', lazy='dynamic')

class SensorData(db.Model):
    __tablename__ = 'sensor_readings'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    value = db.Column(db.Float)
    sensor_id = db.Column(db.Integer, db.ForeignKey('sensors.id'))
