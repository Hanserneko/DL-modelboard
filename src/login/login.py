import flask as fk
import pymysql as sq
from flask import Blueprint

from src.DB import get_db

login_bp = Blueprint('login', __name__)

@login_bp.route('/login', methods=['POST'])
def login():
    req = fk.request.get_json()
    username = req.get('username')
    password = req.get('password')
    if not username or not password:
        return fk.jsonify({'success': False, 'msg': '缺少参数'}), 400
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute('SELECT id FROM users WHERE username=%s AND password=%s', (username, password))
        user = cursor.fetchone()
        if user:
            return fk.jsonify({'success': True, 'msg': '登录成功', 'username': username})
        else:
            return fk.jsonify({'success': False, 'msg': '用户名或密码错误'}), 401
    except Exception as e:
        return fk.jsonify({'success': False, 'msg': str(e)}), 500
    finally:
        cursor.close()
        db.close()
