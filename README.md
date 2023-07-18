# Ankinator

To run ankinator, follow these steps:
- Install docker
- Copy the .env file from the private env repository inside the ankinator root directory
- Inside the directory `extractor`, create a directory called `model_weights` and insert the model weights file (<model_name>.pt) from the teams share there. 
- Run `docker-compose up` to start the application
- If you change code you just need to stop the containers and run the command again. If you add dependencies you have to rebuild the docker images with `docker-compose build`. You can rebuild images indivudally by using the command `docker-compose build <worker_name>`.
- Swagger UI localhost:80/docs
- MongoDB UI localhost:/8081
