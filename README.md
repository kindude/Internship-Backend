# Internship Backend
To launch the project the docker is used. 
Firstly docker image is created using docker file configuration then to run the app the command docker run -p 8000:8000 my-fast-api is utilised, where
8000:8000 is local and external ports 
my-fast-api is a name of a docker image

To create migrations there were used several commands which were

alembic init alembic  -  used to initialize the Alembic migration environment in a directory called "alembic"

alembic revision --autogenerate -m "initial migration" - used to generate an automatic migration script

alembic upgrade head - used to apply any pending database migrations to the latest version defined in your Alembic migration environment.