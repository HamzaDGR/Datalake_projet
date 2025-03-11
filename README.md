#installer les requirements (de preference dans un venv) 
pip install -r requirements.txt

#lancer le projet
docker-compose up --build -d

#installer pymongo dans le container airflow 
docker exec -it data-lake-opensky-airflow-worker-1 bash
pip install pymongo
#une fois fait
exit

#lancer navigateur et se connecter avec airflow airflow
http://localhost:8080/home

lancer le DAG => data_ingestion en cliquant sur trigger dag dans actions
Le travail est fait, le pipeline complet est executé
