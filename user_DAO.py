import pymysql

# # DB 연결 - AWS
# def db_connect() :
#     db = pymysql.connect(
#         user = 'root',
#         password = 'admin12345',
#         host = 'db-svc',
#         db = 'ssgpang',
#         charset = 'utf8',
#         autocommit = True
#     )
#     return db

# # DB 연결 - Azure
# def db_connect_azure() :
#     db = pymysql.connect(
#         user = 'azureroot',
#         password = 'admin12345!!',
#         host = '10.1.2.101',
#         db = 'ssgpang',
#         charset = 'utf8',
#         autocommit = True
#     )
#     return db

# DB 연결 - AWS
def db_connect() :
    db = pymysql.connect(
        user = 'root',
        password = 'admin12345',
        host = 'ssgpangdb.cwshg6arkkpy.ap-northeast-1.rds.amazonaws.com',
        db = 'ssgpang',
        charset = 'utf8',
        autocommit = True
    )
    return db

# DB 연결 - Azure
def db_connect_azure() :
    db = pymysql.connect(
        user = 'azureroot',
        password = 'admin12345!!',
        host = 'ssgpang-db.mysql.database.azure.com',
        db = 'ssgpang',
        charset = 'utf8',
        autocommit = True
    )
    return db

# 회원 정보 UPDATE
def updateUserById(userId, userPw, userName, userEmail, userPhone, 
                   userAddress, cloud_provider, AWS_AZURE_INSERT_FLAG) :
    try:
        # AWS_AZURE_INSERT_FLAG가 True일 경우
        if AWS_AZURE_INSERT_FLAG:
            con = None
            cursor = None
            # AWS
            if cloud_provider == 'AWS':
                con = db_connect()
                con_azure = db_connect_azure()

                cursor = con.cursor()
                cursor_azure = con_azure.cursor()

                sql_update_aws = 'UPDATE users SET user_pw = %s, user_name = %s, user_email = %s, user_phone = %s, user_address = %s WHERE user_id = %s'
                sql_update_azure = 'UPDATE users SET user_pw = %s, user_name = %s, user_email = %s, user_phone = %s, user_address = %s WHERE user_id = %s'

                result_num = cursor.execute(sql_update_aws, (userPw, userName, userEmail, userPhone, userAddress, userId))
                result_num = cursor_azure.execute(sql_update_azure, (userPw, userName, userEmail, userPhone, userAddress, userId))
                con.commit()
                con_azure.commit()

            # AZURE
            else:
                con = db_connect_azure()
                cursor = con.cursor()

                sql_update_azure = 'UPDATE users SET user_pw = %s, user_name = %s, user_email = %s, user_phone = %s, user_address = %s WHERE user_id = %s'

                result_num = cursor.execute(sql_update_azure, (userPw, userName, userEmail, userPhone, userAddress, userId))
                con.commit()

        # AWS_AZURE_INSERT_FLAG가 False일 경우
        else:
            # AWS
            if cloud_provider == 'AWS':
                con = db_connect()
            # AZURE
            else:
                con = db_connect_azure()

            cursor = con.cursor()

            sql_update = 'UPDATE users SET user_pw = %s, user_name = %s, user_email = %s, user_phone = %s, user_address = %s WHERE user_id = %s'
            result_num = cursor.execute(sql_update, (userPw, userName, userEmail, userPhone, userAddress, userId))
            con.commit()

    except Exception as e:
        print("Error:", e)
        if con:
            con.rollback()

    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()

    return result_num

# 회원가입 시 ID 중복확인
def checkUserId(userId, cloud_provider) :
    # AWS
    if cloud_provider == 'AWS' :
        con = db_connect()
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
def checkUserEmail(userEmail, cloud_provider) :
    # AWS
    if cloud_provider == 'AWS' :
        con = db_connect()
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
def checkUserPhoneNumber(userPhone, cloud_provider) :
    # AWS
    if cloud_provider == 'AWS' :
        con = db_connect()
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

# 회원 정보 INSERT (회원가입)
def insertUser(userId, userPw, userName, 
               userEmail, userPhone, userAddress, cloud_provider, AWS_AZURE_INSERT_FLAG) :
    try:
        # AWS_AZURE_INSERT_FLAG가 True일 경우
        if AWS_AZURE_INSERT_FLAG:
            con = None
            cursor = None
            # AWS
            if cloud_provider == 'AWS':
                con = db_connect()
                con_azure = db_connect_azure()

                cursor = con.cursor()
                cursor_azure = con_azure.cursor()

                sql_insert_aws = 'INSERT INTO users (user_id, user_pw, user_name, user_email, user_phone, user_address) VALUES (%s, %s, %s, %s, %s, %s)'
                sql_insert_azure = 'INSERT INTO users (user_id, user_pw, user_name, user_email, user_phone, user_address) VALUES (%s, %s, %s, %s, %s, %s)'

                result_num = cursor.execute(sql_insert_aws, (userId, userPw, userName, userEmail, userPhone, userAddress))
                result_num = cursor_azure.execute(sql_insert_azure, (userId, userPw, userName, userEmail, userPhone, userAddress))
                con.commit()
                con_azure.commit()

            # AZURE
            else:
                con = db_connect_azure()
                cursor = con.cursor()

                sql_insert_azure = 'INSERT INTO users (user_id, user_pw, user_name, user_email, user_phone, user_address) VALUES (%s, %s, %s, %s, %s, %s)'

                result_num = cursor.execute(sql_insert_azure, (userId, userPw, userName, userEmail, userPhone, userAddress))
                con.commit()

        # AWS_AZURE_INSERT_FLAG가 False일 경우
        else:
            # AWS
            if cloud_provider == 'AWS':
                con = db_connect()
            # AZURE
            else:
                con = db_connect_azure()

            cursor = con.cursor()

            sql_insert = 'INSERT INTO users (user_id, user_pw, user_name, user_email, user_phone, user_address) VALUES (%s, %s, %s, %s, %s, %s)'
            result_num = result_num = cursor.execute(sql_insert, (userId, userPw, userName, userEmail, userPhone, userAddress))
            con.commit()

    except Exception as e:
        print("Error:", e)
        if con:
            con.rollback()

    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()

    return result_num

# 상품 등록 페이지 SELECT
def selectProductAll(cloud_provider):
    # AWS
    if cloud_provider == 'AWS' :
        con = db_connect()
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

# 장바구니 Cart INSERT
def insertCartList(cartUserId, cartProductCode, cloud_provider, AWS_AZURE_INSERT_FLAG):
    try:
        # AWS_AZURE_INSERT_FLAG가 True일 경우
        if AWS_AZURE_INSERT_FLAG:
            con = None
            cursor = None
            # AWS
            if cloud_provider == 'AWS':
                con = db_connect()
                con_azure = db_connect_azure()

                cursor = con.cursor()
                cursor_azure = con_azure.cursor()

                # 해당 상품이 장바구니에 있는지 확인
                sql_select_aws = 'SELECT product_count FROM cart WHERE user_id = %s AND product_code = %s'
                cursor.execute(sql_select_aws, (cartUserId, cartProductCode))
                existing_product_aws = cursor.fetchone()

                # 해당 상품이 장바구니에 있는지 확인
                sql_select_azure = 'SELECT product_count FROM cart WHERE user_id = %s AND product_code = %s'
                cursor_azure.execute(sql_select_azure, (cartUserId, cartProductCode))
                existing_product_azure = cursor_azure.fetchone()

                # 이미 장바구니에 있는 경우
                if existing_product_aws or existing_product_azure:
                    # 상품 수량 증가
                    if existing_product_aws:
                        new_count = existing_product_aws[0] + 1
                        sql_update_aws = 'UPDATE cart SET product_count = %s WHERE user_id = %s AND product_code = %s'
                        cursor.execute(sql_update_aws, (new_count, cartUserId, cartProductCode))

                    if existing_product_azure:
                        new_count = existing_product_azure[0] + 1
                        sql_update_azure = 'UPDATE cart SET product_count = %s WHERE user_id = %s AND product_code = %s'
                        cursor_azure.execute(sql_update_azure, (new_count, cartUserId, cartProductCode))
                    
                    result_num = new_count

                # 장바구니에 없는 경우
                else:
                    # 장바구니에 새 상품 추가
                    sql_insert_aws = 'INSERT INTO cart (user_id, product_code, product_count) VALUES (%s, %s, 1)'
                    cursor.execute(sql_insert_aws, (cartUserId, cartProductCode))
                    result_num = 1

                    sql_insert_azure = 'INSERT INTO cart (user_id, product_code, product_count) VALUES (%s, %s, 1)'
                    cursor_azure.execute(sql_insert_azure, (cartUserId, cartProductCode))
                    
            # AZURE
            else:
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

        # AWS_AZURE_INSERT_FLAG가 False일 경우
        else:
            # AWS
            if cloud_provider == 'AWS':
                con = db_connect()
            # AZURE
            else:
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
        
    except Exception as e:
        print("Error:", e)
        if con:
            con.rollback()

    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()

    return result_num


# 장바구니(Cart) 정보 SELECT
def selectCartListByUserId(userId, cloud_provider):
    # AWS
    if cloud_provider == 'AWS' :
        con = db_connect()
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

# 장바구니(Cart) 상품 삭제
def deleteCartListByCode(num, cloud_provider, AWS_AZURE_INSERT_FLAG) :
    try:
        # AWS_AZURE_INSERT_FLAG가 True일 경우
        if AWS_AZURE_INSERT_FLAG:
            con = None
            cursor = None
            # AWS
            if cloud_provider == 'AWS':
                con = db_connect()
                con_azure = db_connect_azure()

                cursor = con.cursor()
                cursor_azure = con_azure.cursor()

                sql_delete_aws = 'DELETE FROM cart WHERE product_code = %s'
                sql_delete_azure = 'DELETE FROM cart WHERE product_code = %s'

                result_num = cursor.execute(sql_delete_aws, num)
                cursor_azure.execute(sql_delete_azure, num)

            # AZURE
            else:
                con = db_connect_azure()
                cursor = con.cursor()

                sql_delete_azure = 'DELETE FROM cart WHERE product_code = %s'

                result_num = cursor.execute(sql_delete_azure, num)

        # AWS_AZURE_INSERT_FLAG가 False일 경우        
        else:
            # AWS
            if cloud_provider == 'AWS' :
                con = db_connect()
            # AZURE    
            else :
                con = db_connect_azure()

            cursor = con.cursor()

            sql_delete = 'DELETE FROM cart WHERE product_code = %s'
            result_num = cursor.execute(sql_delete, num)

    except Exception as e:
        print("Error:", e)
        if con:
            con.rollback()

    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()

    return result_num


# 상품 검색
def selectProductForSearch(searchQuery, cloud_provider) :
    # AWS
    if cloud_provider == 'AWS' :
        con = db_connect()
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

# 장바구니(Cart) -> 주문(Orders) 테이블로 INSERT
def insertOrdersList(order_number, order_product_code, 
                     order_product_stock, order_product_price,
                     order_user_id, order_user_name,
                     order_user_address, order_user_phone, cloud_provider, AWS_AZURE_INSERT_FLAG) :
    try:
        # AWS_AZURE_INSERT_FLAG가 True일 경우
        if AWS_AZURE_INSERT_FLAG:
            con = None
            cursor = None
            # AWS
            if cloud_provider == 'AWS':
                con = db_connect()
                con_azure = db_connect_azure()

                cursor = con.cursor()
                cursor_azure = con_azure.cursor()

                sql_insert_aws = '''INSERT INTO orders (order_number, order_product_code, 
                                    order_product_stock, order_product_price,
                                    order_user_id, order_user_name,
                                    order_user_address, order_user_phone) 
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'''

                sql_insert_azure = '''INSERT INTO orders (order_number, order_product_code, 
                                    order_product_stock, order_product_price,
                                    order_user_id, order_user_name,
                                    order_user_address, order_user_phone) 
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'''

                cursor.execute(sql_insert_aws, (order_number, order_product_code, 
                                                order_product_stock, order_product_price,
                                                order_user_id, order_user_name,
                                                order_user_address, order_user_phone))
                cursor_azure.execute(sql_insert_azure, (order_number, order_product_code, 
                                                          order_product_stock, order_product_price,
                                                          order_user_id, order_user_name,
                                                          order_user_address, order_user_phone))

                con.commit()
                con_azure.commit()

            # AZURE
            else:
                con = db_connect_azure()
                cursor = con.cursor()

                sql_insert_azure = '''INSERT INTO orders (order_number, order_product_code, 
                                      order_product_stock, order_product_price,
                                      order_user_id, order_user_name,
                                      order_user_address, order_user_phone) 
                                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'''

                cursor.execute(sql_insert_azure, (order_number, order_product_code, 
                                                  order_product_stock, order_product_price,
                                                  order_user_id, order_user_name,
                                                  order_user_address, order_user_phone))

                con.commit()

        # AWS_AZURE_INSERT_FLAG가 False일 경우
        else:
            # AWS
            if cloud_provider == 'AWS' :
                con = db_connect()
            # AZURE    
            else :
                con = db_connect_azure()     
            
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
            
    except Exception as e:
        print("Error:", e)
        if con:
            con.rollback()

    finally:
        if cursor:  
            cursor.close()
        if con:
            con.close()

# 결제 후 장바구니(Cart) 상품 전체 비우기
def deleteCartListAll(userId, cloud_provider, AWS_AZURE_INSERT_FLAG) :
    try:
        # AWS_AZURE_INSERT_FLAG가 True일 경우
        if AWS_AZURE_INSERT_FLAG:
            con = None
            cursor = None
            # AWS
            if cloud_provider == 'AWS':
                con = db_connect()
                con_azure = db_connect_azure()

                cursor = con.cursor()
                cursor_azure = con_azure.cursor()

                sql_delete_aws = 'DELETE FROM cart WHERE user_id = %s'
                sql_delete_azure = 'DELETE FROM cart WHERE user_id = %s'

                result_num = cursor.execute(sql_delete_aws, userId)
                cursor_azure.execute(sql_delete_azure, userId)

            # AZURE
            else:
                con = db_connect_azure()
                cursor = con.cursor()

                sql_delete_azure = 'DELETE FROM cart WHERE user_id = %s'
                result_num = cursor.execute(sql_delete_azure, userId)

        # AWS_AZURE_INSERT_FLAG가 False일 경우
        else:
            # AWS
            if cloud_provider == 'AWS' :
                con = db_connect()
            # AZURE    
            else :
                con = db_connect_azure()

            cursor = con.cursor()

            sql_delete = 'DELETE FROM cart WHERE user_id = %s'
            result_num = cursor.execute(sql_delete, userId)

    except Exception as e:
        print("Error:", e)
        if con:
            con.rollback()

    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()

    return result_num

# 장바구니 Cart List 상품수량 변경 시 UPDATE
def updateCartList(product_code, new_quantity, userId, cloud_provider, AWS_AZURE_INSERT_FLAG) :
    try:
        # AWS_AZURE_INSERT_FLAG가 True일 경우
        if AWS_AZURE_INSERT_FLAG:
            con = None
            cursor = None
            # AWS
            if cloud_provider == 'AWS':
                con = db_connect()
                con_azure = db_connect_azure()

                cursor = con.cursor()
                cursor_azure = con_azure.cursor()

                sql_update_aws = 'UPDATE cart SET product_count = %s WHERE user_id = %s AND product_code = %s'
                sql_update_azure = 'UPDATE cart SET product_count = %s WHERE user_id = %s AND product_code = %s'

                result_num = cursor.execute(sql_update_aws, (new_quantity, userId, product_code))
                cursor_azure.execute(sql_update_azure, (new_quantity, userId, product_code))

            # AZURE
            else:
                con = db_connect_azure()
                cursor = con.cursor()

                sql_update_azure = 'UPDATE cart SET product_count = %s WHERE user_id = %s AND product_code = %s'
                result_num = cursor.execute(sql_update_azure, (new_quantity, userId, product_code))

        # AWS_AZURE_INSERT_FLAG가 False일 경우
        else:
            # AWS
            if cloud_provider == 'AWS' :
                con = db_connect()
            # AZURE    
            else :
                con = db_connect_azure()

            cursor = con.cursor()
            sql_update = 'UPDATE cart SET product_count = %s WHERE user_id = %s AND product_code = %s'
            result_num = cursor.execute(sql_update, (new_quantity, userId, product_code))
        
    except Exception as e:
        print("Error:", e)
        if con:
            con.rollback()

    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()

    return result_num

# 주문 내역 정보
def selectOrdersAll(userId, cloud_provider):
    # AWS
    if cloud_provider == 'AWS' :
        con = db_connect()
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