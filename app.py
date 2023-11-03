from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
from flask import flash, get_flashed_messages
from model import db, User, Area, Sensor, SensorData
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import CSRFProtect
from flask_wtf import FlaskForm
from wtforms import ValidationError,StringField, PasswordField, SubmitField, BooleanField, IntegerField
from wtforms.validators import DataRequired
from sqlalchemy.orm import joinedload
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from sqlalchemy.orm import subqueryload



app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
csrf = CSRFProtect(app)


class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    is_admin = BooleanField('Admin')
    areas = QuerySelectMultipleField('Areas', query_factory=lambda: Area.query.all(), get_label="name")
    submit = SubmitField('Submit')


class AreaForm(FlaskForm):
    name = StringField('Area Name', validators=[DataRequired()])
    submit = SubmitField('Submit')

class SensorForm(FlaskForm):
    identifier = StringField('Sensor Identifier', validators=[DataRequired()])
    area = QuerySelectField('Area', query_factory=lambda: Area.query.all(), get_label="name")
    submit = SubmitField('Submit')

class DeleteForm(FlaskForm):
    pass

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        print(request.method)

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['is_admin'] = user.is_admin
            return redirect(url_for('dashboard'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('is_admin', None)
    return redirect(url_for('login'))

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('You need to login first.')
        return redirect(url_for('login'))
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if user is None:
        flash('User not found.')
        return redirect(url_for('login'))

    # Prepare a dictionary to hold area and sensor data
    areas_and_sensors = {}
    for area in user.areas:
        areas_and_sensors[area.name] = [sensor.identifier for sensor in area.sensors.all()]

    return render_template('profile.html', user=user, areas_and_sensors=areas_and_sensors)





from sqlalchemy.orm import subqueryload


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.options(subqueryload('areas'), subqueryload('sensors')).get(session['user_id'])
    return render_template('dashboard.html', user=user)


@app.route('/admin/add_user', methods=['GET', 'POST'])
def add_user():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('login'))
    form = UserForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, is_admin=form.is_admin.data)
        user.set_password(form.password.data)
        user.areas = form.areas.data
        db.session.add(user)
        db.session.commit()
        flash('User added successfully!')
        return redirect(url_for('view_users'))
    return render_template('add_user.html', form=form)

@app.route('/admin/add_area', methods=['GET', 'POST'])
def add_area():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('login'))
    form = AreaForm()
    if form.validate_on_submit():
        area = Area(name=form.name.data)
        db.session.add(area)
        db.session.commit()
        flash('Area added successfully!')
        return redirect(url_for('view_areas'))

    return render_template('add_area.html', form=form)

@app.route('/admin/add_sensor', methods=['GET', 'POST'])
def add_sensor():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('login'))
    form = SensorForm()
    if form.validate_on_submit():
        sensor = Sensor(identifier=form.identifier.data, area_id=form.area.data.id)
        db.session.add(sensor)
        db.session.commit()
        flash('Sensor added successfully!')
        return redirect(url_for('view_sensors'))

    return render_template('add_sensor.html', form=form)

@csrf.exempt
@app.route('/api/sensor_data', methods=['POST'])
def sensor_data():
    data = request.json
    sensor = Sensor.query.filter_by(identifier=data['identifier']).first()
    if not sensor:
        return jsonify({'error': 'Invalid sensor identifier'}), 400
    new_data = SensorData(value=data['value'], sensor=sensor)
    db.session.add(new_data)
    db.session.commit()
    return jsonify({'message': 'Data added successfully'}), 201


@app.route('/admin/view_users')
def view_users():
    users = User.query.all()
    return render_template('view_users.html', users=users)

@app.route('/admin/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = UserForm(obj=user)
    areas = Area.query.all()
    form.areas.choices = [(str(area.id), area.name) for area in areas]
    if form.validate_on_submit():
        user.username = form.username.data
        if form.password.data:
            user.set_password(form.password.data)
        user.is_admin = form.is_admin.data
        user.areas = form.areas.data  # Assign the list of Area objects directly
        db.session.commit()
        flash('User updated successfully!')
        return redirect(url_for('view_users'))
    return render_template('edit_user.html', form=form, user=user)


@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    form = DeleteForm()
    if form.validate_on_submit():
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully!')
        return redirect(url_for('view_users'))
    return render_template('delete_user.html', form=form)


@app.route('/admin/view_areas')
def view_areas():
    areas = Area.query.all()
    return render_template('view_areas.html', areas=areas)

@app.route('/admin/edit_area/<int:area_id>', methods=['GET', 'POST'])
def edit_area(area_id):
    area = Area.query.get_or_404(area_id)
    form = AreaForm(obj=area)
    if form.validate_on_submit():
        area.name = form.name.data
        db.session.commit()
        flash('Area updated successfully!')
        return redirect(url_for('view_areas'))
    return render_template('edit_area.html', form=form, area=area)


@app.route('/admin/delete_area/<int:area_id>', methods=['POST'])
def delete_area(area_id):
    area = Area.query.get_or_404(area_id)
    db.session.delete(area)
    db.session.commit()
    flash('Area deleted successfully!')
    return redirect(url_for('view_areas'))

@app.route('/admin/view_sensors')
def view_sensors():
    sensors = Sensor.query.all()
    return render_template('view_sensors.html', sensors=sensors)

@app.route('/admin/edit_sensor/<int:sensor_id>', methods=['GET', 'POST'])
def edit_sensor(sensor_id):
    sensor = Sensor.query.get_or_404(sensor_id)
    form = SensorForm(obj=sensor)
    if form.validate_on_submit():
        sensor.identifier = form.identifier.data
        db.session.commit()
        flash('Sensor updated successfully!')
        return redirect(url_for('view_sensors'))
    return render_template('edit_sensor.html', form=form)

@app.route('/admin/delete_sensor/<int:sensor_id>', methods=['POST'])
def delete_sensor(sensor_id):
    sensor = Sensor.query.get_or_404(sensor_id)
    db.session.delete(sensor)
    db.session.commit()
    flash('Sensor deleted successfully!')
    return redirect(url_for('view_sensors'))


from datetime import datetime

@app.route('/api/sensor_data_for_area/<int:area_id>', methods=['GET'])
def sensor_data_for_area(area_id):
    # Ensure the user is logged in
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    # Ensure the user has access to the specified area
    user = User.query.get(session['user_id'])
    
    if not any(area.id == area_id for area in user.areas):
        return jsonify({'error': 'Forbidden'}), 403

    # Fetch the sensor data for the given area
    sensors_in_area = Sensor.query.filter_by(area_id=area_id).all()

    sensor_data_list = []

    for sensor in sensors_in_area:
        sensor_data = SensorData.query.filter_by(sensor_id=sensor.id).order_by(SensorData.timestamp).all()
        timestamps = [data.timestamp.strftime('%Y-%m-%d %H:%M:%S') for data in sensor_data]
        values = [data.value for data in sensor_data]
        sensor_data_list.append({
            'sensor_identifier': sensor.identifier,
            'timestamps': timestamps,
            'values': values
        })
    print(sensor_data_list)

    return jsonify(sensor_data_list)


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()  # Rollback the session in case of database errors
    return render_template('500.html'), 500





if __name__ == '__main__':
    app.run(host='0.0.0.0',port=80)
