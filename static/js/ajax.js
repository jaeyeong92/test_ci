// 관리자 상품 삭제 Ajax 처리
$(function(){
    // 삭제 버튼 클릭 시
    $('.delete-product-btn').on('click', function(event) {
        event.preventDefault(); // 기본 동작(링크 이동) 방지

        // 상품 코드 가져오기
        const productCode = parseInt($(this).data('productCode'))
        const clickedButton = $(this); // 클릭된 버튼 요소 저장

        // 서버로 DELETE 요청 보내기
        $.ajax({
            url: `/admin/delete/${productCode}`,
            method: 'POST',
            contentType: 'application/json;charset=UTF-8'
        }).done(function(result) {
            // 삭제 성공 시 해당 상품 엘리먼트 숨기기 또는 제거하기
            const productElement = clickedButton.closest('.col-md-4');
            if (productElement) {
                productElement.fadeOut(1200);
            }
        }).fail(function(error){
            console.error('There has been a problem with your AJAX request:', error);
        });
    });
});

// 회원가입 시 중복 ID 체크
function userRegisterCheck(event){
    event.preventDefault();
    const userId = $('#userId').val();
    $.ajax({
        url : "/user/userIdCheck",
        type : "get",
        data : {"userId" : userId}
    }).done(function(result) {
        if(result === '1') {
            alert('사용 가능한 ID입니다')
            $('#idCheckHidden').val('1');
            checkSubmitForm()
        } else {
            alert('이미 사용중인 ID입니다')
            $('#idCheckHidden').val('0');
            checkSubmitForm()
        }
    }).fail(function(error){
        console.error('There has been a problem with your AJAX request:', error);
    });
}

// 회원가입 시 중복 Email 체크
function userEmailCheck(event){
    event.preventDefault();
    const userEmail = $('#userEmail').val();
    $.ajax({
        url : "/user/userEmailCheck",
        type : "get",
        data : {"userEmail" : userEmail}
    }).done(function(result) {
        if(result === '1') {
            alert('사용 가능한 E-mail입니다')
            $('#emailCheckHidden').val('1');
            checkSubmitForm()
        } else {
            alert('이미 사용중인 E-mail입니다')
            $('#emailCheckHidden').val('0');
            checkSubmitForm()
        }
    }).fail(function(error){
        console.error('There has been a problem with your AJAX request:', error);
    });
}

// 회원가입 시 중복 PhoneNumber 체크
function userPhoneNumberCheck(event){
    event.preventDefault();
    const userPhone = $('#userPhone').val();
    $.ajax({
        url : "/user/userPhoneNumberCheck",
        type : "get",
        data : {"userPhone" : userPhone}
    }).done(function(result) {
        if(result === '1') {
            alert('사용 가능한 전화번호입니다')
            $('#phoneNumberCheckHidden').val('1');
            checkSubmitForm()
        } else {
            alert('이미 사용중인 전화번호입니다')
            $('#phoneNumberCheckHidden').val('0');
            checkSubmitForm()
        }
    }).fail(function(error){
        console.error('There has been a problem with your AJAX request:', error);
    });
}

// 회원가입 Submit 활성화
function checkSubmitForm(){
    const idCheckHidden = $('#idCheckHidden').val();
    const emailCheckHidden = $('#emailCheckHidden').val();
    const phoneNumberCheckHidden = $('#phoneNumberCheckHidden').val();

    if(idCheckHidden == '1' && emailCheckHidden == '1' && phoneNumberCheckHidden == '1'){
        $('#submitBtn').prop('disabled', false);
    } else {
        $('#submitBtn').prop('disabled', true);
    }
}

// 상품 장바구니에 담기
$(function(){
    $('.add-to-cart').on('click', function(event) {
        event.preventDefault();

        // 해당 상품 코드
        const cartProductCode = $(this).data('cartProductCode')
        // 유저 ID
        const cartUserId = $(this).data('cartUserId')

        $.ajax({
            url: '/user/addToCart',
            method: 'POST',
            data: {'cartProductCode': cartProductCode, 'cartUserId': cartUserId}
        }).done(function(result) {
            alert(result)

        }).fail(function(error){
            alert('[Error] 다시 시도해주세요.')
        });
    });
});


