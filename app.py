from flask import *
from datetime import datetime
import admin
import user
import login_DAO
import pymysql

app = Flask(__name__)
app.secret_key = 'secret_key'

# Blueprint
app.register_blueprint(admin.bp)
app.register_blueprint(user.bp)

# index 페이지
@app.route('/')
def home() :
    
    # return render_template('index.html')
    return redirect('/login')

# 로그인
@app.route('/login', methods=['POST', 'GET'])
def login() :
    if request.method == 'GET' :

        return render_template('index.html')
    
    elif request.method == 'POST' :
        # ID
        userId = request.form['userId']
        # PW
        userPw = request.form['userPw']

        # Form에서 입력한 id를 기반으로 DB 검색
        userResult = login_DAO.selectUserById(userId)
        
        if userResult is not None :
            # Form에서 입력한 정보와 DB 정보 비교 후 일치하면 유저의 모든 정보를 Session에 저장
            if(userId == userResult['user_id'] and userPw == userResult['user_pw']) :
                session['loginSessionInfo'] = userResult
                userInfo = session.get('loginSessionInfo')
                # DB user_role에 따라 화면 분기
                if userInfo.get('user_role') == 'role_admin' :
                    return redirect(url_for('admin.home'))
                else :
                    return redirect(url_for('user.home'))
            else :
                return render_template('member/login_fail.html')
        else :
            return render_template('member/login_fail.html')
    else :
        return render_template('index.html')
    
# 로그아웃
@app.route('/logout')
def logout() :

    if 'loginSessionInfo' in session :
        session.pop('loginSessionInfo', None)
        return redirect(url_for('login'))
    else :
        return '<h2>User already logged out <a href="/login">Click here</a></h2>'
        #return '<h2>User already logged out !!!!! <a href="/login">Click here</a></h2>'
        
# main
if __name__ == '__main__' :
    app.run(debug=True, port=80, host='0.0.0.0')



