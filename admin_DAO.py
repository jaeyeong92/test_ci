import pymysql

# DB 연결 - AWS
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

# DB 연결 - Azure
def db_connect_azure() :
    db = pymysql.connect(
        user = 'azureroot',
        password = 'admin12345!!',
        host = '10.1.2.101',
        db = 'ssgpang',
        charset = 'utf8',
        autocommit = True
    )

    return db

# # DB 연결 - AWS
# def db_connect() :
#     db = pymysql.connect(
#         user = 'admin',
#         password = 'admin12345',
#         host = 'ssgpangdb.cwshg6arkkpy.ap-northeast-1.rds.amazonaws.com',
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
#         host = 'ssgpang-db-server.mysql.database.azure.com',
#         db = 'ssgpang',
#         charset = 'utf8',
#         autocommit = True
#     )

#     return db

# 상품정보 등록 - AWS
def insertProduct(productName, productPrice,
                  productStock, productDescription,
                  s3_filename, azure_filename) :
    
    con = db_connect()
    cursor = con.cursor()

    # 상품정보, Image URL을 데이터베이스에 저장하는 쿼리 실행
    sql_insert = "INSERT INTO product (product_name, product_price, product_stock, product_description, product_image_aws, product_image_azure) VALUES (%s, %s, %s, %s, %s, %s)"
    result_num = cursor.execute(sql_insert, (productName, productPrice, productStock, productDescription, 'ssgproduct/'+ s3_filename, azure_filename))
    
    con.commit()
    cursor.close()
    con.close()

# 상품정보 등록 - Azure
def insertProductAzure(productName, productPrice,
                  productStock, productDescription,
                  s3_filename, azure_filename) :
    
    con = db_connect_azure()
    cursor = con.cursor()

    # 상품정보, Image URL을 데이터베이스에 저장하는 쿼리 실행
    sql_insert = "INSERT INTO product (product_name, product_price, product_stock, product_description, product_image_aws, product_image_azure) VALUES (%s, %s, %s, %s, %s, %s)"
    result_num = cursor.execute(sql_insert, (productName, productPrice, productStock, productDescription, 'ssgproduct/'+ s3_filename, azure_filename))
    
    con.commit()
    cursor.close()
    con.close()    

# DB to JSON
def dbToJson(cloud_provider) :
    # AWS
    if cloud_provider == 'AWS' :
        con = db_connect()
    # AZURE    
    else :
        con = db_connect_azure()

    cursor = con.cursor()

    sql_select = "SELECT product_name, product_price, product_stock, product_description, product_image_aws, product_image_azure FROM product"
    cursor.execute(sql_select)
    result = cursor.fetchall()
    
    cursor.close()
    con.close()

    return result

# 상품 페이지
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

# 상품정보 수정을 위한 SELECT
def selectProductByCode(num, cloud_provider) :
    # AWS
    if cloud_provider == 'AWS' :
        con = db_connect()
    # AZURE    
    else :
        con = db_connect_azure()

    result = []
    cursor = con.cursor(cursor=pymysql.cursors.DictCursor)

    sql_select = 'SELECT * FROM product WHERE product_code = %s'
    cursor.execute(sql_select, num)
    result = cursor.fetchone()

    cursor.close()
    con.close()

    return result

# 상품정보 수정 - AWS
def updateProductByCode(productName, productPrice, 
                        productStock, productDescription, 
                        s3_filename, azure_filename, num) :
    
    con = db_connect()
    cursor = con.cursor()

    sql_update = "UPDATE product SET product_name = %s, product_price = %s, product_stock = %s, product_description = %s, product_image_aws = %s, product_image_azure = %s WHERE product_code = %s"
    result_num = cursor.execute(sql_update, (productName, productPrice, productStock, productDescription, 'ssgproduct/'+ s3_filename, azure_filename, num))
    
    cursor.close()
    con.close()

    return result_num

# 상품정보 수정 - Azure
def updateProductByCodeAzure(productName, productPrice, 
                        productStock, productDescription, 
                        s3_filename, azure_filename, num) :
    
    con = db_connect_azure()
    cursor = con.cursor()

    sql_update = "UPDATE product SET product_name = %s, product_price = %s, product_stock = %s, product_description = %s, product_image_aws = %s, product_image_azure = %s WHERE product_code = %s"
    result_num = cursor.execute(sql_update, (productName, productPrice, productStock, productDescription, 'ssgproduct/'+ s3_filename, azure_filename, num))
    
    cursor.close()
    con.close()

    return result_num

# 상품정보 삭제 - AWS
def deleteProductByCode(num):

    con = db_connect()
    cursor = con.cursor()

    sql_delete = 'DELETE FROM product WHERE product_code = %s'
    result_num = cursor.execute(sql_delete, num)

    cursor.close()
    con.close()

    return result_num

# 상품정보 삭제 - Azure
def deleteProductByCodeAzure(num):

    con = db_connect_azure()
    cursor = con.cursor()

    sql_delete = 'DELETE FROM product WHERE product_code = %s'
    result_num = cursor.execute(sql_delete, num)

    cursor.close()
    con.close()

    return result_num

# 유저 정보
def selectUsersAll(cloud_provider):
    # AWS
    if cloud_provider == 'AWS' :
        con = db_connect()
    # AZURE    
    else :
        con = db_connect_azure()

    cursor = con.cursor(cursor=pymysql.cursors.DictCursor)
    sql_select = "SELECT * FROM users WHERE user_role = 'role_user' ORDER BY user_idx ASC"
    cursor.execute(sql_select)
    
    result = []
    result = cursor.fetchall()
    
    cursor.close()
    con.close()

    return result

# 주문 정보
def selectOrdersAll(cloud_provider):
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
    """
    
    cursor.execute(sql_select)
    
    result = []
    result = cursor.fetchall()
    
    cursor.close()
    con.close()

    return result




            


