### Загрузка потокового видео через Selenium

Браузер грузит видео не сразу целиком, а короткими сегментами (порядка 10 сек), которые "пришивает" друг к другу. Так экономится время на скачивании и снижается нагрузка на сервер.

Под капотом технологии браузер загружает с сервера файл типа "m3u8", который и содержит всю иформацию о местоположении и порядке всех сегментов видео, которые должны воспроизводиться.

### Использованные библиотеки
- Selenium
- m3u8

### Источники
https://arnavbonigala.medium.com/download-any-video-from-the-web-bfc3931f0950