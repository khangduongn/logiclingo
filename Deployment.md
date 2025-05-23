# Deployment

## Prerequisite 
- Docker and Docker Compose must be installed 
    - Install here (https://docs.docker.com/engine/install/)
    - It is recommended that you deploy this on a Linux server for less overhead. It is possible to deploy this on other OS, but it will be more complicated and resource intensive. 
        - For example, to install Docker on Windows, you will need WSL2 or Hyper-V installed.
    - Note: Make sure Docker is properly set up and running before deploying the application
- [Git](https://git-scm.com/downloads) must be installed in your system
- Clone the Logiclingo's GitHub project from the prod branch to your system
    - NOTE: Do not clone from the main branch as that branch is not set up for production deployment
- Make sure your network settings for your server allow for public access of the logiclingo web app via port 80 (default port)

## How to Deploy
1. Use cd to navigate into the Logiclingo project until you reach the same directory as the manage.py, Dockerfile, and docker-compose.yml file. 
2. Run the command: ```sudo docker compose up --build```
    - Note: Root privilege might be needed depending on how Docker was set up on your system. Use ```sudo``` if root privilege is needed
3. As the image and containers are being built, take a look at the debug messages being printed to ensure that there are no errors. 
4. After the process finishes, run ```sudo docker ps``` in another terminal to get a list of running containers. Make sure that both the logiclingo-web and logiclingo-db containers are running. If not, then carefully examine the debug messages for the cause of the error.
5. The app is officially deployed, and now you can access the website via the exposed url of your server on port 80 (HTTP). You can change the port in the docker-compose.yml file by setting 'ports' to another port other than "80:80".
6. If you want to stop the application, run the command: ```sudo docker compose down```. This will stop the Docker containers that are running the application but won't delete any data saved to the database.
    - NOTE: If you want to stop the application and delete all data stored in the database, run the command: ```sudo docker compose down -v```
7. When you want to start the application again next time, you can just run the command: ```sudo docker compose up -d```.
    - NOTE: There are other flags you can set to get/store the logs from the containers.

## Customization
- To change the password of the logiclingo database, you can edit the docker-compose.yml file. Edit the DB_PASSWORD and POSTGRES_PASSWORD environment variables in the file to set a new password (Recommended). Restart the containers for the changes to take effect.
- You can also change other configurations in this file to fit your needs