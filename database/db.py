import os.path
import sqlite3
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UserDatabase:
    """Класс таблицы Юзеров в базе данных"""
    def __init__(self, db_name='database/users.db'):
        self.db_name = os.path.abspath(db_name)
        self.create_table()

    def create_table(self):
        """Создает таблицы пользователей и предсказаний, если они не существуют."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL UNIQUE,
                    birth_date TEXT NOT NULL
                )
                '''
            )
            cursor.execute(
                '''
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    image_path TEXT NOT NULL,
                    prediction_date TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
                '''
            )
            conn.commit()

    def add_user(self, user_id, birth_date):
        """Добавляет нового пользователя в базу данных."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO users (user_id, birth_date) VALUES (?, ?)
                ''', (user_id, birth_date))
                conn.commit()
            except sqlite3.IntegrityError:
                logger.warning(f"Пользователь с user_id {user_id} уже существует.")

    def get_user(self, user_id):
        """Получает информацию о пользователе по его user_id."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM users WHERE user_id = ?
            ''', (user_id,))
            user = cursor.fetchone()
            return user

    def get_user_count(self):
        """Получает количество пользователей в базе данных."""
        with sqlite3.connect(self.db_name, timeout=5) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(DISTINCT user_id) FROM users')
            count = cursor.fetchone()
        logger.info(f"Количество пользователей в базе данных: {count}")
        return count[0] if count else 0

    def update_last_prediction(self, user_id, image_path):
        """Обновляем путь к последнему предсказанию и дату."""
        prediction_date = datetime.now().date().isoformat()
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            # Проверяем, существует ли уже предсказание для пользователя на сегодня
            cursor.execute('''
                SELECT * FROM predictions WHERE user_id = ? AND prediction_date = ?
            ''', (user_id, prediction_date))
            existing_prediction = cursor.fetchone()

            if existing_prediction:
                # Если предсказание уже существует, обновляем его
                cursor.execute('''
                    UPDATE predictions SET image_path = ? WHERE user_id = ? AND prediction_date = ?
                ''', (image_path, user_id, prediction_date))
            else:
                # Если предсказания нет, добавляем новое
                cursor.execute('''
                    INSERT INTO predictions (user_id, image_path, prediction_date) VALUES (?, ?, ?)
                ''', (user_id, image_path, prediction_date))
            conn.commit()

    def get_last_prediction(self, user_id):
        """Получаем последнее предсказание и дату."""
        today = datetime.now().date().isoformat()
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT image_path, prediction_date FROM predictions WHERE user_id = ? AND prediction_date = ?
            ''', (user_id, today))
            last_prediction = cursor.fetchone()
            return last_prediction  # Возвращает кортеж (image_path, prediction_date) или None
