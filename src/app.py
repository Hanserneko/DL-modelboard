import pymysql as sq
import flask as fk
from flask_cors import CORS
from get_db import get_db
import asyncio
import os
from werkzeug.utils import secure_filename
import datetime
import json
import zipfile
import shutil

app = fk.Flask(__name__)
CORS(app)

from login.router import login_bp
from register.router import register_bp

app.register_blueprint(login_bp)
app.register_blueprint(register_bp)

MODEL_FOLDER = os.path.join(os.path.dirname(__file__), '../data/models')
DATASET_FOLDER = os.path.join(os.path.dirname(__file__), '../data/datasets')
ALLOWED_EXTENSIONS = {'zip'}


def unzip_file(zip_path, extract_to):
    """解压缩zip文件到指定目录 目录不存在则创建"""
    os.makedirs(extract_to, exist_ok=True)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)


def allowed_file(filename):
    return '.' in filename and filename.rsplit(
        '.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/test', methods=['GET'])
def test():
    return fk.jsonify({'msg': '测试成功'}), 200


@app.route('/api/models', methods=['GET'])
def get_models():

    def safe_json_loads(val):
        if not val:
            return []
        try:
            return json.loads(val)
        except Exception:
            return [
                v.strip().strip("'\"") for v in val.split(',') if v.strip()
            ]

    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            'SELECT m.id, m.name, m.tags, m.requirement_tag, m.uploaded_at, u.username, m.path, m.`desc` FROM models m LEFT JOIN users u ON m.user_id = u.id'
        )
        rows = cursor.fetchall()
        result = []
        for row in rows:
            result.append({
                'id': row[0],
                'name': row[1],
                'tags': safe_json_loads(row[2]),
                'needs': safe_json_loads(row[3]),
                'date': row[4].strftime('%Y-%m-%d'),
                'uploader': row[5] or '',
                'file': row[6],
                'desc': row[7] or ''
            })
        return fk.jsonify({'data': result, 'total': len(result)})
    except Exception as e:
        return fk.jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()  # type: ignore
        db.close()  # type: ignore


@app.route('/api/upload_model', methods=['POST'])
def upload_model():
    db = None
    cursor = None
    try:
        if 'file' not in fk.request.files:
            return fk.jsonify({'success': False, 'message': '未检测到文件'}), 400
        file = fk.request.files['file']
        name = fk.request.form.get('name')
        tags = fk.request.form.get('tags', '[]')
        needs = fk.request.form.get('needs', '[]')
        desc = fk.request.form.get('desc', '')
        uploader = fk.request.form.get('uploader')
        if not all([file, name, uploader]):
            return fk.jsonify({'success': False, 'message': '参数不完整'}), 400
        if not allowed_file(file.filename):
            return fk.jsonify({'success': False, 'message': '仅支持zip文件'}), 400
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT id FROM users WHERE username=%s', (uploader, ))
        user_row = cursor.fetchone()
        if not user_row:
            return fk.jsonify({'success': False, 'message': '用户不存在'}), 400
        
        cursor.execute('SELECT id FROM models WHERE name=%s', (name, ))
        if cursor.fetchone():
            return fk.jsonify({
                'success': False,
                'message': '模型名已存在，请更换名称'
            }), 400
        user_id = user_row[0]
        filename = secure_filename(
            f"{name}_{int(datetime.datetime.now().timestamp())}.zip")

        tmp_save_path = os.path.join(MODEL_FOLDER, filename)
        os.makedirs(MODEL_FOLDER, exist_ok=True)
        file.save(tmp_save_path)
        if name is None:
            return fk.jsonify({'success': False, 'message': '模型名称为空'}), 400
        extract_path = os.path.join(MODEL_FOLDER, f'{name}_{int(datetime.datetime.now().timestamp())}')
        unzip_file(tmp_save_path, extract_path)
        os.remove(tmp_save_path)
        # 检查同名模型
        
        cursor.execute(
            'INSERT INTO models (user_id, name, tags, requirement_tag, path, `desc`, uploaded_at) VALUES (%s, %s, %s, %s, %s, %s, NOW())',
            (user_id, name, tags, needs, extract_path, desc))
        db.commit()
        return fk.jsonify({'success': True, 'message': '上传成功'})
    except Exception as e:
        return fk.jsonify({'success': False, 'message': str(e)}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'db' in locals() and db:
            db.close()


@app.route('/api/tags', methods=['GET'])
def get_tags():
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT tag FROM tag_library')
        tags = [row[0] for row in cursor.fetchall()]
        return fk.jsonify({'success': True, 'data': tags})
    except Exception as e:
        return fk.jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()  # type: ignore
        db.close()  # type: ignore


@app.route('/api/add_tag', methods=['POST'])
def add_tag():
    data = fk.request.get_json(silent=True) or {}
    tag = data.get('tag', '').strip()
    if not tag:
        return fk.jsonify({'success': False, 'message': '标签不能为空'}), 400
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT id FROM tag_library WHERE tag=%s', (tag, ))
        if cursor.fetchone():
            return fk.jsonify({'success': True, 'message': '标签已存在'})
        cursor.execute('INSERT INTO tag_library (tag) VALUES (%s)', (tag, ))
        db.commit()
        return fk.jsonify({'success': True, 'message': '添加成功'})
    except Exception as e:
        return fk.jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()  # type: ignore
        db.close()  # type: ignore


@app.route('/api/delete_model', methods=['POST'])
def delete_model():
    data = fk.request.get_json(silent=True) or {}
    model_id = data.get('id')
    username = data.get('username')
    if not model_id or not username:
        return fk.jsonify({'success': False, 'message': '参数不完整'}), 400
    try:
        db = get_db()
        cursor = db.cursor()
        # 查找用户id
        cursor.execute('SELECT id FROM users WHERE username=%s', (username,))
        user_row = cursor.fetchone()
        if not user_row:
            return fk.jsonify({'success': False, 'message': '用户不存在'}), 400
        user_id = user_row[0]
        # 检查模型归属
        cursor.execute('SELECT path FROM models WHERE id=%s AND user_id=%s', (model_id, user_id))
        model_row = cursor.fetchone()
        if not model_row:
            return fk.jsonify({'success': False, 'message': '无权删除该模型'}), 403
        # 删除数据库记录
        cursor.execute('DELETE FROM models WHERE id=%s', (model_id,))
        db.commit()
        # 删除文件夹
        save_path = os.path.join(MODEL_FOLDER, model_row[0])
        if os.path.exists(save_path):
            shutil.rmtree(save_path)
        return fk.jsonify({'success': True, 'message': '删除成功'})
    except Exception as e:
        return fk.jsonify({'success': False, 'message': str(e)}), 500
    finally:
        try:
            cursor.close() # type: ignore
            db.close() # type: ignore
        except:
            pass


@app.route('/api/datasets', methods=['GET'])
def get_datasets():
    def safe_json_loads(val):
        if not val:
            return []
        try:
            return json.loads(val)
        except Exception:
            return [v.strip().strip("'\"") for v in val.split(',') if v.strip()]
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            'SELECT d.id, d.name, d.tags, d.uploaded_at, u.username, d.path, d.`desc` FROM datasets d LEFT JOIN users u ON d.user_id = u.id')
        rows = cursor.fetchall()
        result = []
        for row in rows:
            result.append({
                'id': row[0],
                'name': row[1],
                'tags': safe_json_loads(row[2]),
                'date': row[3].strftime('%Y-%m-%d'),
                'uploader': row[4] or '',
                'file': row[5],
                'desc': row[6] or ''
            })
        return fk.jsonify({'data': result, 'total': len(result)})
    except Exception as e:
        return fk.jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()  # type: ignore
        db.close()  # type: ignore


@app.route('/api/upload_dataset', methods=['POST'])
def upload_dataset():
    db = None
    cursor = None
    try:
        if 'file' not in fk.request.files:
            return fk.jsonify({'success': False, 'message': '未检测到文件'}), 400
        file = fk.request.files['file']
        name = fk.request.form.get('name')
        tags = fk.request.form.get('tags', '[]')
        desc = fk.request.form.get('desc', '')
        uploader = fk.request.form.get('uploader')
        if not all([file, name, uploader]):
            return fk.jsonify({'success': False, 'message': '参数不完整'}), 400
        if not allowed_file(file.filename):
            return fk.jsonify({'success': False, 'message': '仅支持zip文件'}), 400
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT id FROM users WHERE username=%s', (uploader,))
        user_row = cursor.fetchone()
        if not user_row:
            return fk.jsonify({'success': False, 'message': '用户不存在'}), 400
        user_id = user_row[0]
        # 检查同名数据集
        cursor.execute('SELECT id FROM datasets WHERE name=%s', (name,))
        if cursor.fetchone():
            return fk.jsonify({'success': False, 'message': '数据集名已存在，请更换名称'}), 400
        filename = secure_filename(f"{name}_{int(datetime.datetime.now().timestamp())}.zip")
        tmp_save_path = os.path.join(DATASET_FOLDER, filename)
        os.makedirs(DATASET_FOLDER, exist_ok=True)
        file.save(tmp_save_path)
        extract_path = os.path.join(DATASET_FOLDER, f'{name}_{int(datetime.datetime.now().timestamp())}')
        unzip_file(tmp_save_path, extract_path)
        os.remove(tmp_save_path)
        cursor.execute(
            'INSERT INTO datasets (user_id, name, tags, path, `desc`, uploaded_at) VALUES (%s, %s, %s, %s, %s, NOW())',
            (user_id, name, tags, extract_path, desc)
        )
        db.commit()
        return fk.jsonify({'success': True, 'message': '上传成功'})
    except Exception as e:
        return fk.jsonify({'success': False, 'message': str(e)}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'db' in locals() and db:
            db.close()


@app.route('/api/delete_dataset', methods=['POST'])
def delete_dataset():
    data = fk.request.get_json(silent=True) or {}
    dataset_id = data.get('id')
    username = data.get('username')
    if not dataset_id or not username:
        return fk.jsonify({'success': False, 'message': '参数不完整'}), 400
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT id FROM users WHERE username=%s', (username,))
        user_row = cursor.fetchone()
        if not user_row:
            return fk.jsonify({'success': False, 'message': '用户不存在'}), 400
        user_id = user_row[0]
        cursor.execute('SELECT path FROM datasets WHERE id=%s AND user_id=%s', (dataset_id, user_id))
        dataset_row = cursor.fetchone()
        if not dataset_row:
            return fk.jsonify({'success': False, 'message': '无权删除该数据集'}), 403
        cursor.execute('DELETE FROM datasets WHERE id=%s', (dataset_id,))
        db.commit()
        save_path = os.path.join(DATASET_FOLDER, dataset_row[0])
        if os.path.exists(save_path):
            shutil.rmtree(save_path)
        return fk.jsonify({'success': True, 'message': '删除成功'})
    except Exception as e:
        return fk.jsonify({'success': False, 'message': str(e)}), 500
    finally:
        if 'cursor' in locals() and cursor: # type: ignore
            cursor.close()
        if 'db' in locals() and db: # type: ignore
            db.close()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9982, debug=True)
