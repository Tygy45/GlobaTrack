from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import os
import uuid
from datetime import datetime

app = Flask(__name__)

# Настройка базы данных (SQLite)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///markers.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Секретный ключ для работы с сессиями
app.secret_key = 'your_secret_key_here'

# Модель для таблицы пользователей
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Модель для таблицы сессий (маршрутов)
class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    route_name = db.Column(db.String(200), nullable=True)
    route_length = db.Column(db.Float, nullable=True)
    use_roads = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Модель для таблицы меток
class Marker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    session_id = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Создаем таблицы в базе данных
with app.app_context():
    db.create_all()

# Маршрут по умолчанию: перенаправление на страницу регистрации
@app.route('/')
def home():
    return redirect(url_for('registration'))

# Маршрут для главной страницы (index.html)
@app.route('/index')
def index():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    # Получаем все сессии пользователя
    user_sessions = Session.query.filter_by(user_id=user_id).all()
    return render_template('index.html', sessions=user_sessions)

# Маршрут для профиля
@app.route('/profile')
def profile():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    # Получаем все сессии пользователя
    user_sessions = Session.query.filter_by(user_id=user_id).all()
    return render_template('profile.html', sessions=user_sessions)

# Маршрут для загрузки меток
@app.route('/load-markers/<session_id>', methods=['GET'])
def load_markers(session_id):
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({"error": "Пользователь не авторизован."}), 401

        # Проверяем, что сессия принадлежит текущему пользователю
        session_record = Session.query.filter_by(session_id=session_id, user_id=user_id).first()
        if not session_record:
            return jsonify({"error": "Сессия не найдена или доступ запрещен."}), 404

        # Получаем все метки для указанной сессии
        markers = Marker.query.filter_by(session_id=session_id, user_id=user_id).all()

        # Формируем данные для ответа
        markers_data = [{
            "name": marker.name,
            "coords": [marker.latitude, marker.longitude]
        } for marker in markers]

        return jsonify({
            "markers": markers_data,
            "routeName": session_record.route_name,
            "routeLength": session_record.route_length,
            "useRoads": session_record.use_roads
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Маршрут для удаления сохранённого маршрута
@app.route('/delete-session/<session_id>', methods=['POST'])
def delete_session(session_id):
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({"error": "Пользователь не авторизован."}), 401

        session_record = Session.query.filter_by(session_id=session_id, user_id=user_id).first()
        if not session_record:
            return jsonify({"error": "Сессия не найдена или доступ запрещен."}), 404

        # Удаляем все метки маршрута
        Marker.query.filter_by(session_id=session_id, user_id=user_id).delete()
        # Удаляем запись о сессии
        db.session.delete(session_record)
        db.session.commit()

        return jsonify({"message": "Маршрут успешно удалён."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# Маршрут для поддержки
@app.route('/support')
def support():
    return render_template('support.html')

# Маршрут для регистрации
@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        password2 = request.form.get('password2')

        # Проверка заполнения обязательных полей
        if not username or not email or not password or not password2:
            return jsonify({"error": "Пожалуйста, заполните все обязательные поля."}), 400

        # Проверка совпадения паролей
        if password != password2:
            return jsonify({"error": "Пароли не совпадают."}), 400

        # Проверка, существует ли пользователь с таким email
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({"error": "Пользователь с таким email уже существует."}), 400

        # Создание нового пользователя
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        # Перенаправление на главную страницу
        return redirect(url_for('index'))

    return render_template('registration.html')

# Маршрут для входа
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Проверка, существует ли пользователь с таким email и паролем
        user = User.query.filter_by(email=email, password=password).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('index'))
        else:
            return jsonify({"error": "Неверный email или пароль."}), 401

    return render_template('login.html')

# Маршрут для сохранения меток
@app.route('/save-markers', methods=['POST'])
def save_markers():
    try:
        data = request.json  # Получаем данные из запроса
        user_id = session.get('user_id')

        if not user_id:
            return jsonify({"error": "Пользователь не авторизован."}), 401

        # Генерируем новый session_id
        session_id = str(uuid.uuid4())

        # Получаем дополнительные данные о маршруте
        route_name = data.get('routeName', 'Без названия')
        route_length = data.get('routeLength', 0)
        use_roads = data.get('useRoads', False)
        markers = data.get('markers', [])

        # Сохраняем новую сессию в базе данных
        new_session = Session(
            session_id=session_id, 
            user_id=user_id,
            route_name=route_name,
            route_length=route_length,
            use_roads=use_roads
        )
        db.session.add(new_session)

        # Сохраняем метки в базу данных
        for marker in markers:
            new_marker = Marker(
                name=marker['name'],
                latitude=marker['coords'][0],
                longitude=marker['coords'][1],
                session_id=session_id,
                user_id=user_id
            )
            db.session.add(new_marker)

        db.session.commit()
        return jsonify({"message": "Метки успешно сохранены!", "sessionId": session_id}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=2000)