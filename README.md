
* **car_crawloer:** Extract car data from some sites and store it in a postgre database, historicaly.

* **pedzap:** Extract data from pedZap API and save it in CSV or XLSX files, incrementally.





##### Docker - postgre database
```shell
docker run -d --name pg_local \
	-e POSTGRES_USER=root \
	-e POSTGRES_PASSWORD=root \
	-e POSTGRES_DB=local \
	-p 5432:5432 \
	postgres:13
```
