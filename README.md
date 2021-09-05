## Preconditions:

- Python3, Pulumi, Helm, Docker, AWS cliv2

## Clone the project

```
git clone https://github.com/eugenestarchenko/crypto-api-demo.git
```

## Run local app

### Install

```
make install
```
or
```
make all
```
### Run server

```
make run
```

### Run tests

```
make test
```

## Run with docker

### Run server

```
docker-compose up -d --build
```

### Run tests

```
docker-compose exec api pytest .
```

## API documentation (provided by Swagger UI)

```
http://127.0.0.1:8000/docs
```

## EKS Cluster / ALB Ingress with Pulumi

Read [INFRA](infra/INFRA.md) to prepare app infrastructure.


## TL;DR

After EKS is up and running use helm chart to setup crypto-api-demo


```
cd $PWD/chart
helm install crypto-api-demo .
helm upgrade crypto-api-demo .
```

API is currently running on EKS.

ALB endpoint for testing purposes only
http://k8s-default-cryptoap-e3b7b4884b-375603982.us-east-1.elb.amazonaws.com/docs


```
curl -X 'GET' \
  'http://k8s-default-cryptoap-e3b7b4884b-375603982.us-east-1.elb.amazonaws.com/v1/currency?ticker=CAD' \
  -H 'accept: application/json'
```

## TODO (if have more time)

- Extend unit tests
- Include a `/metrics` ednpoint
- Setup RBAC and Github Actions Helm action for deployment
