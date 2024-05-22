import pymysql

# DB 연결 - AWS
def db_connect() :
    try:
        db = pymysql.connect(
            user = 'root',
            password = 'admin12345',
            host = 'db-svc',
            db = 'ssgpang',
            charset = 'utf8',
            autocommit = True
        )
        return db
    
    except pymysql.MySQLError as e:
        print("AWS DB Connection Failed: ", e)
        return None
    
# DB 연결 - Azure
def db_connect_azure() :
    try:
        db = pymysql.connect(
            user = 'azureroot',
            password = 'admin12345!!',
            host = '10.1.2.101',
            db = 'ssgpang',
            charset = 'utf8',
            autocommit = True
        )
        return db
    
    except pymysql.MySQLError as e:
        print("Azure DB Connection Failed: ", e)
        return None

# # DB 연결 - AWS
# def db_connect() :
#     try:
#         db = pymysql.connect(
#             user = 'admin',
#             password = 'admin12345',
#             host = 'ssgpangdb.cwshg6arkkpy.ap-northeast-1.rds.amazonaws.com',
#             db = 'ssgpang',
#             charset = 'utf8',
#             autocommit = True
#         )
#         return db
    
#     except pymysql.MySQLError as e:
#         print("AWS DB Connection Failed: ", e)
#         return None

# # DB 연결 - Azure
# def db_connect_azure() :
#     try:
#         db = pymysql.connect(
#             user = 'azureroot',
#             password = 'admin12345!!',
#             host = 'ssgpang-db-server.mysql.database.azure.com',
#             db = 'ssgpang',
#             charset = 'utf8',
#             autocommit = True
#         )
#         return db
    
#     except pymysql.MySQLError as e:
#         print("Azure DB Connection Failed: ", e)
#         return None

# 로그인 시 DB 확인
def selectUserById(userId, CLOUD_PROVIDER) :
    con = None

    # AWS
    if CLOUD_PROVIDER == 'AWS' :
        con = db_connect()
        if con is None:
            print("Switching to Azure DB due to AWS connection failure.")
            con = db_connect_azure()
    # AZURE    
    else :
        con = db_connect_azure()

    result = []
    cursor = con.cursor(cursor=pymysql.cursors.DictCursor)
    sql_select = 'SELECT * FROM users WHERE user_id = %s'
    cursor.execute(sql_select, userId)
    result = cursor.fetchone()

    cursor.close()
    con.close()

    return result

