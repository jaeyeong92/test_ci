from flask import *
import admin_DAO
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
from datetime import datetime
import json
from azure.storage.blob import BlobServiceClient, BlobClient
from azure.core.exceptions import AzureError, ResourceNotFoundError
import requests
import os
import logging
import random
import re

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

# 실행 환경 식별 ( AWS / Azure )
CLOUD_PROVIDER = os.environ.get("CLOUD_PROVIDER")
# CLOUD_PROVIDER = "AWS"
# CLOUD_PROVIDER = "AZURE"

# AWS/Azure DB 동기화
AWS_AZURE_INSERT_FLAG = True

# 샘플 상품 데이터
script_dir = os.path.dirname(os.path.abspath(__file__))
sample_products = [
    {
        "name": f"상품{i}",
        "price": random.randint(500, 20000) * 100,
        "stock": random.randint(1, 20),
        "description": f"상품{i}에 대한 설명",
        "image_path": os.path.join(script_dir, 'static', 'images', 'sampleImage', f'test{i}.png')
    } for i in range(1, 21)
]

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

# AWS S3 접근가능 테스트
def can_access_s3(S3_BUCKET):
    try:
        # 버킷 리스트 요청을 통해 접근 가능 여부 확인
        s3_client.head_bucket(Bucket=S3_BUCKET)
        return True
    except (NoCredentialsError, PartialCredentialsError, ClientError) as e:
        print(f"Failed to access S3 bucket {S3_BUCKET}: {e}")
        return False

# Azure Blob Storage 접근가능 테스트    
def can_access_azure_blob(account_url, container_name):
    try:
        # BlobServiceClient를 생성하여 Blob Storage에 접속
        blob_service_client = BlobServiceClient(account_url=account_url)

        # 컨테이너가 존재하는지 확인
        container_client = blob_service_client.get_container_client(container_name)
        container_properties = container_client.get_container_properties()

        # 컨테이너가 존재하면 접근 가능
        return True
    except ResourceNotFoundError:
        # 컨테이너가 없으면 접근 불가능
        return False
    except Exception as e:
        # 그 외의 예외 발생 시 처리
        print(f"Failed to access Azure Blob Storage: {e}")
        return False

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
                try :
                    # AWS
                    admin_DAO.insertProduct(productName, productPrice, 
                                            productStock, productDescription, 
                                            s3_filename, azure_filename)
                except Exception as e:
                    print("AWS DB Insert Failed: ", e)

                try:
                    # Azure
                    admin_DAO.insertProductAzure(productName, productPrice,
                                            productStock, productDescription, 
                                            s3_filename, azure_filename)
                except Exception as e:
                    print("Azure DB Insert Failed: ", e)

            # "AWS"일 때, S3에 업로드
            # if CLOUD_PROVIDER == "AWS" :
            if can_access_s3(S3_BUCKET):
                try:
                    s3_file.seek(0)
                    s3_client.upload_fileobj(s3_file, S3_BUCKET,'ssgproduct/' + s3_filename)
                    print("File uploaded successfully to S3.")
                except ClientError as e:
                    print(f"Failed to upload file to S3: {e}")
            else:
                print("S3 bucket is not accessible. File upload aborted.")

            # "AWS" / "AZURE"일 때, Azure Blob에 업로드
            if CLOUD_PROVIDER in ["AWS", "AZURE"]:
                try:
                    # 연결 문자열에서 AccountName과 DefaultEndpointsProtocol 추출
                    account_name_match = re.search(r"AccountName=([^;]+)", CONNECTION_STRING)
                    protocol_match = re.search(r"DefaultEndpointsProtocol=([^;]+)", CONNECTION_STRING)

                    if account_name_match and protocol_match:
                        account_name = account_name_match.group(1)
                        protocol = protocol_match.group(1)
                        azure_url = f"{protocol}://{account_name}.blob.core.windows.net"
                    else:
                        azure_url = None

                    print("Azure Blob Storage URL:", azure_url)
                    if not can_access_azure_blob(azure_url, CONTAINER_NAME):
                        print("Azure Blob Storage is not accessible. File upload aborted.")
                        # Azure Blob Storage에 접근할 수 없으면 더 이상 진행하지 않음
                        raise Exception("Azure Blob Storage is not accessible.")

                    blob_client = container_client.get_blob_client(azure_filename)
                    blob_client.upload_blob(azure_file_read, timeout=1)
                    print(f"{s3_filename} uploaded (UPDATE) to Azure Blob Storage.")
                except AzureError as e:
                    print(f"Failed to upload file to Azure Blob Storage: {e}")
                except Exception as e:
                    print(f"An unexpected error occurred: {e}")

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
                try :
                    admin_DAO.updateProductByCode(productName, productPrice, 
                                                productStock, productDescription, 
                                                s3_filename, azure_filename, num)
                except Exception as e:
                    print("AWS DB Insert Failed: ", e)

                # Azure
                try :
                    admin_DAO.updateProductByCodeAzure(productName, productPrice, 
                                                productStock, productDescription, 
                                                s3_filename, azure_filename, num)
                except Exception as e:
                    print("AWS DB Insert Failed: ", e)

            # "AWS"일 때, S3에 업로드
            # if CLOUD_PROVIDER == "AWS" :
            if can_access_s3(S3_BUCKET):
                try:
                    s3_file.seek(0)
                    s3_client.upload_fileobj(s3_file, S3_BUCKET,'ssgproduct/' + s3_filename)
                    print("File uploaded (UPDATE) successfully to S3.")
                except ClientError as e:
                    print(f"Failed to upload file to S3: {e}")
            else:
                print("S3 bucket is not accessible. File upload aborted.")

            # "AWS" / "AZURE"일 때, Azure Blob에 업로드
            if CLOUD_PROVIDER in ["AWS", "AZURE"]:
                try:
                    # 연결 문자열에서 AccountName과 DefaultEndpointsProtocol 추출
                    account_name_match = re.search(r"AccountName=([^;]+)", CONNECTION_STRING)
                    protocol_match = re.search(r"DefaultEndpointsProtocol=([^;]+)", CONNECTION_STRING)

                    if account_name_match and protocol_match:
                        account_name = account_name_match.group(1)
                        protocol = protocol_match.group(1)
                        azure_url = f"{protocol}://{account_name}.blob.core.windows.net"
                    else:
                        azure_url = None

                    print("Azure Blob Storage URL:", azure_url)
                    if not can_access_azure_blob(azure_url, CONTAINER_NAME):
                        print("Azure Blob Storage is not accessible. File upload aborted.")
                        # Azure Blob Storage에 접근할 수 없으면 더 이상 진행하지 않음
                        raise Exception("Azure Blob Storage is not accessible.")

                    blob_client = container_client.get_blob_client(azure_filename)
                    blob_client.upload_blob(azure_file_read, timeout=1)
                    print(f"{s3_filename} uploaded (UPDATE) to Azure Blob Storage.")
                except AzureError as e:
                    print(f"Failed to upload file to Azure Blob Storage: {e}")
                except Exception as e:
                    print(f"An unexpected error occurred: {e}")

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
    
    aws_result = False
    azure_result = False

    # AWS/AZURE 동시 삭제
    if AWS_AZURE_INSERT_FLAG :
        # AWS
        try :
            aws_result = admin_DAO.deleteProductByCode(num, CLOUD_PROVIDER)
        except Exception as e:
                    print("AWS DB Insert Failed: ", e)
        # Azure
        try :
            azure_result = admin_DAO.deleteProductByCodeAzure(num)
        except Exception as e:
                    print("AWS DB Insert Failed: ", e)

        if aws_result or azure_result:
            message = '상품이 성공적으로 삭제되었습니다.' if aws_result and azure_result else '상품이 일부만 삭제되었습니다.'
            print(message)
            return jsonify({'message': message}), 200
        else:
            return jsonify({'message': '상품 삭제에 실패했습니다.'}), 500

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

# 더미데이터 Setup
@bp.route('/setup', methods=['GET'])
def setup():
    try:
        for product in sample_products:
            # 이미지 파일 이름 준비
            today_datetime = datetime.now().strftime("%Y%m%d%H%M")
            s3_filename = f"{today_datetime}_{product['name']}.png"
            azure_filename = s3_filename

            # AWS S3에 업로드
            try:
                with open(product['image_path'], 'rb') as f:
                    s3_client.upload_fileobj(f, S3_BUCKET, f"ssgproduct/{s3_filename}")
                print(f"{s3_filename}을(를) S3에 업로드했습니다.")
            except (NoCredentialsError, PartialCredentialsError, ClientError) as e:
                print(f"{s3_filename}을(를) S3에 업로드하는 데 실패했습니다:", e)

            # Azure Blob Storage에 업로드
            try:
                with open(product['image_path'], 'rb') as f:
                    blob_client = container_client.get_blob_client(azure_filename)
                    blob_client.upload_blob(f, overwrite=True)
                print(f"{azure_filename}을(를) Azure Blob Storage에 업로드했습니다.")
            except AzureError as e:
                print(f"{azure_filename}을(를) Azure Blob Storage에 업로드하는 데 실패했습니다:", e)

            # DB INSERT
            # AWS
            try:
                admin_DAO.insertProduct(product['name'], product['price'], product['stock'], product['description'], s3_filename, azure_filename)
                print(f"{product['name']}을(를) 데이터베이스에 삽입했습니다.")
            except Exception as e:
                print(f"{product['name']}을(를) 데이터베이스에 삽입하는 데 실패했습니다:", e)

            # Azure
            try:
                admin_DAO.insertProductAzure(product['name'], product['price'], product['stock'], product['description'], s3_filename, azure_filename)
                print(f"{product['name']}을(를) 데이터베이스에 삽입했습니다.")
            except Exception as e:
                print(f"{product['name']}을(를) 데이터베이스에 삽입하는 데 실패했습니다:", e)

        return jsonify({"message": "샘플 상품 데이터 설정이 완료되었습니다."}), 200

    except Exception as e:
        return jsonify({"error g": str(e)}), 500      
