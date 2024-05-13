$(function () {

    // 총 결제 금액
    updateProductPrice();

    // minusBtn 클릭 시
    $(".minusBtn").click(function () {
        let quantityInput = $(this).closest(".input-group").find(".quantityInput");
        let currentCount = parseInt(quantityInput.val());
        if (currentCount > 1) {
            quantityInput.val(currentCount - 1);
        } else {
            quantityInput.val(1);
        }
        updateTotalPrice($(this));
        updateProductPrice();
        updateCartList($(this));
    });

    // plusBtn 클릭 시
    $(".plusBtn").click(function () {
        let quantityInput = $(this).closest(".input-group").find(".quantityInput");
        let currentCount = parseInt(quantityInput.val());
        quantityInput.val(currentCount + 1);
        updateTotalPrice($(this));
        updateProductPrice();
        updateCartList($(this));
    });

    // 유저 장바구니 상품 삭제 Ajax 처리
    $('.delete-cart-product-btn').on('click', function(event) {
        event.preventDefault();

        // 상품 코드 가져오기
        const cartProductCode = parseInt($(this).data('cartProductCode'))
        const clickedButton = $(this); // 클릭된 버튼 요소 저장

        // 서버로 DELETE 요청 보내기
        $.ajax({
            url: `/user/deleteCartList/${cartProductCode}`,
            method: 'POST'
        }).done(function(result) {
            // 삭제 성공 시 해당 상품 삭제
            const productElement = clickedButton.closest('.col-md-12');
            if (productElement) {
                productElement.remove();
                updateProductPrice();
            }
        }).fail(function(error){
            console.error('There has been a problem with your AJAX request:', error);
        });
    });

    // Total Price 업데이트 함수
    function updateTotalPrice(button) {
        let productCard = button.closest(".card");
        let quantityInput = productCard.find(".quantityInput");
        let priceInput = productCard.find("[name='priceInput']");
        let totalPriceField = productCard.find(".totalPrice");

        const productCount = parseInt(quantityInput.val());
        const productPrice = parseInt(priceInput.val());
        const totalPrice = productCount * productPrice;
        totalPriceField.text(totalPrice.toLocaleString() + "원");
    }

    // 상품 가격 업데이트 함수
    function updateProductPrice() {
        let totalPriceSum = 0;
        
        $(".totalPrice").each(function () {
            let totalPriceText = $(this).text().replace(/[^\d]/g, ""); // 숫자를 제외한 모든 문자 제거
            let totalPrice = Number(totalPriceText);
            totalPriceSum += totalPrice;
        });

        let deliveryPrice = 3500 + totalPriceSum;
        
        $("#productPrice").text("상품 금액   " + totalPriceSum.toLocaleString() + "원");
        $("#resultProductPrice").text("결제예정금액   " + deliveryPrice.toLocaleString() + "원");
    }
});

// 장바구니 업데이트 함수
function updateCartList(btn) {
    const quantityInput = btn.parent().siblings('.quantityInput');
    const productCodeInput = btn.closest('.card').siblings('input[name="product_code[]"]');

    const productCountInput = productCodeInput.siblings('input[name="product_count[]"]');

    const productCode = productCodeInput.val();
    const newQuantity = parseInt(quantityInput.val());

    const formData = {
        productCode: productCode,
        newQuantity: newQuantity
    };

    // Ajax 요청 보내기
    $.ajax({
        url: '/user/updateCartList',
        type: 'POST',
        data: formData
    }).done(function(result){
        // 장바구니 업데이트 성공 시 처리할 내용
        console.log(result);
        productCountInput.val(newQuantity);
            
    }).fail(function(error){
        console.error('장바구니 업데이트 오류:', error);
    });
}