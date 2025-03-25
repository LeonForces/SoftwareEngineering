workspace {
    model {
        // Пользователи
        developer = person "Разработчик" "Человек, занимающийся созданием, тестированием и поддержкой программного обеспечения."
        customer = person "Пользователь" "Конечный пользователь продукта, который взаимодействует с системой для решения своих задач" "Customer"
        admin = person "Администратор" "Управляет инфраструктурой системы: настраивает права доступа, обеспечивает безопасность, обновляет компоненты и устраняет технические сбои."

        // Основная система
        emailSystem = softwareSystem "E-Mail System" "Веб-сервис электронной почты" {
            apiGateway = container "API Gateway" "Маршрутизация запросов к сервисам. Аутентификация (проверка JWT). Логирование и мониторинг." "Python (FastAPI)" "API Gateway"
            mobileApplication = container "Mobile Application" "Нативное мобильное приложение с push-уведомлениями и офлайн-режимом" "Swift, Kotlin" "Mobile Client"
            webApplication = container "Web Application" "Отвечает за рендеринг писем, форм и настроек." "React.js" "Web Application" 
            emailService = container "Email Service" "Создание нового письма в папке. Получение всех писем в папке. Получение письма по коду (ID)." "Python (FastAPI)"
            folderService = container "Folder Service" "Создание новой почтовой папки. Получение перечня всех папок пользователя." "Python (FastAPI)"
            userService = container "User Service" "Создание нового пользователя. Поиск пользователя по логину. Поиск пользователя по маске имени и фамилии." "Python (FastAPI)"
        }

        // Внешние системы
        smptServer = softwareSystem "SMPT-сервер" "Отправка исходящих писем" "External system"
        imapServer = softwareSystem "IMAP-сервер" "Получение писем с внешних почтовых ящиков" "External system"
        oauthService = softwareSystem "OAuth сервис" "Сторонний сервис аутентификации" "External system"
        cloudStorage = softwareSystem "Облачное хранилище" "Хранилище для вложений" "External system"

        // Контекстные взаимодействия
        customer -> emailSystem "Использует для отправки/получения писем, Управления контактами, Настройки фильтров, Работы с вложениями"
        developer -> emailSystem "Разрабатывает и поддерживает: Новые функции, Исправление ошибок, Оптимизацию производительности"
        admin -> emailSystem "Администрирует: Инфраструктуру, Права доступа, Мониторинг, Резервное копирование"
        emailSystem -> smptServer "Асинхронная отправка исходящих писем, TLS шифрование, Retry политики"
        emailSystem -> imapServer "Синхронизация входящих писем, Периодический опрос, IDLE расширение"
        emailSystem -> oauthService "Federated Authentication, OAuth 2.0 flows, JWT валидация"
        emailSystem -> cloudStorage "Хранение вложений, Частичная загрузка, CDN интеграция"

        // Взаимодействие container
        customer -> mobileApplication "видит письма, почтовые папки пользователя используя"
        customer -> webApplication "видит письма, почтовые папки пользователя используя"
        mobileApplication -> apiGateway "выполняет вызов api через" "JSON/HTTPS"
        webApplication -> apiGateway "выполняет вызов api через" "JSON/HTTPS"
        apiGateway -> oauthService "проверяет токен через" "JSON/HTTPS"
        apiGateway -> emailService "создает письмо, получает письмо по ID, загружает вложения через" "JSON/HTTPS"
        apiGateway -> folderService "создает папки для писем, получает списки папок пользователя через" "JSON/HTTPS"
        apiGateway -> userService "регистрирует новых пользователей, поиск пользователей по логину или имени через" "JSON/HTTPS"
    }

    views {
        
        systemContext emailsystem {
            include *
            autoLayout
            description "Контекст и его взаимодействие с пользователями и системами"
        }

        container emailsystem {
            include *
            autoLayout
            description "Контейнер веб-сервиса электронной почты"
        }

        dynamic emailsystem "Dynamic" {
            autoLayout lr
            description "Последовательность действий пользователя при регистрации, создании папки и отправке письма."
            
            // Шаги сценария
            customer -> mobileApplication "Регистрация: вводит логин и пароль"
            mobileApplication -> apiGateway "POST /api/users"
            apiGateway -> userService "Сохранить пользователя"

            customer -> mobileApplication "Вход: вводит логин/пароль"
            mobileApplication -> apiGateway "POST /api/oauth/token"
            apiGateway -> oauthService "Сгенерировать JWT"

            customer -> mobileApplication "Создание папки: вводит название"
            mobileApplication -> apiGateway "POST /api/folders"
            apiGateway -> oauthService "Проверить токен"
            apiGateway -> folderService "Создать папку"

            customer -> mobileApplication "Отправка письма: заполняет форму"
            mobileApplication -> apiGateway "POST /api/emails"
            apiGateway -> oauthService "Проверить токен"
            apiGateway -> emailService "Сохранить письмо"
        }

        styles {
            element "Person" {
                color #ffffff
                fontSize 22
                shape Person
            }
            element "Web Application" {
                shape WebBrowser
            }
            element "Mobile Application" {
                shape MobileDeviceLandscape
            }
            element "Database" {
                shape Cylinder
            }
            element "Component" {
                background #85bbf0
                color #000000
            }
            element "Software System" {
                background #1168bd
                color #ffffff
            }
            element "Container" {
                background #438dd5
                color #ffffff
            }

            element "Customer" {
                background #08427b
            }
            element "External system" {
                background #dddddd
                color #ffffff
            }
        }
    }
}
