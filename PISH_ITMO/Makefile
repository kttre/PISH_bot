start:
	docker-compose down
	docker-compose build
	docker image prune -f
	docker-compose up
	python manage.py migrate
	python manage.py collectstatic --noinput
	python manage.py runserver
