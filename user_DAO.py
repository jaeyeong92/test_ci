import pymysql

# DB 연결
def db_connect() :
    db = pymysql.connect(
        user = 'root',
        password = 'admin12345',
        host = 'coupangdb.cwshg6arkkpy.ap-northeast-1.rds.amazonaws.com',
        db = 'coupang',
        charset = 'utf8',
        autocommit = True
    )

    return db

# 회원 정보 UPDATE
def updateUserById(userId, userPw, userName, userEmail, userPhone, userAddress) :

    con = db_connect()
    cursor = con.cursor()
    sql_update = 'UPDATE user SET user_pw = %s, user_name = %s, user_email = %s, user_phone = %s, user_address = %s WHERE user_id = %s'

    result_num = cursor.execute(sql_update, (userPw, userName, userEmail, userPhone, userAddress, userId))
    
    cursor.close()
    con.close()

    return result_num

# 회원가입 시 ID 중복확인
def checkUserId(userId) :

    result = []
    con = db_connect()

    cursor = con.cursor(cursor=pymysql.cursors.DictCursor)
    sql_select = 'SELECT user_id FROM user WHERE user_id = %s'
    cursor.execute(sql_select, userId)
    result = cursor.fetchone()

    # 연결 종료
    cursor.close()
    con.close()

    return result

# 회원가입 시 E-mail 중복확인
def checkUserEmail(userEmail) :

    result = []
    con = db_connect()

    cursor = con.cursor(cursor=pymysql.cursors.DictCursor)
    sql_select = 'SELECT user_email FROM user WHERE user_email = %s'
    cursor.execute(sql_select, userEmail)
    result = cursor.fetchone()

    # 연결 종료
    cursor.close()
    con.close()

    return result

# 회원가입 시 PhoneNumber 중복확인
def checkUserPhoneNumber(userPhone) :

    result = []
    con = db_connect()

    cursor = con.cursor(cursor=pymysql.cursors.DictCursor)
    sql_select = 'SELECT user_phone FROM user WHERE user_phone = %s'
    cursor.execute(sql_select, userPhone)
    result = cursor.fetchone()

    # 연결 종료
    cursor.close()
    con.close()

    return result

# 회원 정보 INSERT (회원가입)
def insertUser(userId, userPw, userName, userEmail, userPhone, userAddress) :
    
    con = db_connect()
    cursor = con.cursor()
    sql_insert = 'INSERT INTO user (user_id, user_pw, user_name, user_email, user_phone, user_address) VALUES (%s, %s, %s, %s, %s, %s)'

    result_num = cursor.execute(sql_insert, (userId, userPw, userName, userEmail, userPhone, userAddress))
    
    cursor.close()
    con.close()

    return result_num

# 상품 등록 페이지 SELECT
def selectProductAll():
    # MySQL 데이터베이스에 연결
    con = db_connect()
    cursor = con.cursor(cursor=pymysql.cursors.DictCursor)

    # S3 URL을 데이터베이스에 저장하는 쿼리 실행
    sql_select = "SELECT * FROM product ORDER BY product_date DESC"
    cursor.execute(sql_select)
    
    result = []
    result = cursor.fetchall()
    
    # 연결 종료
    cursor.close()
    con.close()

    return result

# 장바구니 Cart INSERT
def insertCartList(cartUserId, cartProductCode) :
    
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

# 장바구니(Cart) 정보 SELECT
def selectCartListByUserId(userId):
    con = db_connect()
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

# 장바구니(Cart) 상품 삭제
def deleteCartListByCode(num) :
    con = db_connect()
    cursor = con.cursor()

    sql_delete = 'DELETE FROM cart WHERE product_code = %s'
    result_num = cursor.execute(sql_delete, num)

    cursor.close()
    con.close()

    return result_num

# 상품 검색
def selectProductForSearch(searchQuery) :

    result = []
    con = db_connect()
    cursor = con.cursor(cursor=pymysql.cursors.DictCursor)

    sql_select = 'SELECT * FROM product WHERE product_name LIKE %s;'
    cursor.execute(sql_select, f'%{searchQuery}%')
    
    result = cursor.fetchall()

    cursor.close()
    con.close()

    return result

# 장바구니(Cart) -> 주문(Orders) 테이블로 INSERT
def insertOrdersList(order_number, order_product_code, 
                     order_product_stock, order_product_price,
                     order_user_id, order_user_name,
                     order_user_address, order_user_phone) :
    
    con = db_connect()
    cursor = con.cursor()

    # 장바구니에 새 상품 추가
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

# 결제 후 장바구니(Cart) 상품 전체 비우기
def deleteCartListAll(userId) :
    con = db_connect()
    cursor = con.cursor()

    sql_delete = 'DELETE FROM cart WHERE user_id = %s'
    result_num = cursor.execute(sql_delete, userId)

    cursor.close()
    con.close()

    return result_num

# 장바구니 Cart List 상품수량 변경 시 UPDATE
def updateCartList(product_code, new_quantity, userId) :

    con = db_connect()
    cursor = con.cursor()
    sql_update = 'UPDATE cart SET product_count = %s WHERE user_id = %s AND product_code = %s'

    result_num = cursor.execute(sql_update, (new_quantity, userId, product_code))
    
    cursor.close()
    con.close()

    return result_num