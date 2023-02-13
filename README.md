To launch this project, simply do the commands :  
docker compose up -d db  
docker compose up -d  
If you want to launch it + get the logs : use docker compose up  
You first need to launch the database before launching the API. If you doesn't, the API initialization would fail (because it can't connect to the database).
