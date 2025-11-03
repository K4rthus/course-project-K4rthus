# STRIDE Анализ угроз для Suggestion Box

| Поток/Элемент | Угроза (STRIDE) | Риск | Контроль | Ссылка на NFR | Проверка |
|---------------|------------------|------|----------|---------------|----------|
| F1 /login | S: Spoofing - Подмена пользователя | R1 | Rate limiting + MFA | NFR-03 | Auth tests |
| F1 /login | T: Repudiation - Отказ от действий | R2 | Audit logs с user_id | NFR-10 | Audit tests |
| F3 Данные предложений | I: Information Disclosure - Утечка PII | R3 | Маскирование в логах | NFR-04 | Log review |
| F3 Данные предложений | D: DoS - Перегрузка сервиса | R4 | Rate limiting + автоскейлинг | NFR-01, NFR-08 | Load tests |
| F5 HTTPS/TLS | E: Eavesdropping - Перехват трафика | R5 | TLS 1.3 + сертификаты | NFR-04 | SSL labs test |
| F9 SQL запросы | T: Tampering - SQL инъекции | R6 | Prepared statements + ORM | NFR-09 | SAST/DAST |
| F8 JWT токены | S: Spoofing - Подделка токенов | R7 | Подпись токенов + короткий TTL | NFR-03 | Token validation |
| F10 Логи | I: Information Disclosure - Чувствительные данные | R8 | Маскирование PII | NFR-04 | Log audit |
| DB Хранилище | D: DoS - DoS атака на БД | R9 | Connection pooling + limits | NFR-07 | DB monitoring |
| APP Сервис | E: Elevation of Privilege - Неавторизованный доступ | R10 | RBAC + проверка прав | NFR-05 | AuthZ tests |
| F2 Модерация | R: Repudiation - Отказ от модерации | R11 | Подписанные audit logs | NFR-10 | Audit trail |
| F4 Запросы к данным | T: Tampering - Изменение статусов | R12 | Валидация прав доступа | NFR-05 | Integration tests |
| F6/7 HTTP | I: Information Disclosure - MITM атака | R13 | HTTPS enforcement | NFR-04 | Security headers |
| U Клиент | E: Elevation - XSS атаки | R14 | CSP headers + validation | NFR-09 | Security scan |
