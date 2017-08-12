## MongoDB

Create a [MongoDB](https://www.mongodb.com/) derived docker image containing an initialized contacts collection stored in a docker volume.


## Building

Scripts are provided in `docker/` for:

* `./build.sh`: build the docker image
* `./run.sh`: create/start a container from the new image
* `./teardown.sh`: stop the container and remove the container/image

## Strategy

The Dockerfile copies a contacts db initialization script to `/docker-entrypoint-initdb.d/` which is imported on container initialization. Data is stored in a docker volume which persists through container restarts.

The concept can also be used for integration and load testing to provide a subset of groomed live data.

NOTES:

* Data is stored in `test.contacts`
* No auth is implemented

## Viewing data

After `build.sh` and `run.sh`, you can connect to MongoDB on `localhost:27017` using [mongo-express](https://github.com/mongo-express/mongo-express) or, to the mongo shell in the docker container with:

```shell
$ docker run -it \
    --link mongo-sample-data:mongo \
    --rm mongo sh -c \
    'exec mongo "$MONGO_PORT_27017_TCP_ADDR:$MONGO_PORT_27017_TCP_PORT/test"'
MongoDB shell version v3.4.3
connecting to: mongodb://172.17.0.2:27017/test
MongoDB server version: 3.4.3
Welcome to the MongoDB shell.

# remaining startup comments omitted...

> db.contacts.findOne()
{
        "_id" : ObjectId("58fc2073a8544985c2a8a0f4"),
        "firstName" : "James",
        "lastName" : "Butt",
        "companyName" : "Benton, John B Jr",
        "address" : "6649 N Blue Gum St",
        "city" : "New Orleans",
        "county" : "Orleans",
        "state" : "LA",
        "zip" : "70116",
        "phone1" : "504-621-8927",
        "phone2" : "504-845-1427",
        "email" : "jbutt@gmail.com",
        "website" : "http://www.bentonjohnbjr.com"
}
> exit
bye
```

## Push to Docker Registry

These images are stored in the `releases` Nexus repo which does not allow re-deploy.

To store the image in our Nexus Docker Registry:

1. Connect your vpn to the CLC mgmt mesh
2. Re-tag the docker image to point the docker registry and contain our group name
    ```
    docker tag mongo-sample-data:3.4 nexus.pl.ctl.io:16001/io.clc/mongo-sample-data:3.4
    ```
3. Log in to the registry with your Nexus creds via command line
    ```
    ᐅ docker login nexus.pl.ctl.io:16001
    Username: <account>
    Password:
    Login Succeeded
    ```
3. Push the image
    ```
    ᐅ docker push nexus.pl.ctl.io:16001/io.clc/mongo-sample-data:3.4
    ```
