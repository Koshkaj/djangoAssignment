dev: create_makefile
	docker-compose -f ./docker-compose.yml up --build -d

create_makefile:
	echo "POSTGRES_NAME=dev" > ./app-backend/.env
	echo "POSTGRES_USERNAME=dev" >> ./app-backend/.env
	echo "POSTGRES_PASSWORD=mysecretpassword" >> ./app-backend/.env

CONTAINER_ID := $(shell docker ps -f "name=proexe_backend" -q)

test:
	@docker exec -it $(CONTAINER_ID) ./manage.py test -v 1

.PHONY: dev create_makefile test

