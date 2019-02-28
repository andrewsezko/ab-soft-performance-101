# PROJECT STARTUP GUIDE

## Prerequisites
- Install Docker [MacOS](https://docs.docker.com/docker-for-mac/install/),[Windows](https://docs.docker.com/docker-for-windows/install/)
- [Git](https://help.github.com/en/articles/set-up-git) 
- Python IDE [PyCharm](https://www.jetbrains.com/pycharm/download/) (optional) or your favorite text editor

## Description
This project is a set of simple services, which partially represent common logic elements of e-commerce systems.
It contains 3 Dockerized python apps:
- Authentication service
- Product service
- Cart service

All servers config could be managed through docker-compose.yml file in the project root (See ENVIRONMENT VARIABLES)

#### Authentication service
##### Methods
- `GET /api/auth/generate_token`
- `GET /api/auth/validate_token/<string:token_id>`

###### Note:
>For tracking user activities, the system uses token, which could be generated with GET /api/auth/generate_token.
Requests to all other services without token would fail.


#### Product service
##### Methods
- `GET /api/products/get_all`
- `GET /api/products/get_product/<string:product_id>`


#### Cart service
##### Methods
- `GET /api/cart/get_items`
- `GET /api/cart/add_item/<string:product_id>`
- `GET /api/cart/checkout`


## Configuration

#### Environment variables

To emulate service slowness use these two parameters in docker-compose file.

- `SLOWDOWN_SERVICE_MS_MIN` - min time of method execution
- `SLOWDOWN_SERVICE_MS_MAX` - max time of method execution

Slowdown value will be generated randomly in range (_SLOWDOWN_SERVICE_MS_MIN, SLOWDOWN_SERVICE_MS_MAX_)

Endpoint addresses configuration could be done through `*_SERVER_PORT` and `*_SERVER_HOST` respectively.
All endpoints are mapped on each other. By default next ports are used: 
- Product service port: **7777**
- Authentication service port: **7778**
- Cart service port: **7779**

###### Note:
> If you are going to change port mappings, pay attention to exposed ports in docker-compose.yml, they should be changed also.

## Running the app
1. Run the docker engine on your host.
2. Git clone this project from GitHub.
3. Use following commands: 

All commands should be executed from the project root directory.
Startup command:
```
docker-compose up -d
```
###### Note:
>Command above will run docker containers in detached mode. To view console output from all containers just don\`t add `-d` flag 

To restart all services run:
```
docker-compose restart
```

To recreate all services run:
```
docker-compose down
```

List containers
```
docker ps -a
```
Quick look to container output:
```
docker logs $docker_container_name
```

###### Note:
>Other useful Docker commands could be found in official [docs](https://docs.docker.com/engine/reference/commandline/cli/)

All services could be run without Docker. 
If you familiar with Python you can run all Flask servers from cmd or from Python IDE (eg. PyCharm).
All configurations should be performed directly in each server *.py file then. 
By default all servers will run with the same config as described in docker-compose.yml
