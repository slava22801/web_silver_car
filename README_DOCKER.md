# Docker Setup для Silver Car API

## Требования

- Docker
- Docker Compose

## Быстрый старт

### 1. Сборка и запуск контейнеров

```bash
docker-compose up -d --build
```

Это создаст и запустит:
- **web** - FastAPI приложение на порту 8001
- **mongodb** - MongoDB база данных на порту 27017

### 2. Проверка работы

Откройте браузер и перейдите на:
- API: http://localhost:8001
- API Docs: http://localhost:8001/docs
- MongoDB: localhost:27017

### 3. Остановка контейнеров

```bash
docker-compose down
```

### 4. Остановка с удалением данных

```bash
docker-compose down -v
```

## Переменные окружения

Для настройки подключения к базе данных используйте переменные окружения:

- `MONGODB_URL` - URL подключения к MongoDB (по умолчанию: `mongodb://localhost:27017/`)
- `MONGODB_DB_NAME` - Имя базы данных (по умолчанию: `silver_car`)

В docker-compose.yml эти переменные уже настроены для работы с контейнером MongoDB.

## Сборка образа вручную

```bash
# Сборка образа
docker build -t silver_car_api .

# Запуск контейнера
docker run -d \
  -p 8001:8001 \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/keys:/app/keys \
  -e MONGODB_URL=mongodb://mongodb:27017/ \
  -e MONGODB_DB_NAME=silver_car \
  --name silver_car_api \
  silver_car_api
```

## Просмотр логов

```bash
# Логи всех сервисов
docker-compose logs -f

# Логи только веб-сервиса
docker-compose logs -f web

# Логи только MongoDB
docker-compose logs -f mongodb
```

## Проверка состояния контейнеров

```bash
docker-compose ps
```

## Вход в контейнер

```bash
# Войти в контейнер веб-сервиса
docker-compose exec web bash

# Войти в контейнер MongoDB
docker-compose exec mongodb bash
```

## Важные директории

Следующие директории монтируются как volumes:
- `./uploads` - загруженные файлы (фото машин)
- `./logs` - логи приложения
- `./keys` - JWT ключи (должны быть созданы перед запуском)

## Безопасность

⚠️ **Важно:**
1. Убедитесь, что папка `keys/` содержит необходимые JWT ключи (private.pem и public.pem)
2. Не коммитьте файлы с секретами в git
3. Используйте переменные окружения для конфиденциальных данных

## Troubleshooting

### Проблема с подключением к MongoDB

Если веб-сервис не может подключиться к MongoDB:
1. Убедитесь, что оба контейнера запущены: `docker-compose ps`
2. Проверьте логи: `docker-compose logs mongodb`
3. Убедитесь, что в переменной окружения `MONGODB_URL` указано `mongodb://mongodb:27017/` (имя сервиса, не localhost)

### Проблема с правами доступа к файлам

Если возникают проблемы с правами доступа:
```bash
sudo chmod -R 755 uploads logs keys
```

### Пересборка образа

Если изменили зависимости:
```bash
docker-compose build --no-cache
docker-compose up -d
```

