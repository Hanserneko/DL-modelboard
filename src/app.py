import pymysql as sq
import flask as fk
import asyncio

app = fk.Flask(__name__)

# connect blueprint
from src.login.login import login_bp

app.register_blueprint(login_bp)

@app.route('/test', methods=['GET'])
def test():
    return fk.jsonify({'msg': '测试成功'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9982, debug=False)
