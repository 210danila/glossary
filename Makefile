install:
	python3 -m venv venv \
	&& source venv/bin/activate \
	&& pip install -r requirements.txt \
	&& python -m nltk.downloader wordnet

start:
	python app.py

migrate:
	touch database/glossary.db
	python database/migrations.py

backup:
	cp database/glossary.db database/glossary_backup.db

refresh:
	cp database/glossary.db database/glossary_backup.db
	rm database/glossary.db
	touch database/database.db
	python database/migrations.py

install-windows:
	python -m venv venv
	venv/Scripts/activate
	pip install -r requirements.txt
