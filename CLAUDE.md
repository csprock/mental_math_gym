# Mental Math Gym

Mental math practice using problem sets from different sources. 


## Architecture

Below is a very high-level archetecture of the application components: 

* Python-based classes for generating problem sets. 
* FastAPI REST API backend to serve the problem sets to the front-end. 
* SQLite database for tracking progress + SQLAlchemy ORM to facilitate later migrations to other RDBMS. 
* Simple JavaScript + HTML frontend client.
* Local version deployed via Docker and docker compose. 
* Future-proof front-end for creation of mobile application later. 

## Conventions

* Use a centralized logger module for each component. 

