import pymysql as sq

def get_db():
    return sq.connect(
        host="127.0.0.1",
        user="root",
        password="wuhantuMJ0209",
        port=3306,
        database='root',
        charset='utf8mb4'
    )

if __name__ == '__main__':
    db = get_db()
    print(db.get_server_info())
    print(db.get_host_info())
    db.close()