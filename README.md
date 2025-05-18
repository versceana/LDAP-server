# ChatOps LDAP Management

This project is a ChatOps-style system for managing an LDAP server through two interfaces:

* A **Telegram bot** for basic user and group management via commands.
* A **Spring Boot web application** (backend) for a graphical interface.

Both services communicate with an OpenLDAP server deployed via Docker.

---

## Architecture

All components run in Docker containers and are orchestrated using `docker-compose`.

### Services:

| Service        | Description                                      | Port   |
| -------------- | ------------------------------------------------ | ------ |
| `openldap`     | LDAP server (Bitnami OpenLDAP image)             | `1389` |
| `phpldapadmin` | GUI for LDAP inspection and testing              | `8081` |
| `backend`      | Java Spring Boot web app to manage LDAP          | `8080` |
| `bot`          | Telegram bot that provides ChatOps LDAP commands | `5000` |
| `nginx`        | Reverse proxy for `backend` and `bot` services   | `80`   |

---

## Features

### Telegram Bot

* `/list_users` — list all users
* `/add_user <uid> <password> [cn]` — add a new LDAP user
* `/del_user <uid>` — delete a user from LDAP
* `/set_role <uid> <group>` — assign a user to a group

### Web Application

* User-friendly web interface to:

  * View LDAP users
  * Add/remove users
  * Assign roles
  * Authenticate with LDAP

---

## Environment Variables

### `.env` for Telegram bot

```env
BOT_TOKEN=your_telegram_bot_token
LDAP_HOST=openldap
LDAP_PORT=1389
LDAP_ADMIN_DN=cn=admin,dc=example,dc=org
LDAP_ADMIN_PASSWORD=adminpassword
LDAP_BASE_DN=dc=example,dc=org
```

> Make sure this file is named `.env` and is mounted into the `bot` container.

---

## Quick Start

### 1. Clone the project

```bash
git clone 
cd chatops-ldap/infra
```

### 2. Create the `.env` file for the bot

```bash
cp ../bot/.env.example ../bot/.env
# Then edit with your actual Telegram bot token
```

### 3. Build and start all services

```bash
cd infra
docker-compose up --build
```

Wait until services are up. The bot will connect to Telegram, and backend will connect to LDAP.

---

## Access Points

* **Telegram bot** 
* **LDAP web interface (PHP LDAP Admin)** — [http://localhost:8081](http://localhost:8081)
* **Backend app** — [http://localhost:8080](http://localhost:8080)
* **Nginx entrypoint (if configured)** — [http://localhost](http://localhost)

---

## Technologies Used

* 🐍 Python 3.9 + Aiogram (Telegram bot)
* ☕ Java 23 + Spring Boot (backend)
* 📦 OpenLDAP (Bitnami)
* 🔸 PHP LDAP Admin
* 🐳 Docker & Docker Compose
* 🔐 LDAP3 Python library

---

## Project Structure

```
.
├── backend/               # Java Spring Boot app
├── bot/                   # Telegram bot (Python)
├── infra/                 # docker-compose, nginx, and LDAP schemas
│   └── docker-compose.yml
│   └── ldap/ldap.schema.ldif
│   └── nginx/nginx.conf
├── README.md
├── LICENSE
```

---

## Telegram Bot Commands

Make sure the bot is started and `/start`ed by you before using the following:

* `/list_users` — show LDAP users
* `/add_user john secret123 John Smith`
* `/del_user john`

---

## Troubleshooting

* If the bot shows `invalidCredentials`, verify that:

  * `LDAP_ADMIN_DN` matches your OpenLDAP config (`cn=admin,dc=example,dc=org`)
  * `adminpassword` matches the one in `docker-compose.yml`
* If `localhost:8080` is unavailable, check logs with:

```bash
docker logs chatops-backend
```

---

## License

MIT License. See `LICENSE` file for more details.