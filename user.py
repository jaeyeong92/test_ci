from flask import *
import user_DAO
import login_DAO
import boto3
import uuid

bp = Blueprint("user", __name__, url_prefix="/user")

# AWS 자격 증명 및 S3 클라이언트 생성
session = boto3.Session()
s3 = session.client('s3')
S3_BUCKET = 'final-koupang-bucket'



def get_public_url(bucket_name, key) :
    # S3 객체에 대한 공개적인 URL 생성
    url = s3.generate_presigned_url(
        ClientMethod='get_object',
        Params={'Bucket': bucket_name, 'Key': key},
        ExpiresIn=3600  # URL의 유효기간 설정 (초 단위)
    )
    return url

@bp.route('/home')
def home() :
    
    return render_template('user/home.html')

# 회원가입
@bp.route('/userRegister', methods=['POST', 'GET'])
def userRegister() :
    if request.method == 'GET' :
        return render_template('user/userRegister.html')
    
    elif request.method == 'POST' :
        # 입력 받은 데이터 변수 설정
        userId = request.form['userId']
        userPw = request.form['userPw']
        userName = request.form['userName']
        userEmail = request.form['userEmail']
        userPhone = request.form['userPhone']
        userAddress = request.form['userAddress']

        user_DAO.insertUser(userId, userPw, userName, userEmail, userPhone, userAddress)
        return redirect(url_for('user.home'))

    else :
        return redirect(url_for('user.home'))
    
# ID 중복확인
@bp.route('/userIdCheck', methods=['GET'])
def userIdCheck() :
        userId = request.args.get('userId')
        result = user_DAO.checkUserId(userId)

        if result is None :
            return '1'
        else :
            return '0'
        
# E-mail 중복확인
@bp.route('/userEmailCheck', methods=['GET'])
def userEmailCheck() :
        userEmail = request.args.get('userEmail')
        result = user_DAO.checkUserEmail(userEmail)

        if result is None :
            return '1'
        else :
            return '0'
        
# PhoneNumber 중복확인
@bp.route('/userPhoneNumberCheck', methods=['GET'])
def userPhoneNumberCheck() :
        userPhone = request.args.get('userPhone')
        result = user_DAO.checkUserPhoneNumber(userPhone)

        if result is None :
            return '1'
        else :
            return '0'
    
# 회원 MyPage
@bp.route('/myPage', methods=['GET', 'POST'])
def myPage() :

    if 'loginSessionInfo' in session :
        userInfo = session.get('loginSessionInfo')

        return render_template('user/myPage.html', userInfo = userInfo)
    
    else :
        return render_template('user/home.html')
    
# 회원 MyPage 수정화면
@bp.route('/myPageEdit/<int:num>', methods=['GET', 'POST'])
def myPageEdit(num) :

    if 'loginSessionInfo' in session :
        userInfo = session.get('loginSessionInfo')

        if request.method == 'GET' :
            
            # 해당 글의 idx로 SELECT
            # select_result = blind_member_DAO.selectMemberByIdx(num)
            return render_template('user/myPageEdit.html', userInfo = userInfo)
        
        elif request.method == 'POST' :
            # 회원정보 수집 Form 정보 수집
            userId = request.form['userId']
            userPw = request.form['userPw']
            userName = request.form['userName']
            userEmail = request.form['userEmail']
            userPhone = request.form['userPhone']
            userAddress = request.form['userAddress']

            user_DAO.updateUserById(userId, userPw, userName, userEmail, userPhone, userAddress)

            # Session 갱신 후 user/home으로 redirect
            session['loginSessionInfo'] = login_DAO.selectUserById(userId)

            return redirect(url_for('user.home'))
        
    else :
        return render_template('user/home.html')
    
# 상품정보
@bp.route('/product', methods=['POST', 'GET'])
def product() :
    
    if 'loginSessionInfo' in session :
        if request.method == 'GET' :
            userInfo = session.get('loginSessionInfo')

            products = []
            products = user_DAO.selectProductAll()

            for product in products :
                imageName = product['product_image'][61:]
                newImageName = get_public_url(S3_BUCKET, imageName)
                product['product_image'] = newImageName

            return render_template('user/product.html', products = products, userInfo = userInfo)

        else :
            return render_template('user/home.html')
    else :
        return render_template('user/home.html')


# 장바구니에 담기 (Cart)
@bp.route('/addToCart', methods=['POST'])
def add_to_cart():

    cartUserId = request.form.get('cartUserId')
    cartProductCode = request.form.get('cartProductCode')
    
    # 장바구니에 상품 추가
    user_DAO.insertCartList(cartUserId, cartProductCode)
    
    return '장바구니에 담았습니다.'


# 장바구니(Cart) 리스트
@bp.route('/cartList', methods=['POST', 'GET'])
def cartList() :
    
    if 'loginSessionInfo' in session :
        if request.method == 'GET' :
            userInfo = session.get('loginSessionInfo')
            userId = userInfo.get('user_id')

            carts = user_DAO.selectCartListByUserId(userId)

            for cart in carts :
                imageName = cart['product_image'][61:]
                newImageName = get_public_url(S3_BUCKET, imageName)
                cart['product_image'] = newImageName

            return render_template('user/cartList.html', carts = carts, userInfo = userInfo)

        elif request.method == 'POST' :
            return render_template('user/home.html')
        
        else :
            return render_template('user/home.html')
    else :
        return render_template('user/home.html')
    
# 장바구니(Cart) 상품 삭제
@bp.route('/deleteCartList/<int:num>', methods=['POST'])
def deleteCartList(num) :

    result = user_DAO.deleteCartListByCode(num)
    
    if result :
        return '200'
    else :
        return '500'

# 특가/혜택 리스트
@bp.route('/specialBenefit', methods=['GET'])
def specialBenefit() :
    
    if 'loginSessionInfo' in session :
        if request.method == 'GET' :

            return render_template('user/specialBenefit.html')
        
        else :
            return render_template('user/home.html')
    else :
        return render_template('user/home.html')
    
# 회원 상품 검색
@bp.route('/searchProduct', methods=['POST'])
def searchProduct() :
    
    if 'loginSessionInfo' in session :
        if request.method == 'POST' :
            userInfo = session.get('loginSessionInfo')

            searchQuery = request.form['searchQuery']
            searchProducts = []
            searchProducts = user_DAO.selectProductForSearch(searchQuery)

            for searchProduct in searchProducts :
                imageName = searchProduct['product_image'][61:]
                newImageName = get_public_url(S3_BUCKET, imageName)
                searchProduct['product_image'] = newImageName

            return render_template('user/productBySearch.html', searchProducts = searchProducts, userInfo = userInfo, searchQuery = searchQuery)
        
        else :
            return render_template('user/home.html')
    else :
        return render_template('user/home.html')
    

# 결제
@bp.route('/pay', methods=['POST'])
def pay():

    if 'loginSessionInfo' in session :
        if request.method == 'POST' :
            # form에서 전송된 상품 코드들과 수량들을 받음
            userInfo = session.get('loginSessionInfo')
            userId = userInfo.get('user_id')
            unique_order_number = uuid.uuid4()

            # 주문 번호
            order_number = str(unique_order_number).replace('-', '')
            # 상품 번호
            order_product_code = request.form.getlist('product_code[]')
            # 상품 수량
            order_product_stock = request.form.getlist('product_count[]')
            # 상품 가격
            order_product_price = request.form.getlist('product_price[]')
            # 유저 ID
            order_user_id = request.form.getlist('product_userId[]')
            # 유저 이름
            order_user_name = request.form.getlist('product_userName[]')
            # 유저 주소
            order_user_address = request.form.getlist('product_userAddress[]')
            # 유저 휴대폰번호
            order_user_phone = request.form.getlist('product_userPhone[]')

            # 상품 코드와 수량을 묶어서 처리할 수 있음
            for code, stock, price, userid, username, useraddress, userphone in zip(order_product_code, order_product_stock, 
                                   order_product_price, order_user_id, 
                                   order_user_name, order_user_address, order_user_phone):
                # 각 상품 코드와 수량에 대한 처리 수행
                # 예: 주문 생성 및 데이터베이스에 저장
                user_DAO.insertOrdersList(order_number, code, stock, price, userid, username, useraddress, userphone)
                user_DAO.deleteCartListAll(userId)
            # 결제 완료 후 처리
            return redirect(url_for('user.product'))
        
        else :
            return render_template('user/home.html')
    else :
        return render_template('user/home.html')

# 장바구니창에서 수량변경 시, cart Table에 적용
@bp.route('/updateCartList', methods=['POST'])
def updateCartList():
    if 'loginSessionInfo' in session :
        if request.method == 'POST':
                userInfo = session.get('loginSessionInfo')
                userId = userInfo.get('user_id')

                product_code = request.form['productCode']
                new_quantity = request.form['newQuantity']
                
                print('product_code',product_code)
                print('newquantity', new_quantity)
                # 장바구니 업데이트 로직 수행
                # 예: user_DAO.updateCart(product_code, new_quantity)
                user_DAO.updateCartList(product_code, new_quantity, userId)
                
                return '장바구니가 업데이트되었습니다.'
        else:
            return '잘못된 요청입니다.'
    else :
        return render_template('user/home.html')    
   