# Data Flow Diagrams для Suggestion Box

## Контекстная диаграмма (Уровень 0)
```mermaid
graph TD
    U[Пользователь] -->|F1: Запросы API| API[API Gateway]
    M[Модератор] -->|F2: Модерационные действия| API
    API -->|F3: Данные предложений| SVC[Сервис предложений]
    SVC -->|F4: Запросы к данным| DB[(База данных)]

    classDef trustZone fill:#e1f5fe
    class U,M trustZone
    classDef internal fill:#f3e5f5
    class API,SVC,DB internal
```

## Логическая архитектура (Уровень 1)
```mermaid
graph LR
    U[Веб-клиент] -->|F5: HTTPS/TLS| LB[Load Balancer]
    LB -->|F6: HTTP| AUTH[Сервис аутентификации]
    LB -->|F7: HTTP| APP[Сервис предложений]
    AUTH -->|F8: JWT токены| APP
    APP -->|F9: SQL запросы| DB[(PostgreSQL)]
    APP -->|F10: Логи| LOG[Centralized Logging]

    classDef external fill:#ffebee
    class U external
    classDef boundary fill:#fff3e0
    class LB boundary
    classDef internal fill:#e8f5e8
    class AUTH,APP,DB,LOG internal
```

## Диаграмма процессов (Уровень 2)
```mermaid
flowchart TD
    Start[Начало] --> Auth[Аутентификация пользователя]
    Auth -->|F11: JWT токен| Validate[Валидация входных данных]
    Validate -->|F12: Очищенные данные| Create[Создание предложения]
    Create -->|F13: Новое предложение| SaveDB[Сохранение в БД]
    SaveDB -->|F14: ID предложения| LogCreate[Логирование создания]
    LogCreate -->|F15: Audit запись| Response[Ответ пользователю]

    ModStart[Модератор входит] --> ModAuth[Аутентификация модератора]
    ModAuth -->|F16: Модератор JWT| GetPending[Получение ожидающих предложений]
    GetPending -->|F17: Список предложений| Review[Просмотр предложения]
    Review --> Decision{Решение}
    Decision -->|Approve| UpdateApprove[Обновление статуса APPROVED]
    Decision -->|Reject| UpdateReject[Обновление статуса REJECTED]
    UpdateApprove -->|F18: Новый статус| LogModerate[Логирование модерации]
    UpdateReject -->|F18: Новый статус| LogModerate
    LogModerate -->|F19: Audit запись| Notify[Уведомление пользователя]

    classDef userProcess fill:#bbdefb
    classDef modProcess fill:#c8e6c9
    classDef dataStore fill:#f0f4c3
    class Auth,Validate,Create,SaveDB,LogCreate,Response userProcess
    class ModAuth,GetPending,Review,Decision,UpdateApprove,UpdateReject,LogModerate,Notify modProcess
    class SaveDB,LogCreate,LogModerate dataStore
```

## Границы доверия

- External - Клиенты (ненадежная зона)
- Boundary - Edge services (демилитаризованная зона)
- Internal - Бэкенд сервисы (доверенная зона)
- User Processes - Процессы обычного пользователя
- Moderator Processes - Процессы модератора (привилегированная зона)
