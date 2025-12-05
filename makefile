sql-up:
	@cd local_env && \
	docker-compose up -d
	
sql-down:
	@cd local_env && \
	docker-compose down

sql-cl:
	@cd local_env && \
	docker-compose run sql-client

data-ut:
	@cd ./data_producer/ && \
	. myenv/bin/activate && \
	python python_from_file_to_kafka.py --file users_transactions

data-t:
	@cd ./data_producer/ && \
	. myenv/bin/activate && \
	python python_from_file_to_kafka.py --file simple_transactions