import pymysql as sq
import flask as fk
import asyncio


app = fk.Flask(__name__)

@app.route('/test', methods=['GET'])
def hello():
    data = {'aaa' : 'bbb',
            'ccc' : 'ddd'}
    return fk.jsonify(data)

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=9982, debug=True)

    # db = sq.connect(host="127.0.0.1",
    #                 user="root",
    #                 password="wuhantuMJ0209",
    #                 port=3306)
    # print(db.get_server_info())
    # db.select_db('test')
    # p = db.cursor()

    # p.execute('select * from aaa')

    # p.close()
    # db.close()
