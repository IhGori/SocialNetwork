The backend was developed in Django with the purpose of simulating common actions and requests in a social network. This includes functionalities such as creating, updating, and removing users, adding friends, creating posts, managing likes and comments, as well as implementing a simultaneous chat feature. To ensure real-time communication, we use webhooks, which facilitate the exchange of information between the server and clients efficiently.

Furthermore, to guarantee the authenticity of requests, we have implemented the use of JSON Web Tokens (JWT). These tokens are generated during the authentication process and are used to securely transmit information between the involved parties, ensuring the integrity and authenticity of transactions performed within the system.

Link front-end: `https://github.com/IhGori/SocialNetwork-FRONTEND`

The application leverages the power of containerization to ensure seamless deployment and scalability. With Docker Compose version 3, we orchestrate multiple services encapsulated within individual containers, each serving a specific purpose in our social network application. The socialnetwork service hosts our main application, built using Vue.js and Django, facilitating smooth interactions between users. We rely on PostgreSQL (psql) and Redis (redis) containers to manage data storage and caching, ensuring efficient data handling and retrieval. Additionally, we utilize MinIO (minio) for object storage, enabling reliable storage and retrieval of media assets. By encapsulating each component within its own container, we achieve a modular and flexible architecture, allowing for easy deployment across different environments while maintaining consistency and reliability.

## Install
To make use of it, you'll need to create a .env file with the parameters used in the .env-example, as well as define the access key and secret key after gaining access to the MinIO bucket.

Run the command docker-compose up -d --build.

![image](https://github.com/IhGori/SocialNetwork-BACKEND-API/assets/73910233/3aab0e14-76f2-4e99-a192-84a95caa9214)


![image](https://github.com/IhGori/SocialNetwork-BACKEND-API/assets/73910233/467ecf0b-3581-4384-8cff-64962f53a6fa)


