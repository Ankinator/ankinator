# Ankinator

To run ankinator, follow these steps:
- Install docker
- Copy the .env file from the private env repository inside the ankinator root directory
- Run docker-compose up --force-recreate to start the application
- If you change code you just need to stop the containers and run the command again. If you add dependencies you have to rebuild the docker images.
- Swagger UI localhost:80/docs
- MongoDB UI localhost:/8081
