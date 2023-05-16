docker compose stop fastapi
docker compose rm fastapi
docker image rm fast-template-fastapi:latest
docker compose up fastapi -d
