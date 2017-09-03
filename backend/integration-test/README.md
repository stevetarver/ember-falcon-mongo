# Integration testing

Integration tests run against an established environment - no api/datastore setup is done here.

The tests are implemented as Postman environments and collections and run by `newman`. 

Smoke, Integration, and Regression tests are provided.

**TODO**: integration and regression are copies of smoke test - make them more robust.

## Tool Installation

[newman](https://www.npmjs.com/package/newman) is a [nodejs](https://nodejs.org/en/) package providing a command line interface for running [Postman](https://www.getpostman.com/) collections.

If you don't have nodejs installed:

* Download the official installer [here](https://nodejs.org/en/download/)
* or, install it with Homebrew following [this guide](https://treehouse.github.io/installation-guides/mac/node-mac.html).

Once nodejs is installed, install the newman package:

```
$ npm install -g newman
```

## Environment setup

These tests may be run agains these environment configurations:

* API and mongo run on the OS
* API run on the OS, mongo in a container
* API in a container, mongo in a container using docker compose
* Deployed to Kubernetes
* etc.


## Smoke test

This api is small enough that we can perform a full integration test as a smoke test - although edge cases are currently missing.

