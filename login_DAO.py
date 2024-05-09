import pymysql

# DB 연결
def db_connect() :
    db = pymysql.connect(
        user = 'root',
        password = 'admin12345',
        host = 'db-svc',
        db = 'ssgpang',
        charset = 'utf8',
        autocommit = True
    )

    return db

# 로그인 시 DB 확인
def selectUserById(userId) :

    result = []
    con = db_connect()

    cursor = con.cursor(cursor=pymysql.cursors.DictCursor)
    sql_select = 'SELECT * FROM user WHERE user_id = %s'
    cursor.execute(sql_select, userId)
    result = cursor.fetchone()

    # 연결 종료
    cursor.close()
    con.close()

    return result

