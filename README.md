# Ankinator
This repository contains the Ankinator backend. To run Ankinator, follow these steps:

- Install docker
- Insert your openai key into the .env file if you want to use the ChatGPT Model
- Inside the directory `extractor`, create a directory called `model_weights` and insert the model weights file (<model_name>.pt) from the teams share there. 
- Inside the directory `flashcard_model`, create a directory called `model_weights` and insert the folder with the model config from teams there.
- Run `docker-compose up` to start the application
- If you change code you just need to stop the containers and run the command again. If you add dependencies you have to rebuild the docker images with `docker-compose build`. You can rebuild images individually by using the command `docker-compose build <worker_name>`.
- Swagger UI is available under localhost:80/docs
- MongoDB UI is available under localhost:/8081

The following models are available for generating flashcards: ChatGPT, T5, LLaMA and VitGPT2.

IMPORTANT: The LLaMA model requires a lot of memory to run and if there is not enough memory the process will stop. 
