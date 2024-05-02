from flask import *
import admin_DAO
import boto3
import requests
from datetime import datetime
import json

bp = Blueprint("admin", __name__, url_prefix="/admin")

# AWS 자격 증명 및 S3 클라이언트 생성
session2 = boto3.Session()
s3_client = session2.client('s3')
S3_BUCKET = 'final-koupang-bucket'

def get_public_url(bucket_name, key) :
    # S3 객체에 대한 공개적인 URL 생성
    url = s3_client.generate_presigned_url(
        ClientMethod='get_object',
        Params={'Bucket': bucket_name, 'Key': key},
        ExpiresIn=3600  # URL의 유효기간 설정 (초 단위)
    )
    return url

# main 관리 페이지
@bp.route('/home')
def home() :

    # 관리자가 아닐 경우 user/home으로 redirect
    if 'loginSessionInfo' in session :
        userInfo = session.get('loginSessionInfo')
        if userInfo.get('user_role') != 'role_admin' :
            return redirect(url_for('user.home'))
        return render_template('admin/home.html')
    else :
        return redirect(url_for('login'))

# 상품정보
@bp.route('/product', methods=['POST', 'GET'])
def product() :

    if 'loginSessionInfo' in session :
        # 관리자가 아닐 경우 user/home으로 redirect
        userInfo = session.get('loginSessionInfo')
        if userInfo.get('user_role') != 'role_admin' :
            return redirect(url_for('user.home'))
        
        if request.method == 'GET' :

            products = []
            products = admin_DAO.selectProductAll()

            for product in products :
                imageName = product['product_image'][61:]
                newImageName = get_public_url(S3_BUCKET, imageName)
                product['product_image'] = newImageName

            return render_template('admin/product.html', products=products)
        
        elif request.method == 'POST' :
            # Form에서 입력한 id
            userId = request.form['userId']
            # Form에서 입력한 password
            userPw = request.form['userPw']

            # Form에서 입력한 id를 기반으로 DB 검색
            userResult = admin_DAO.selectMemberById(userId)

        else :
            return render_template('index.html')
    else :
        return redirect(url_for('login'))
    
# 상품 등록
@bp.route('/register', methods=['POST', 'GET'])
def register() :
    if 'loginSessionInfo' in session :
        # 관리자가 아닐 경우 user/home으로 redirect
        userInfo = session.get('loginSessionInfo')
        if userInfo.get('user_role') != 'role_admin' :
            return redirect(url_for('user.home'))
        
        if request.method == 'GET' :
            return render_template('admin/register.html')
        
        elif request.method == 'POST' :
            # 상품명
            productName = request.form['productName']

            # 상품가격
            productPrice = request.form['productPrice']

            # 상품재고
            productStock = request.form['productStock']

            # 상품설명
            productDescription = request.form['productDescription']

            # 상품이미지
            today_datetime = datetime.now().strftime("%Y%m%d%H%M")
            file = request.files['productImage']
            filename = today_datetime + '_' + file.filename

            # 업로드된 이미지의 S3 URL 생성
            s3_url = f"https://{S3_BUCKET}.s3.ap-northeast-1.amazonaws.com/furtniture/{filename}"
            
            # DB 저장
            admin_DAO.saveToDatabase(productName, productPrice, productStock, productDescription, s3_url)

            # S3에 업로드
            s3_client.upload_fileobj(file, S3_BUCKET,'furtniture/'+filename)

            # DB to JSON
            result = admin_DAO.dbToJson()
            objects = []
            for item in result:
                obj = {
                    "product_name": item[0],
                    "product_price": item[1],
                    "product_stock": item[2],
                    "product_description": item[3],
                    "product_image": item[4]
                }
                objects.append(obj)

            # 생성할 JSON 파일 설정
            FILE_NAME = "./db_data.json"
            f = open(FILE_NAME, 'w', encoding='utf-8')
            f.write(json.dumps(objects, ensure_ascii=False))
            f.close()

            return redirect(url_for('admin.product'))

        else :
            return render_template('index.html')
    else :
        return redirect(url_for('login'))
    
# 상품 수정
@bp.route('/edit/<int:num>', methods=['POST', 'GET'])
def edit(num) :

    if 'loginSessionInfo' in session :

        # 관리자가 아닐 경우 user/home으로 redirect
        userInfo = session.get('loginSessionInfo')
        if userInfo.get('user_role') != 'role_admin' :
            return redirect(url_for('user.home'))
        
        if request.method == 'GET' :
            selectResult = admin_DAO.selectProductByCode(num)
            return render_template('admin/edit.html', selectResult = selectResult)
        
        elif request.method == 'POST' :
            # 상품명
            productName = request.form['productName']

            # 상품가격
            productPrice = request.form['productPrice']

            # 상품재고
            productStock = request.form['productStock']

            # 상품설명
            productDescription = request.form['productDescription']

            # 상품이미지
            today_datetime = datetime.now().strftime("%Y%m%d%H%M")
            file = request.files['productImage']
            filename = today_datetime + '_' + file.filename

            # 업로드된 이미지의 S3 URL 생성
            s3_url = f"https://{S3_BUCKET}.s3.ap-northeast-1.amazonaws.com/furtniture/{filename}"
            
            # DB 저장
            admin_DAO.updateProductByCode(productName, productPrice, productStock, productDescription, s3_url, num)

            # S3에 업로드
            s3_client.upload_fileobj(file, S3_BUCKET,'furtniture/'+filename)

            # DB to JSON
            result = admin_DAO.dbToJson()
            objects = []
            for item in result:
                obj = {
                    "product_name": item[0],
                    "product_price": item[1],
                    "product_stock": item[2],
                    "product_description": item[3],
                    "product_image": item[4]
                }
                objects.append(obj)

            # 생성할 JSON 파일 설정
            FILE_NAME = "./db_data.json"
            f = open(FILE_NAME, 'w', encoding='utf-8')
            f.write(json.dumps(objects, ensure_ascii=False))
            f.close()

            return redirect(url_for('admin.product'))

        else :
            return render_template('index.html')
    else :
        return redirect(url_for('login'))
    
# 상품 삭제
@bp.route('/delete/<int:num>', methods=['POST'])
def delete(num) :

    if 'loginSessionInfo' in session :
        # 관리자일 경우에만 상품 삭제 가능
        userInfo = session.get('loginSessionInfo')
        if userInfo.get('user_role') == 'role_admin' :

            admin_DAO.deleteProductByCode(num)
            # return redirect(url_for('product'))
            # DB to JSON
            result = admin_DAO.dbToJson()
            objects = []
            for item in result:
                obj = {
                    "product_name": item[0],
                    "product_price": item[1],
                    "product_stock": item[2],
                    "product_description": item[3],
                    "product_image": item[4]
                }
                objects.append(obj)

            # 생성할 JSON 파일 설정
            FILE_NAME = "./db_data.json"
            f = open(FILE_NAME, 'w', encoding='utf-8')
            f.write(json.dumps(objects, ensure_ascii=False))
            f.close()

            if result:
                return jsonify({'message': '상품이 성공적으로 삭제되었습니다.'}), 200
            else:
                return jsonify({'message': '상품 삭제에 실패했습니다.'}), 500
    else :
        return redirect(url_for('login'))