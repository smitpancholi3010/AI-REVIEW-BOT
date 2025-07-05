up:
	docker compose up --build

down:
	docker compose down

pull-model:
	docker exec -it ollama ollama pull codellama

review:
	curl -X POST http://localhost:8080/review \
	     -H "Content-Type: application/json" \
	     --data @review_payload.json | jq
