import flask as fk
import pymysql as sq
from flask import Blueprint
from get_db import get_db
from hashlib import sha256

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
        cursor.execute('SELECT id FROM users WHERE username=%s', (username, ))
        user = cursor.fetchone()
        if not user:
            return fk.jsonify({'success': False, 'msg': '用户不存在'}), 404
        user_id = user[0]
        cursor.execute('SELECT password FROM passwd WHERE user_id=%s',
                       (user_id, ))
        pw_row = cursor.fetchone()
        if pw_row and pw_row[0] == sha256(password.encode()).hexdigest():
            return fk.jsonify({
                'success': True,
                'msg': '登录成功',
                'username': username
            })
        else:
            return fk.jsonify({'success': False, 'msg': '密码错误'}), 401
    except Exception as e:
        return fk.jsonify({'success': False, 'msg': str(e)}), 500
    finally:
        cursor.close()
        db.close()
