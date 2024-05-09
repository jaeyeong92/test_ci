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

# DB 연결
def db_connect_azure() :
    db = pymysql.connect(
        user = 'azureroot',
        password = 'admin12345!!',
        host = '10.1.10.10',
        db = 'ssgpang',
        charset = 'utf8',
        autocommit = True
    )

    return db

# S3 Image URL을 DB에 저장
def saveToDatabase(productName, productPrice, productStock, productDescription, s3_filename, azure_filename):
    # MySQL 데이터베이스에 연결
    con = db_connect_azure()
    cursor = con.cursor()

    # S3 URL을 데이터베이스에 저장하는 쿼리 실행
    sql_insert = "INSERT INTO product (product_name, product_price, product_stock, product_description, product_image_aws, product_image_azure) VALUES (%s, %s, %s, %s, %s, %s)"
    result_num = cursor.execute(sql_insert, (productName, productPrice, productStock, productDescription, 'ssgproduct/'+ s3_filename, azure_filename))
    
    # 변경 사항 커밋
    con.commit()
    
    # 연결 종료
    cursor.close()
    con.close()

# DB to JSON
def dbToJson():
    # MySQL 데이터베이스에 연결
    con = db_connect_azure()
    cursor = con.cursor()

    # S3 URL을 데이터베이스에 저장하는 쿼리 실행
    sql_select = "SELECT product_name, product_price, product_stock, product_description, product_image_aws, product_image_azure FROM product"
    cursor.execute(sql_select)
    result = cursor.fetchall()
    
    # 연결 종료
    cursor.close()
    con.close()

    return result

# 상품 등록 페이지 SELECT
def selectProductAll():
    # MySQL 데이터베이스에 연결
    con = db_connect_azure()
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

# 상품정보 수정 SELECT
def selectProductByCode(num) :

    result = []
    con = db_connect_azure()
    cursor = con.cursor(cursor=pymysql.cursors.DictCursor)

    sql_select = 'SELECT * FROM product WHERE product_code = %s'
    cursor.execute(sql_select, num)
    result = cursor.fetchone()

    cursor.close()
    con.close()

    return result

# 상품정보 수정 UPDATE
def updateProductByCode(productName, productPrice, productStock, productDescription, s3_filename, azure_filename, num) :
    # MySQL 데이터베이스에 연결
    con = db_connect_azure()
    cursor = con.cursor()

    # S3 URL을 데이터베이스에 저장하는 쿼리 실행
    sql_update = "UPDATE product SET product_name = %s, product_price = %s, product_stock = %s, product_description = %s, product_image_aws = %s, product_image_azure = %s WHERE product_code = %s"
    result_num = cursor.execute(sql_update, (productName, productPrice, productStock, productDescription, 'ssgproduct/'+ s3_filename, azure_filename, num))
    
    # 연결 종료
    cursor.close()
    con.close()

    return result_num

# 상품 삭제
def deleteProductByCode(num) :
    con = db_connect_azure()
    cursor = con.cursor()

    sql_delete = 'DELETE FROM product WHERE product_code = %s'
    result_num = cursor.execute(sql_delete, num)

    cursor.close()
    con.close()

    return result_num




