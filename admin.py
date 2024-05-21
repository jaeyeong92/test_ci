from flask import *
import admin_DAO
import boto3
from datetime import datetime
import json
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import requests
import os
import logging

# Blueprint 설정
bp = Blueprint("admin", __name__, url_prefix="/admin")

# Logging 설정
logging.basicConfig(filename='error.log', level=logging.ERROR)
logger = logging.getLogger()

# AWS Role 및 S3 클라이언트 생성
session2 = boto3.Session()
s3_client = session2.client('s3')
S3_BUCKET = 'ssgpang-bucket2'

# Azure Blob Storage 연결 설정
CONNECTION_STRING = os.environ.get("AZURE_CONNECTION_STRING")
# CONNECTION_STRING = ""
CONTAINER_NAME = "ssgpangcontainer"

# Blob 서비스 클라이언트 생성
blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)
container_client = blob_service_client.get_container_client(CONTAINER_NAME)

# Git
GIST_ID = "a9d6acbaf78e4d82a4dcf858ba3652ea"
GITHUB_TOKEN = os.environ.get("GIST_TOKEN")
# GITHUB_TOKEN = ""

# 실행 환경 식별 ( AWS / Azure )
CLOUD_PROVIDER = os.environ.get("CLOUD_PROVIDER")
# CLOUD_PROVIDER = "AWS"
# CLOUD_PROVIDER = "AZURE"

# AWS/Azure DB 동기화
AWS_AZURE_INSERT_FLAG = True

# AWS S3 Image URL
def get_public_url(bucket_name, key) :
    # S3 객체에 대한 공개적인 URL 생성
    url = s3_client.generate_presigned_url(
        ClientMethod='get_object',
        Params={'Bucket': bucket_name, 'Key': key},
        ExpiresIn=3600  # URL의 유효기간 설정 (초 단위)
    )
    return url

# Azure Blob Storage Image URL
def get_public_url_azure(container_name, blob_name):
    blob_client = BlobClient.from_connection_string(
        CONNECTION_STRING, container_name, blob_name
    )
    url = blob_client.url
    return url

# main 관리 페이지
@bp.route('/home')
def home() :
    # 관리자가 아닐 경우 user/home으로 redirect
    if 'loginSessionInfo' in session :
        userInfo = session.get('loginSessionInfo')
        if userInfo.get('user_role') != 'role_admin' :
            return redirect(url_for('user.product'))
        return redirect(url_for('admin.product'))
    else :
        return redirect(url_for('login'))

# 상품정보
@bp.route('/product', methods=['POST', 'GET'])
def product() :
    if 'loginSessionInfo' in session :
        userInfo = session.get('loginSessionInfo')
        # 관리자가 아닐 경우 user/home으로 redirect
        if userInfo.get('user_role') != 'role_admin' :
            return redirect(url_for('user.product'))
        
        products = []
        products = admin_DAO.selectProductAll(CLOUD_PROVIDER)

        for product in products :
            # AWS
            if CLOUD_PROVIDER == "AWS":
                imageName = product['product_image_aws']
                newImageName = get_public_url(S3_BUCKET, imageName)
                product['product_image_aws'] = newImageName
                logger.error(f"Generated AWS URL: {newImageName}")  # 로그 기록
            # Azure
            else :
                imageName = product['product_image_azure']
                newImageName = get_public_url_azure(CONTAINER_NAME, imageName)
                product['product_image_azure'] = newImageName
                    

        return render_template('admin/product.html', products = products, cloud_provider = CLOUD_PROVIDER)

    else :
        return redirect(url_for('login'))

# 상품 등록
@bp.route('/register', methods=['POST', 'GET'])
def register() :
    if 'loginSessionInfo' in session :
        userInfo = session.get('loginSessionInfo')
        # 관리자가 아닐 경우 user/home으로 redirect
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
            s3_file = request.files['productImage']
            s3_filename = today_datetime + '_' + s3_file.filename
            azure_file = request.files['productImage']
            azure_file_read = request.files['productImage'].read()
            azure_filename = today_datetime + '_' + azure_file.filename
            
            # DB 저장
            # AWS/AZURE 동시 저장
            if AWS_AZURE_INSERT_FLAG :
                # AWS
                admin_DAO.insertProduct(productName, productPrice, 
                                        productStock, productDescription, 
                                        s3_filename, azure_filename)
                # Azure
                admin_DAO.insertProductAzure(productName, productPrice, 
                                        productStock, productDescription, 
                                        s3_filename, azure_filename)
            # 단일 저장    
            else :
                # AWS
                if CLOUD_PROVIDER == 'AWS' :
                    admin_DAO.insertProduct(productName, productPrice, 
                                            productStock, productDescription, 
                                            s3_filename, azure_filename)
                # AZURE    
                else :
                    admin_DAO.insertProductAzure(productName, productPrice, 
                                            productStock, productDescription, 
                                            s3_filename, azure_filename)

            # "AWS"일 때, S3에 업로드
            if CLOUD_PROVIDER == "AWS" :
                s3_file.seek(0)
                s3_client.upload_fileobj(s3_file, S3_BUCKET,'ssgproduct/' + s3_filename)

            # "AWS" / "AZURE"일 때, Azure Blob에 업로드
            if CLOUD_PROVIDER in ["AWS", "AZURE"] :
                blob_client = container_client.get_blob_client(azure_filename)
                blob_client.upload_blob(azure_file_read)
                print(f"{s3_filename} uploaded to Azure Blob Storage.")

            # AWS/AZURE 동시 저장이 "아닐" 경우 DB 백업서버를 위한 DB Data JSON화 
            if AWS_AZURE_INSERT_FLAG == False :
                result = admin_DAO.dbToJson(CLOUD_PROVIDER)
                objects = []
                for item in result:
                    obj = {
                        "product_name": item[0],
                        "product_price": item[1],
                        "product_stock": item[2],
                        "product_description": item[3],
                        "product_image_aws": item[4],
                        "product_image_azure": item[5],
                    }
                    objects.append(obj)

                # 생성할 JSON 파일 설정
                FILE_NAME = "./db_data.json"
                f = open(FILE_NAME, 'w', encoding='utf-8')
                f.write(json.dumps(objects, ensure_ascii=False))
                f.close()

                # GitHub Gist를 업데이트합니다.
                file_content = read_json(FILE_NAME)
                if uploadJsonToGist(GIST_ID, "db_data.json", str(file_content), GITHUB_TOKEN):
                    print("Updated GitHub Gist successfully.")
                else:
                    print("Failed to update GitHub Gist.")

            return redirect(url_for('admin.product'))

        else :
            return redirect(url_for('login'))
    else :
        return redirect(url_for('login'))
    
# 상품 수정
@bp.route('/edit/<int:num>', methods=['GET', 'POST'])
def edit(num) :
    if 'loginSessionInfo' in session :
        userInfo = session.get('loginSessionInfo')
        # 관리자가 아닐 경우 user/home으로 redirect
        if userInfo.get('user_role') != 'role_admin' :
            return redirect(url_for('user.home'))
        
        if request.method == 'GET' :
            selectResult = admin_DAO.selectProductByCode(num, CLOUD_PROVIDER)
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
            s3_file = request.files['productImage']
            s3_filename = today_datetime + '_' + s3_file.filename
            azure_file = request.files['productImage']
            azure_file_read = request.files['productImage'].read()
            azure_filename = today_datetime + '_' + azure_file.filename

            # AWS/AZURE 동시 업데이트
            if AWS_AZURE_INSERT_FLAG :
                # AWS
                admin_DAO.updateProductByCode(productName, productPrice, 
                                            productStock, productDescription, 
                                            s3_filename, azure_filename, num)
                # Azure
                admin_DAO.updateProductByCodeAzure(productName, productPrice, 
                                            productStock, productDescription, 
                                            s3_filename, azure_filename, num)
            # 단일 업데이트
            else :
                # AWS
                if CLOUD_PROVIDER == 'AWS' :
                    admin_DAO.updateProductByCode(productName, productPrice, 
                                            productStock, productDescription, 
                                            s3_filename, azure_filename, num)
                # Azure
                else :
                    admin_DAO.updateProductByCodeAzure(productName, productPrice, 
                                            productStock, productDescription, 
                                            s3_filename, azure_filename, num)

            # "AWS"일 때, S3에 업로드
            if CLOUD_PROVIDER == "AWS" :
                s3_file.seek(0)
                s3_client.upload_fileobj(s3_file, S3_BUCKET,'ssgproduct/'+ s3_filename)

            # "AWS" / "AZURE"일 때, Azure Blob에 업로드
            if CLOUD_PROVIDER in ["AWS", "AZURE"] :
                blob_client = container_client.get_blob_client(azure_filename)
                blob_client.upload_blob(azure_file_read)
                print(f"{s3_filename} uploaded to Azure Blob Storage.")

            # AWS/AZURE 동시 저장이 "아닐" 경우 DB 백업서버를 위한 DB Data JSON화
            if AWS_AZURE_INSERT_FLAG == False :
                result = admin_DAO.dbToJson(CLOUD_PROVIDER)
                objects = []
                for item in result:
                    obj = {
                        "product_name": item[0],
                        "product_price": item[1],
                        "product_stock": item[2],
                        "product_description": item[3],
                        "product_image_aws": item[4],
                        "product_image_azure": item[5]
                    }
                    objects.append(obj)

                # 생성할 JSON 파일 설정
                FILE_NAME = "./db_data.json"
                f = open(FILE_NAME, 'w', encoding='utf-8')
                f.write(json.dumps(objects, ensure_ascii=False))
                f.close()

                # GitHub Gist를 업데이트합니다.
                file_content = read_json(FILE_NAME)
                if uploadJsonToGist(GIST_ID, "db_data.json", str(file_content), GITHUB_TOKEN):
                    print("Updated GitHub Gist successfully.")
                else:
                    print("Failed to update GitHub Gist.")

            return redirect(url_for('admin.product'))

        else :
            return redirect(url_for('login'))
    else :
        return redirect(url_for('login'))
    
# 상품 삭제
@bp.route('/delete/<int:num>', methods=['POST'])
def delete(num) :
    if 'loginSessionInfo' not in session:
        return redirect(url_for('login'))
    
    # 관리자일 경우에만 상품 삭제 가능
    userInfo = session.get('loginSessionInfo')
    if userInfo.get('user_role') != 'role_admin':
        return redirect(url_for('login'))
    
    # AWS/AZURE 동시 삭제
    if AWS_AZURE_INSERT_FLAG :
        # AWS
        aws_result = admin_DAO.deleteProductByCode(num)
        # Azure
        azure_result = admin_DAO.deleteProductByCodeAzure(num)

        if aws_result and azure_result:
            return jsonify({'message': '상품이 성공적으로 삭제되었습니다.'}), 200
        else:
            return jsonify({'message': '상품 삭제에 실패했습니다.'}), 500

    # AWS 삭제
    else :
        # AWS
        if CLOUD_PROVIDER == 'AWS' :
            result = admin_DAO.deleteProductByCode(num)
        else :
            result = admin_DAO.deleteProductByCodeAzure(num)
        
        # AWS/AZURE 동시 저장이 "아닐" 경우 DB 백업서버를 위한 DB Data JSON화 
        if AWS_AZURE_INSERT_FLAG == False :
            results = admin_DAO.dbToJson()
            objects = []
            for item in results:
                obj = {
                    "product_name": item[0],
                    "product_price": item[1],
                    "product_stock": item[2],
                    "product_description": item[3],
                    "product_image_aws": item[4],
                    "product_image_azure": item[5]
                }
                objects.append(obj)

            # 생성할 JSON 파일 설정
            FILE_NAME = "./db_data.json"
            f = open(FILE_NAME, 'w', encoding='utf-8')
            f.write(json.dumps(objects, ensure_ascii=False))
            f.close()

            # JSON 파일을 읽어옵니다.
            file_content = read_json(FILE_NAME)

            # GitHub Gist를 업데이트합니다.
            if uploadJsonToGist(GIST_ID, "db_data.json", str(file_content), GITHUB_TOKEN):
                print("Updated GitHub Gist successfully.")
            else:
                print("Failed to update GitHub Gist.")

        if result:
            return jsonify({'message': '상품이 성공적으로 삭제되었습니다.'}), 200
        else:
            return jsonify({'message': '상품 삭제에 실패했습니다.'}), 500
        
    
    
# JSON -> Github GIST 자동 업로드
def uploadJsonToGist(gist_id, file_name, file_content, github_token):
    # 업데이트할 Gist의 URL을 생성합니다.
    gist_url = f"https://api.github.com/gists/{gist_id}"

    # GitHub API를 사용하여 Gist를 업데이트합니다.
    data = {
        "files": {
            file_name: {
                "content": file_content
            }
        }
    }

    # GitHub API를 사용하여 Gist를 업데이트합니다.
    response = requests.patch(
        gist_url,
        headers={"Authorization": f"token {github_token}"},
        json=data
    )

    # 요청이 성공하면 True를 반환합니다.
    if response.status_code == 200:
        return True
    else:
        # 요청이 실패하면 False를 반환합니다.
        print("Failed to update GitHub Gist.")
        error_message = f"Failed to update GitHub Gist. Status code: {response.status_code}, Response body: {response.text}"
        print(error_message)
        return False

# JSON 파일 읽기
def read_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

# 고객 관리
@bp.route('/userInfo', methods=['GET'])
def userInfo() :
    if 'loginSessionInfo' in session :
        userInfo = session.get('loginSessionInfo')
        # 관리자가 아닐 경우 user/home으로 redirect
        if userInfo.get('user_role') != 'role_admin' :
            return redirect(url_for('user.home'))
        
        if request.method == 'GET' :
            users = []
            users = admin_DAO.selectUsersAll(CLOUD_PROVIDER)

            return render_template('admin/userInfo.html', users = users)

        else :
            return redirect(url_for('login'))
    else :
        return redirect(url_for('login'))
    

# 주문 관리
@bp.route('/orderInfo', methods=['GET'])
def orderInfo() :
    if 'loginSessionInfo' in session :
        userInfo = session.get('loginSessionInfo')
        # 관리자가 아닐 경우 user/home으로 redirect
        if userInfo.get('user_role') != 'role_admin' :
            return redirect(url_for('user.home'))
        
        if request.method == 'GET' :
            orders = []
            orders = admin_DAO.selectOrdersAll(CLOUD_PROVIDER)

            return render_template('admin/orderInfo.html', orders = orders)

        else :
            return redirect(url_for('login'))
    else :
        return redirect(url_for('login'))
