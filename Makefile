all: install run test clean

install: venv
	. venv/bin/activate && pip install -r requirements.txt

venv:
	test -d venv || python3 -m venv venv

run:
	docker-compose up -d --build

test:
	docker-compose exec api pytest .

clean:
	rm -rf venv
	find -iname "*.pyc" -delete
