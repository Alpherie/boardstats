# boardstats
Statistics gathering for some imageboards


### Запуск

influxdb `docker-compose up --build influxdb`

Сборщик `docker-compose up --build b`
(Или иной, если он у вас настроен)

Тесты `pytest tests/testing.py`


### Настройка influxdb

1. Создайте пользователя с паролем, организацией и бакетом `2ch_hk` (это ж для харкача статистика), запишите реквизиты (бакет можно потом настраивать в Data->Buckets)
2. В Data->API Tokens создайте токены - для записи и для чтения.
3. В файле `get_data.py` вставьте токен для записи и имя организации (я когда-нибудь потом переделаю через секреты в докер-компосте)
4. В файле `compress_data` вставьте токен для чтения и имя организации, в крон файле проверьте бакет `2ch_hk`
5. В разделе Boards создайте дашборд с отображением статистики. Примеры запросов ниже

#### Запросы для дашборда инфлюкса

Потом добавлю 
 