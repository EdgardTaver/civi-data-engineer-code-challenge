up:
	@ docker-compose -f devops/docker-compose.yml --project-name data-engineer-code-challenge  \
		up --build --remove-orphans --detach
	@ docker-compose -f devops/docker-compose.yml --project-name data-engineer-code-challenge  \
		logs

logs:
	@ docker-compose -f devops/docker-compose.yml --project-name data-engineer-code-challenge  \
		logs -f

sh: 
	@ docker-compose -f devops/docker-compose.yml --project-name data-engineer-code-challenge  \
		exec database sh

.DEFAULT_GOAL := help

help: ## prints this help
	@grep -h -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

install: ## installs python dependencies
	python3 -m pip install -r requirements.txt
	
run: ## run main dwh process
	python3 main.py

drop: ## drops dwh database
	python3 drop_dwh.py