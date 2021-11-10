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