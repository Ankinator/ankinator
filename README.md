# Ankinator
This repository contains the Ankinator backend. To run Ankinator, follow these steps:

- Install docker
- Insert your openai key into the .env file if you want to use the ChatGPT Model
- Inside the directory `extractor`, create a directory called `model_weights` and insert the model weights file (<model_name>.pt) from the teams share there. 
- Run `docker-compose up` to start the application
- If you change code you just need to stop the containers and run the command again. If you add dependencies you have to rebuild the docker images with `docker-compose build`. You can rebuild images individually by using the command `docker-compose build <worker_name>`.
- Swagger UI is available under localhost:80/docs
- MongoDB UI is available under localhost:/8081
