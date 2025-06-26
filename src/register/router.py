import flask as fk
import pymysql as sq
from flask import Blueprint
from get_db import get_db

from hashlib import sha256

register_bp = Blueprint('register', __name__)


@register_bp.route('/register', methods=['POST'])
def register():
    req = fk.request.get_json()
    username = req.get('username')
    password = req.get('password')
    email = req.get('email')
    if not username or not password or not email:
        return fk.jsonify({'success': False, 'msg': '缺少参数'}), 400
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute('SELECT id FROM users WHERE username=%s OR email=%s',
                       (username, email))
        if cursor.fetchone():
            return fk.jsonify({'success': False, 'msg': '用户名或邮箱已存在'}), 409
        cursor.execute('INSERT INTO users (username, email) VALUES (%s, %s)',
                       (username, email))
        user_id = cursor.lastrowid
        cursor.execute(
            'INSERT INTO passwd (user_id, password) VALUES (%s, %s)',
            (user_id, sha256(password.encode()).hexdigest()))
        db.commit()
        return fk.jsonify({
            'success': True,
            'msg': '注册成功',
            'username': username
        }), 201
    except Exception as e:
        db.rollback()
        return fk.jsonify({'success': False, 'msg': str(e)}), 500
    finally:
        cursor.close()
        db.close()
