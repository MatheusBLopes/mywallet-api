PROJECT_NAME = $(shell pwd | rev | cut -f1 -d'/' - | rev)

runserver:
	poetry run python mywallet-api/manage.py runserver

build-image:
	docker build -t registry.heroku.com/mywallet/web .

push-image:
	docker push registry.heroku.com/mywallet/web

release:
	heroku container:release -a mywallet web

delete-last-image:
	docker rmi registry.heroku.com/mywallet/web

deploy:
	@make build-image
	@make push-image
	@make release

lint:
	poetry run pre-commit run --all-files

logs:
	heroku logs --tail -a mywallet

run-gunicorn:
	gunicorn -c gunicorn_config.py mywallet_api.wsgi:application

test:
	poetry run pytest -sx $(PROJECT_NAME) --reuse-db --create-db
