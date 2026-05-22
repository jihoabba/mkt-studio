let lottieAnimation;
let isLottieLoaded = false;

// Lottie 애니메이션 초기화
function initLottieAnimation() {
    return new Promise((resolve, reject) => {
        try {
            console.log("Initializing Lottie animation...");
            const container = document.getElementById("lottie-container");
            
            // 기존 애니메이션이 있다면 제거
            if (lottieAnimation) {
                lottieAnimation.destroy();
            }

            lottieAnimation = lottie.loadAnimation({
                container: container,
                renderer: "svg",
                loop: false,
                autoplay: false,
                path: "https://vos.line-scdn.net/ipx-mall/images/out/showcase/250605/animation.json"
            });

            // 애니메이션 로드 완료 이벤트
            lottieAnimation.addEventListener("DOMLoaded", function () {
                console.log("Lottie animation loaded successfully");
                container.classList.add("initialized");
                container.style.display = "none";
                isLottieLoaded = true;
                resolve();
            });

            // 애니메이션 에러 이벤트
            lottieAnimation.addEventListener("error", function (err) {
                console.error("Lottie animation error:", err);
                container.style.display = "none";
                reject(err);
            });

            // 애니메이션 완료 이벤트
            lottieAnimation.addEventListener("complete", function () {
                console.log("Lottie animation completed");
            });

        } catch (error) {
            console.error("Error initializing Lottie:", error);
            document.getElementById("lottie-container").style.display = "none";
            reject(error);
        }
    });
}

// 페이지 로드 시 Lottie 초기화
window.addEventListener("load", async function () {
    console.log("Window loaded, initializing Lottie...");
    try {
        await initLottieAnimation();
        console.log("Lottie animation initialized successfully");
    } catch (error) {
        console.error("Failed to initialize Lottie:", error);
    }
});

const items = [
    {
        name: "Gray",
        img: "https://vos.line-scdn.net/ipx-mall/images/out/showcase/250605/img/pc/noo_gray.png",
        chance: 700,
        reward: "Claw Machine Coin",
        popup: "https://vos.line-scdn.net/ipx-mall/images/out/showcase/250605/img/pc/popup_gray.png",
    },
    {
        name: "Blue",
        img: "https://vos.line-scdn.net/ipx-mall/images/out/showcase/250605/img/pc/noo_blue.png",
        chance: 100,
        reward: "minini-chu",
        popup: "https://vos.line-scdn.net/ipx-mall/images/out/showcase/250605/img/pc/popup_blue.png",
    },
    {
        name: "Pink",
        img: "https://vos.line-scdn.net/ipx-mall/images/out/showcase/250605/img/pc/noo_pink.png",
        chance: 1000,
        reward: "10% Discount Coupon",
        popup: "https://vos.line-scdn.net/ipx-mall/images/out/showcase/250605/img/pc/popup_pink.png",
    },
    {
        name: "Golden",
        img: "https://vos.line-scdn.net/ipx-mall/images/out/showcase/250605/img/pc/noo_golden.png",
        chance: 200,
        reward: "30% Discount Coupon",
        popup: "https://vos.line-scdn.net/ipx-mall/images/out/showcase/250605/img/pc/popup_golden.png",
    },
];

// 팝업 이미지 미리 로드
function preloadImages() {
    items.forEach((item) => {
        const img = new Image();
        img.src = item.popup; // 실제 경로 사용
    });
}

// 페이지 로드 시 이미지 미리 로드
window.addEventListener("load", preloadImages);

function pickWeightedItem() {
    const total = items.reduce((sum, item) => sum + item.chance, 0);
    const rand = Math.random() * total;
    let sum = 0;
    for (const item of items) {
        sum += item.chance;
        if (rand < sum) return item;
    }
}

function startRoulette() {
    const rotateImg = document.querySelector("#rotate-img");
    const rouletteBox = document.querySelector(".roulette-box");
    const startBtn = document.querySelector(".start-btn");
    const restartBtn = document.querySelector(".restart-btn");
    const goldenBrownImg = document.querySelector(".golden-brown-img");

    startBtn.style.pointerEvents = "none";
    restartBtn.style.display = "none";

    rotateImg.style.transition = "";
    rotateImg.style.transform = "";

    const animationDuration = 2500;
    let startTime = Date.now();
    let currentInterval = 100; // 초기 속도는 0.1초
    let lastChangeTime = startTime;
    let lastImage = null;

    const finalItem = pickWeightedItem();

    const animationInterval = setInterval(() => {
        const currentTime = Date.now();
        const elapsedTime = currentTime - startTime;

        const progress = elapsedTime / animationDuration;

        // 더 부드러운 감속을 위한 이징 함수
        const easeOut = 1 - Math.pow(1 - progress, 3);

        const minInterval = 100; // 최소 간격 0.1초
        const maxInterval = 300; // 최대 간격 0.3초
        const intervalRange = maxInterval - minInterval;

        // 감속 시작 시점을 더 일찍 시작하도록 조정
        const adjustedProgress = progress < 0.6 ? 0 : (progress - 0.6) / 0.4;
        const smoothEase = Math.sin((adjustedProgress * Math.PI) / 2);
        currentInterval = minInterval + intervalRange * smoothEase;

        if (currentTime - lastChangeTime >= currentInterval) {
            if (elapsedTime >= animationDuration - 200) {
                goldenBrownImg.setAttribute("href", finalItem.img);
            } else {
                const randomIndex = Math.floor(Math.random() * items.length);
                lastImage = items[randomIndex];
                goldenBrownImg.setAttribute("href", lastImage.img);
            }
            lastChangeTime = currentTime;
        }

        if (elapsedTime >= animationDuration) {
            clearInterval(animationInterval);

            // 0.5초 후에 결과 화면 표시
            setTimeout(() => {
                showResultImage(finalItem.popup);
            }, 500);
        }
    }, 16);
}

// 재시작 버튼 클릭 이벤트
document.querySelectorAll(".restart-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
        resetGame();
    });
});

// 시작 버튼 클릭 이벤트
document.querySelector(".start-btn").addEventListener("click", startRoulette);

// bubbly animation
document.querySelectorAll(".bubbly-button").forEach((button) => {
    button.addEventListener("click", (e) => {
        e.preventDefault();
        button.classList.remove("animate");
        void button.offsetWidth;
        button.classList.add("animate");
        setTimeout(() => {
            button.classList.remove("animate");
        }, 700);
    });
});

function showResultImage(imagePath) {
    const resultBox = document.querySelector(".result-box");
    const resultImage = resultBox.querySelector(".result-image img");
    const rouletteBox = document.querySelector(".roulette-box");
    const restartBtn = resultBox.querySelector(".restart-btn");
    const lottieContainer = document.getElementById("lottie-container");

    console.log("Showing result image and starting Lottie animation...");

    // Lottie 컨테이너 표시
    lottieContainer.style.display = "block";
    resultBox.classList.add("show");
    rouletteBox.style.opacity = "0";

    // result-box에 show 클래스가 추가된 후 Lottie 애니메이션 실행
    setTimeout(() => {
        if (lottieAnimation && isLottieLoaded) {
            console.log("Playing Lottie animation...");
            // 애니메이션을 처음부터 다시 시작
            lottieAnimation.goToAndStop(0, true);
            lottieContainer.classList.add("show");
            lottieAnimation.play();
        } else {
            console.error("Lottie animation not initialized or not loaded");
            // 애니메이션이 초기화되지 않았다면 다시 초기화 시도
            initLottieAnimation().then(() => {
                lottieAnimation.goToAndStop(0, true);
                lottieContainer.classList.add("show");
                lottieAnimation.play();
            });
        }
    }, 100);

    setTimeout(() => {
        rouletteBox.style.display = "none";
    }, 200);

    // 이미지 로드 후 결과 이미지 표시
    const img = new Image();
    img.onload = () => {
        resultImage.src = imagePath;
        restartBtn.style.display = "block";
    };
    img.src = imagePath;
}

function resetGame() {
    const resultBox = document.querySelector(".result-box");
    const rouletteBox = document.querySelector(".roulette-box");
    const rotateImg = document.querySelector("#rotate-img");
    const lottieContainer = document.getElementById("lottie-container");

    // Lottie 애니메이션 중지 및 컨테이너 숨기기
    if (lottieAnimation) {
        lottieAnimation.stop();
        lottieContainer.style.display = "none";
        lottieContainer.classList.remove("show");
    }

    resultBox.classList.remove("show");
    rouletteBox.style.display = "flex";
    rouletteBox.style.opacity = "1";
    rotateImg.style.transform = "rotate(0deg)";
    rotateImg.style.transition = "none";

    // 스타트 버튼 이벤트 리스너 재설정
    const startBtn = document.querySelector(".start-btn");
    startBtn.style.pointerEvents = "";
    startBtn.removeEventListener("click", startRoulette);
    startBtn.addEventListener("click", startRoulette);
}

$(function () {
    $(".fancy-button").mousedown(function () {
        $(this).bind("animationend webkitAnimationEnd MSAnimationEnd oAnimationEnd", function () {
            $(this).removeClass("active");
        });
        $(this).addClass("active");
    });
});