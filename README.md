# LDAP → Keycloak → Telegram Bot → ELK → CI/CD

## Описание
- **OpenLDAP**: каталог пользователей в Docker.
- **Keycloak**: SSO + LDAP Federation.
- **Telegram Bot**: /list, /add, /del пользователей.
- **ELK**: централизованная агрегация логов.
- **CI/CD**: GitHub Actions для автоматического деплоя.

## Быстрый старт

1. **Зависимости**  
   - Docker & Docker Compose  
   - (macOS) `brew install python@3.10`  
   - (Ubuntu) `sudo apt install python3.10 python3-pip`

2. **Настройка**  
   ```bash
   cp .env.example .env
   # откройте .env и заполните свои пароли/токен/ID
