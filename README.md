# Запуск

docker compose down -v

docker compose up --build

docker compose exec api alembic upgrade head
