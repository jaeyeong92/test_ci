// 관리자 상품 등록 유효성 검사
$(function(){
    // 등록 시 Form 전체 체크
    $('#registerForm').submit(function(event) {

        let errors = [];
        
        // 상품명 Check
        if($('#productName').val() !== '') {
            $('#productNameMessage').text('');
        } else {
            // 입력된 값이 없을 때
            $('#productNameMessage').text('상품명을 확인해주세요.').css('color','red');
            errors.push("Product name is required.");
        }

        // 상품가격 Check
        if($('#productPrice').val() !== '') {
            $('#productPriceMessage').text('');
        } else {
            // 입력된 값이 없을 때
            $('#productPriceMessage').text('상품가격을 확인해주세요.').css('color','red');
            errors.push("Product price is required.");
        }

        // 상품재고 Check
        if($('#productStock').val() !== '') {
            $('#productStockMessage').text('');
        } else {
            // 입력된 값이 없을 때
            $('#productStockMessage').text('재고를 확인해주세요.').css('color','red');
            errors.push("Product stock is required.");
        }

        // 상품설명 Check
        if($('#productDescription').val() !== '') {
            $('#productDescriptionMessage').text('');
        } else {
            // 입력된 값이 없을 때
            $('#productDescriptionMessage').text('상품설명을 확인해주세요.').css('color','red');
            errors.push("Product description is required.");
        }

        // 상품이미지 Check
        if($('#productImage').val() !== '') {
            $('#productImageMessage').text('');
        } else {
            // 입력된 값이 없을 때
            $('#productImageMessage').text('이미지를 선택해주세요.').css('color','red');
            errors.push("Product image is required.");
        }

        if (errors.length > 0) {
            // 폼 제출 방지
            event.preventDefault();
        } else {
            errors.clear()
        }
    });

    // 각 항목 별도 체크
    $('#productName, #productPrice, #productStock, #productDescription, #productImage').on('input', function() {
        const input = $(this);
        const messageElement = $(`#${input.attr('id')}Message`);
        if($(this).val() === '') {
            const labelText = $(this).closest('.form-group').find('label').text();
            messageElement.text(`${labelText}을(를) 확인해주세요.`).css('color', 'red');
        } else {
            messageElement.text('');
        }
    });
});

// 회원가입 시, ID 영문자/숫자만 허용
function checkReg(event) {
    const regExp = /[^0-9a-zA-Z.@]/g; // 숫자와 영문자만 허용
    const del = event.target;
    if (regExp.test(del.value)) {
      del.value = del.value.replace(regExp, '');
    }
  };

// 회원가입 시, 비밀번호 일치 체크
function passwordCheck(){
    const userPw1 = $('#userPw1').val();
    const userPw2 = $('#userPw2').val();
    if(userPw1 != userPw2){
        $('#pwCheckMessage').html('Password가 일치하지 않습니다.');
        $('#pwCheckMessage').css("color", "red")
    } else {
        $('#pwCheckMessage').html('');
        $('#userPw').val(userPw1);
    }
}





