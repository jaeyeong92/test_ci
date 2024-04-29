// 왼쪽 Navbar Menu Active 처리 -> 활성화 된 메뉴 파란색으로 표시
document.addEventListener('DOMContentLoaded', function () {
    let navLinks = document.querySelectorAll('.nav-link');

    // 현재 URL
    let currentUrl = window.location.href;

    // 각 nav-link 요소에 대해 반복
    navLinks.forEach(function (link) {
        let linkUrl = link.href;

        // 현재 URL과 링크의 URL이 일치하는지 확인
        if (currentUrl === linkUrl) {
            link.classList.add('active');
        }
    });
});

document.addEventListener('DOMContentLoaded', function () {
    let menuItems = document.querySelectorAll('.menu-item.top');

    // 현재 URL
    let currentUrl = window.location.href;

    // 각 menu-item 요소에 대해 반복
    menuItems.forEach(function (item) {
        let itemUrl = item.href;

        // 현재 URL과 링크의 URL이 일치하는지 확인
        if (currentUrl === itemUrl) {
            item.classList.add('active');
        }
    });
});

document.addEventListener('DOMContentLoaded', function () {
    let menuItems = document.querySelectorAll('.navbar-top.icon');

    // 현재 URL
    let currentUrl = window.location.href;

    // 각 menu-item 요소에 대해 반복
    menuItems.forEach(function (item) {
        let itemUrl = item.parentElement.href;

        // 현재 URL과 링크의 URL이 일치하는지 확인
        if (currentUrl === itemUrl) {
            item.classList.add('active');
        }
    });
});

