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
#             host = 'ssgpangdb.cwshg6arkkpy.ap-northeast-1.rds.amazonaws.comgg',
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

# 회원정보 수정 - AWS
def updateUserById(userId, userPw, userName, userEmail, userPhone, userAddress) :
    con = db_connect()
    cursor = con.cursor()
    sql_update = 'UPDATE users SET user_pw = %s, user_name = %s, user_email = %s, user_phone = %s, user_address = %s WHERE user_id = %s'

    result_num = cursor.execute(sql_update, (userPw, userName, userEmail, userPhone, userAddress, userId))
    
    cursor.close()
    con.close()

    return result_num

# 회원정보 수정 - Azure
def updateUserByIdAzure(userId, userPw, userName, userEmail, userPhone, userAddress) :
    con = db_connect_azure()
    cursor = con.cursor()
    sql_update = 'UPDATE users SET user_pw = %s, user_name = %s, user_email = %s, user_phone = %s, user_address = %s WHERE user_id = %s'

    result_num = cursor.execute(sql_update, (userPw, userName, userEmail, userPhone, userAddress, userId))
    
    cursor.close()
    con.close()

    return result_num

# 회원가입 시 ID 중복확인
def checkUserId(userId, CLOUD_PROVIDER) :
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
    sql_select = 'SELECT user_id FROM users WHERE user_id = %s'
    cursor.execute(sql_select, userId)
    result = cursor.fetchone()

    cursor.close()
    con.close()

    return result

# 회원가입 시 E-mail 중복확인
def checkUserEmail(userEmail, CLOUD_PROVIDER) :
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
    sql_select = 'SELECT user_email FROM users WHERE user_email = %s'
    cursor.execute(sql_select, userEmail)
    result = cursor.fetchone()

    cursor.close()
    con.close()

    return result

# 회원가입 시 PhoneNumber 중복확인
def checkUserPhoneNumber(userPhone, CLOUD_PROVIDER) :
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
    sql_select = 'SELECT user_phone FROM users WHERE user_phone = %s'
    cursor.execute(sql_select, userPhone)
    result = cursor.fetchone()

    cursor.close()
    con.close()

    return result

# 회원가입 - AWS
def insertUser(userId, userPw, userName, userEmail, userPhone, userAddress) :
    con = db_connect()
    cursor = con.cursor()
    sql_insert = 'INSERT INTO users (user_id, user_pw, user_name, user_email, user_phone, user_address) VALUES (%s, %s, %s, %s, %s, %s)'

    result_num = cursor.execute(sql_insert, (userId, userPw, userName, userEmail, userPhone, userAddress))
    
    cursor.close()
    con.close()

    return result_num

# 회원가입 - Azure
def insertUserAzure(userId, userPw, userName, userEmail, userPhone, userAddress) :
    con = db_connect_azure()
    cursor = con.cursor()
    sql_insert = 'INSERT INTO users (user_id, user_pw, user_name, user_email, user_phone, user_address) VALUES (%s, %s, %s, %s, %s, %s)'

    result_num = cursor.execute(sql_insert, (userId, userPw, userName, userEmail, userPhone, userAddress))
    
    cursor.close()
    con.close()

    return result_num

# 상품 등록 페이지 SELECT
def selectProductAll(CLOUD_PROVIDER):
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

    cursor = con.cursor(cursor=pymysql.cursors.DictCursor)
    sql_select = "SELECT * FROM product ORDER BY product_date DESC"
    cursor.execute(sql_select)
    
    result = []
    result = cursor.fetchall()
    
    cursor.close()
    con.close()

    return result

# 상품 장바구니에 담기
def insertCartList(cartUserId, cartProductCode):
    con = db_connect()
    cursor = con.cursor()
    # 해당 상품이 장바구니에 있는지 확인
    sql_select = 'SELECT product_count FROM cart WHERE user_id = %s AND product_code = %s'
    cursor.execute(sql_select, (cartUserId, cartProductCode))
    existing_product = cursor.fetchone()

    # 이미 장바구니에 있는 경우
    if existing_product:
        # 상품 수량 증가
        new_count = existing_product[0] + 1
        sql_update = 'UPDATE cart SET product_count = %s WHERE user_id = %s AND product_code = %s'
        cursor.execute(sql_update, (new_count, cartUserId, cartProductCode))
        result_num = new_count

    # 장바구니에 없는 경우
    else:  
        # 장바구니에 새 상품 추가
        sql_insert = 'INSERT INTO cart (user_id, product_code, product_count) VALUES (%s, %s, 1)'
        cursor.execute(sql_insert, (cartUserId, cartProductCode))
        result_num = 1

    con.commit()
    cursor.close()
    con.close()

    return result_num

# 상품 장바구니에 담기
def insertCartListAzure(cartUserId, cartProductCode):
    con = db_connect_azure()
    cursor = con.cursor()
    # 해당 상품이 장바구니에 있는지 확인
    sql_select = 'SELECT product_count FROM cart WHERE user_id = %s AND product_code = %s'
    cursor.execute(sql_select, (cartUserId, cartProductCode))
    existing_product = cursor.fetchone()

    # 이미 장바구니에 있는 경우
    if existing_product:
        # 상품 수량 증가
        new_count = existing_product[0] + 1
        sql_update = 'UPDATE cart SET product_count = %s WHERE user_id = %s AND product_code = %s'
        cursor.execute(sql_update, (new_count, cartUserId, cartProductCode))
        result_num = new_count

    # 장바구니에 없는 경우
    else:  
        # 장바구니에 새 상품 추가
        sql_insert = 'INSERT INTO cart (user_id, product_code, product_count) VALUES (%s, %s, 1)'
        cursor.execute(sql_insert, (cartUserId, cartProductCode))
        result_num = 1

    con.commit()
    cursor.close()
    con.close()

    return result_num

# 장바구니(Cart) 정보 SELECT
def selectCartListByUserId(userId, CLOUD_PROVIDER):
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

    cursor = con.cursor(cursor=pymysql.cursors.DictCursor)

    sql_select = """
    SELECT cart.*, product.*
    FROM cart
    INNER JOIN product ON cart.product_code = product.product_code
    WHERE cart.user_id = %s
    """
    cursor.execute(sql_select, (userId))
    result = cursor.fetchall()

    cursor.close()
    con.close()

    return result

# 장바구니(Cart) 삭제 - AWS
def deleteCartListByCode(num) :
    con = db_connect()
    cursor = con.cursor()

    sql_delete = 'DELETE FROM cart WHERE product_code = %s'
    result_num = cursor.execute(sql_delete, num)

    cursor.close()
    con.close()

    return result_num

# 장바구니(Cart) 삭제 - AWS
def deleteCartListByCodeAzure(num) :
    con = db_connect_azure()
    cursor = con.cursor()

    sql_delete = 'DELETE FROM cart WHERE product_code = %s'
    result_num = cursor.execute(sql_delete, num)

    cursor.close()
    con.close()

    return result_num

# 상품 검색
def selectProductForSearch(searchQuery, CLOUD_PROVIDER) :
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

    sql_select = 'SELECT * FROM product WHERE product_name LIKE %s;'
    cursor.execute(sql_select, f'%{searchQuery}%')
    
    result = cursor.fetchall()

    cursor.close()
    con.close()

    return result

# 장바구니(Cart) -> 주문(Orders) 테이블로 INSERT - AWS
def insertOrdersList(order_number, order_product_code, order_product_stock, 
                     order_product_price, order_user_id, order_user_name,
                     order_user_address, order_user_phone) :
    
    con = db_connect()
    cursor = con.cursor()

    sql_insert = '''INSERT INTO orders (order_number, order_product_code, 
                    order_product_stock, order_product_price,
                    order_user_id, order_user_name,
                    order_user_address, order_user_phone) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'''
    
    cursor.execute(sql_insert, (order_number, order_product_code, order_product_stock, 
                                order_product_price, order_user_id, order_user_name, 
                                order_user_address, order_user_phone))

    con.commit()
    cursor.close()
    con.close()

# 장바구니(Cart) -> 주문(Orders) 테이블로 INSERT - Azure
def insertOrdersListAzure(order_number, order_product_code, order_product_stock, 
                     order_product_price, order_user_id, order_user_name,
                     order_user_address, order_user_phone) :
    
    con = db_connect_azure()
    cursor = con.cursor()

    sql_insert = '''INSERT INTO orders (order_number, order_product_code, 
                    order_product_stock, order_product_price,
                    order_user_id, order_user_name,
                    order_user_address, order_user_phone) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'''
    
    cursor.execute(sql_insert, (order_number, order_product_code, order_product_stock, 
                                order_product_price, order_user_id, order_user_name, 
                                order_user_address, order_user_phone))

    con.commit()
    cursor.close()
    con.close()    

# 결제 후 장바구니(Cart) 상품 전체 비우기 - AWS
def deleteCartListAll(userId) :
    con = db_connect()
    cursor = con.cursor()

    sql_delete = 'DELETE FROM cart WHERE user_id = %s'
    result_num = cursor.execute(sql_delete, userId)

    cursor.close()
    con.close()

    return result_num

# 결제 후 장바구니(Cart) 상품 전체 비우기 - Azure
def deleteCartListAllAzure(userId) :
    con = db_connect_azure()
    cursor = con.cursor()

    sql_delete = 'DELETE FROM cart WHERE user_id = %s'
    result_num = cursor.execute(sql_delete, userId)

    cursor.close()
    con.close()

    return result_num

# 장바구니 Cart List 상품수량 변경 시 UPDATE - AWS
def updateCartList(product_code, new_quantity, userId) :
    con = db_connect()
    cursor = con.cursor()
    sql_update = 'UPDATE cart SET product_count = %s WHERE user_id = %s AND product_code = %s'

    result_num = cursor.execute(sql_update, (new_quantity, userId, product_code))
    
    cursor.close()
    con.close()

    return result_num

# 장바구니 Cart List 상품수량 변경 시 UPDATE - Azure
def updateCartListAzure(product_code, new_quantity, userId) :
    con = db_connect_azure()
    cursor = con.cursor()
    sql_update = 'UPDATE cart SET product_count = %s WHERE user_id = %s AND product_code = %s'

    result_num = cursor.execute(sql_update, (new_quantity, userId, product_code))
    
    cursor.close()
    con.close()

    return result_num

# 주문 내역 정보
def selectOrdersAll(userId, CLOUD_PROVIDER):
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

    cursor = con.cursor(cursor=pymysql.cursors.DictCursor)
    sql_select = """
    SELECT 
        o.order_number,
        o.order_product_code,
        p.product_name,
        o.order_product_stock,
        o.order_product_price,
        o.order_product_status,
        o.order_product_date,
        o.order_user_id,
        o.order_user_name,
        o.order_user_address,
        o.order_user_phone
    FROM 
        orders o
    INNER JOIN 
        product p
    ON 
        o.order_product_code = p.product_code
    WHERE
        o.order_user_id = %s
    """
    
    cursor.execute(sql_select, userId)
    
    result = []
    result = cursor.fetchall()
    
    cursor.close()
    con.close()

    return result