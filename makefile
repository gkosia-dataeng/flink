sql-up:
	@cd local_env && \
	docker-compose up -d
	
sql-down:
	@cd local_env && \
	docker-compose down

sql-client:
	@cd local_env && \
	docker-compose run sql-client

data:
	@cd ./data_producer/ && \
	. myenv/bin/activate && \
	python python_from_file_to_kafka.py 