from flask import *
import admin_DAO
import boto3
from datetime import datetime
import json
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import requests

bp = Blueprint("admin", __name__, url_prefix="/admin")

# AWS 자격 증명 및 S3 클라이언트 생성
session2 = boto3.Session()
s3_client = session2.client('s3')
S3_BUCKET = 'ssgpang-bucket'

# Azure Blob Storage 연결 설정
CONNECTION_STRING = ""
CONTAINER_NAME = "ssgpang-container"

# Blob 서비스 클라이언트 생성
blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)
container_client = blob_service_client.get_container_client(CONTAINER_NAME)

# Git
GIST_ID = "a9d6acbaf78e4d82a4dcf858ba3652ea"
GITHUB_TOKEN = ""

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
                imageName = product['product_image_aws']
                newImageName = get_public_url(S3_BUCKET, imageName)
                product['product_image_aws'] = newImageName

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
            s3_file = request.files['productImage']
            s3_filename = today_datetime + '_' + s3_file.filename
            azure_file = request.files['productImage']
            azure_filename = today_datetime + '_' + azure_file.filename
            
            # 업로드된 이미지의 S3 URL 생성
            # s3_url = f"https://{S3_BUCKET}.s3.ap-northeast-1.amazonaws.com/ssgproduct/{s3_filename}"
            
            # DB 저장
            admin_DAO.saveToDatabase(productName, productPrice, productStock, productDescription, s3_filename, azure_filename)
            # admin_DAO.saveToDatabaseAzure(productName, productPrice, productStock, productDescription, s3_url)

            # S3에 업로드
            s3_client.upload_fileobj(s3_file, S3_BUCKET,'ssgproduct/' + s3_filename)

            # Azure Blob Storage에 파일 업로드
            blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)
            container_client = blob_service_client.get_container_client(CONTAINER_NAME)

            # S3 객체 "전체"를 Azure Blob Storage에 복사    
            # s3_objects = s3_client.list_objects_v2(Bucket=S3_BUCKET, Prefix='ssgproduct/')
            # for obj in s3_objects.get('Contents', []):
            #     file_key = obj['Key']
            #     try:
            #         # S3 객체 다운로드
            #         file_obj = s3_client.get_object(Bucket=S3_BUCKET, Key=file_key)
            #         file_content = file_obj['Body'].read()

            #         # Azure Blob에 업로드
            #         blob_client = container_client.get_blob_client(file_key.split('/')[-1])
            #         blob_client.upload_blob(file_content)
            #         print(f"{file_key} uploaded to Azure Blob Storage.")
            #     except Exception as e:
            #         print(f"Error uploading {file_key}: {e}")

            # 현재 AWS S3에 업로드 한 파일을 Azure Blob Storage에 똑같이 복사
            try:
                # S3 객체 다운로드
                s3_obj = s3_client.get_object(Bucket=S3_BUCKET, Key=f'ssgproduct/{s3_filename}')
                file_content = s3_obj['Body'].read()

                # Azure Blob에 업로드
                blob_client = container_client.get_blob_client(azure_filename)
                blob_client.upload_blob(file_content)
                print(f"{s3_filename} uploaded to Azure Blob Storage.")
            except Exception as e:
                print(f"Error uploading {s3_filename}: {e}")

            # DB to JSON
            result = admin_DAO.dbToJson()
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

            # JSON 파일을 읽어옵니다.
            file_content = read_json(FILE_NAME)
            # GIST에 업로드
            # uploadJsonToGist(GIST_ID, FILE_NAME, FILE_CONTENT, GITHUB_TOKEN)

            # GitHub Gist를 업데이트합니다.
            if uploadJsonToGist(GIST_ID, "db_data.json", str(file_content), GITHUB_TOKEN):
                print("Updated GitHub Gist successfully.")
            else:
                print("Failed to update GitHub Gist.")

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
            s3_file = request.files['productImage']
            s3_filename = today_datetime + '_' + s3_file.filename
            azure_file = request.files['productImage']
            azure_filename = today_datetime + '_' + azure_file.filename

            # 업로드된 이미지의 S3 URL 생성
            # s3_url = f"https://{S3_BUCKET}.s3.ap-northeast-1.amazonaws.com/ssgproduct/{s3_filename}"
            
            # DB 저장
            admin_DAO.updateProductByCode(productName, productPrice, productStock, productDescription, s3_filename, azure_filename, num)

            # S3에 업로드
            s3_client.upload_fileobj(s3_file, S3_BUCKET,'ssgproduct/'+ s3_filename)

            # Azure Blob Storage에 파일 업로드
            blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)
            container_client = blob_service_client.get_container_client(CONTAINER_NAME)

            # S3 객체 "전체"를 Azure Blob Storage에 복사    
            # s3_objects = s3_client.list_objects_v2(Bucket=S3_BUCKET, Prefix='ssgproduct/')
            # for obj in s3_objects.get('Contents', []):
            #     file_key = obj['Key']
            #     try:
            #         # S3 객체 다운로드
            #         file_obj = s3_client.get_object(Bucket=S3_BUCKET, Key=file_key)
            #         file_content = file_obj['Body'].read()

            #         # Azure Blob에 업로드
            #         blob_client = container_client.get_blob_client(file_key.split('/')[-1])
            #         blob_client.upload_blob(file_content)
            #         print(f"{file_key} uploaded to Azure Blob Storage.")
            #     except Exception as e:
            #         print(f"Error uploading {file_key}: {e}")

            # 현재 AWS S3에 업로드 한 파일을 Azure Blob Storage에 똑같이 복사
            try:
                # S3 객체 다운로드
                s3_obj = s3_client.get_object(Bucket=S3_BUCKET, Key=f'ssgproduct/{s3_filename}')
                file_content = s3_obj['Body'].read()

                # Azure Blob에 업로드
                blob_client = container_client.get_blob_client(azure_filename)
                blob_client.upload_blob(file_content)
                print(f"{s3_filename} uploaded to Azure Blob Storage.")
            except Exception as e:
                print(f"Error uploading {s3_filename}: {e}")

            # DB to JSON
            result = admin_DAO.dbToJson()
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
                    "product_image_aws": item[4],
                    "product_image_azure": item[5]
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
    print(response.content)

    # 요청이 성공하면 True를 반환합니다.
    if response.status_code == 200:
        return True
    else:
        # 요청이 실패하면 False를 반환합니다.
        print("Failed to update GitHub Gist.")
        return False

# JSON 파일을 읽어옵니다.
def read_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

