## cloud-starter-falcon

A python ReST API on the [Falcon](https://falconframework.org/) framework with a MongoDB datastore.

See the `doc/` directory for project setup and standard implementations.


## Running the project

### Environment variables

Required:

* `MONGO_URI`: a mongo connection string in URI format: `'mongodb://localhost:27017/'`

Optional:

* `LOG_MODE`: use `LOCAL` for human readable, colored, positional logging

### Commands

You can run this project locally by starting a MongoDB container (`build.sh` and `run.sh` in `datastore/mongo/docker`).

From a shell in `backend/cloud-starter-falcon/`

```
# Run this service in PD mode:
$ ./run.sh

# in local dev mode
$ ./run.dv.sh
```

## Running tests

This project uses the `pytest` package. To run all tests in `test/`:

```
$ pytest test
```

## Docker image management

The `build.sh` script provides build, run, teardown commands for simple iteration when revising the docker image

```
$ ./build.sh build    : build the docker image
$ ./build.sh run      : create and start a docker container from the image
$ ./build.sh teardown : stop the container and remove all build artifacts
```
