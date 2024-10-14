let socket_yandex;
let socket_google;
let socket_mail;
let ids = [];
let id_yandex = 0;
let id_google = 0;
let id_mail = 0;
let count = $('#len_yandex').val(); // 33
let current = 0; // 16
let count_google = $('#len_google').val(); // 33
let count_mail = $('#len_mail').val(); // 33
let current_google = 0;
let current_mail = 0;

let timer_yandex;
let timer_google;
let res_yandex;
let res_google;
let res_mail;
let timer_mail;
let id_user = document.getElementById('id_user').value;

// Подключение WebSocket к серверам
socket_yandex = new WebSocket('ws://127.0.0.1:8000/ws');
socket_google = new WebSocket('ws://127.0.0.1:8000/google');
socket_mail = new WebSocket('ws://127.0.0.1:8000/mail');

function connectWebSocket() {
    socket_yandex.onopen = function (e) {
        console.log('WebSocket для Yandex открыт!');
        
        timer_yandex = setInterval(function () {
            if (socket_yandex.readyState === WebSocket.OPEN) {
                socket_yandex.send(JSON.stringify({
                    data: 'list', id_yandex: id_yandex, id_user: id_user
                }));
            }
        }, 100);

    };

    socket_yandex.onmessage = function (event) {
        try {
            let d = JSON.parse(event['data']);
            $('#yandex_block').append(d['message']);

            id_yandex = $('p[id="id_block"]').last().text();
            current += 1;
            res_yandex = Math.round(current / count * 100);

            $('#progress_bar').attr('aria-valuenow', res_yandex);
            $('#progress_bar').css('width', res_yandex + '%');
            $('#progress_bar').text(res_yandex + '%');

           if (res_yandex >= 100) {
                clearInterval(timer_yandex);
                console.log('Завершен процесс Yandex. Подключение Google...');

                // Проверяем состояние WebSocket для Google
                if (socket_google.readyState === WebSocket.OPEN) {
                    console.log('WebSocket для Google уже открыт!');
                    startGoogleTimer();  // Если открыт, начинаем отправку
                } else {
                    // Открытие WebSocket для Google и обработчик onopen
                    socket_google.onopen = function (e) {
                        console.log('WebSocket для Google открыт!');
                        startGoogleTimer();  // Начинаем отправку по таймеру
                    };
                }
            }
        } catch (e) {
            console.log('Error:', e.message);
        }
    };

    socket_google.onmessage = function (event) {
        try {

            console.log('Получены данные от Google');
            let d = JSON.parse(event['data']);
            //document.getElementById('google_block').innerHTML = d['message'];


            $('#google_block').append(d['message']);
            id_google = $('p[id="id_block_google"]').last().text();
            current_google += 1;
            res_google = Math.round(current_google / count_google * 100);
            $('#progress_bar_google').attr('aria-valuenow', res_google);
            $('#progress_bar_google').css('width', res_google + '%');
            $('#progress_bar_google').text(res_google + '%');
            if(res_google >= 100){

                clearInterval(timer_google);
                // Проверяем состояние WebSocket для Google
                if (socket_mail.readyState === WebSocket.OPEN) {
                    console.log('WebSocket для Mail уже открыт!');
                    startMailTimer();  // Если открыт, начинаем отправку
                } else {
                        // Открытие WebSocket для Google и обработчик onopen
                        socket_mail.onopen = function (e) {
                            console.log('WebSocket для Mail открыт!');
                            startMailTimer();  // Начинаем отправку по таймеру
                        };
                    }
                }
        } catch (e) {
            console.log('Error:', e.message);
        }
    };
     socket_mail.onmessage = function (event) {
        try {

            console.log('Получены данные от Mail');

            let d = JSON.parse(event['data']);
            console.log(d);
            $('#mail_block').append(d['message']);
            id_mail = $('p[id="id_block_mail"]').last().text();
            current_mail += 1;
            res_mail = Math.round(current_mail / count_mail * 100);
            $('#progress_bar_mail').attr('aria-valuenow', res_mail);
            $('#progress_bar_mail').css('width', res_mail + '%');
            $('#progress_bar_mail').text(res_mail + '%');
            if(res_mail>= 100){

                clearInterval(timer_mail);

            }
        } catch (e) {
            console.log('Error:', e.message);
        }
    };


    socket_yandex.onclose = function (e) {
        console.log('WebSocket для Yandex закрыт. Повторное подключение...');
    };

    socket_yandex.onerror = function (error) {
        console.log('WebSocket для Yandex ошибка: ' + error.message);
    };

    socket_google.onerror = function (error) {
        console.log('WebSocket для Google ошибка: ' + error.message);
    };

    socket_mail.onerror = function (error) {
        console.log('WebSocket для Mail ошибка: ' + error.message);
    };
}
function startGoogleTimer() {
    timer_google = setInterval(function () {
        if (socket_google.readyState === WebSocket.OPEN) {
            console.log(33);
            const message = JSON.stringify({
                data: 'list', id_google: id_google, id_user: id_user
            });
            console.log("Отправка сообщения на сервер Google WebSocket:", message);
            socket_google.send(message);
        }
    }, 100);
}
function startMailTimer() {
    timer_mail = setInterval(function () {
        if (socket_mail.readyState === WebSocket.OPEN) {
            const message = JSON.stringify({
                data: 'list', id_mail: id_mail, id_user: id_user
            });
            console.log("Отправка сообщения на сервер Mail WebSocket:", message);
            socket_mail.send(message);
        }
    }, 100);
}
connectWebSocket();


