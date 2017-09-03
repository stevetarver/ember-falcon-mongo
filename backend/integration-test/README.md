# Integration testing

Integration tests run against an established environment - no api/datastore setup is done here.

The tests are implemented as Postman environments and collections and run by `newman`. 

Smoke, Integration, and Regression tests are provided.

**TODO**: integration and regression are copies of smoke test - make them more robust.

## Environment setup

These tests may be run agains these environment configurations:

* API run in OS, mongo in a container
* API in a container, mongo in a container using docker compose
* Deployed to Kubernetes


## Smoke test

This api is small enough that we can perform a full integration test as a smoke test - although edge cases are currently missing.

