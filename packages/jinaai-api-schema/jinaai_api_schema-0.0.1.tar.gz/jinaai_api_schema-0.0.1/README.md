# JinaAI Model Serving Core

## Overview

This is the core of the JinaAI Model Serving. It consists of two parts: 
- `api_schema`: the universal API schemas 
- `api_gateway`: the API gateway that serves the API schemas with respect to the backend services

## Installation

To install `jinaai-api-schema` package:

```bash
python setup.py --package schema install
```

To install `jinaai-api-gateway` package:

```bash
python setup.py --package gateway install
```

## Start the API Gateway

```bash 
$ uvicorn api_gateway:app --reload
```

### Fetch the OpanAPI schema

You can fetch the OpenAPI schema of the API by sending a GET request to the `/api/v1/openapi.json` endpoint:

```bash
$ curl http://localhost:8000/api/v1/openapi.json
```

### The API Reference

You can find the API references in the [API Reference](http://localhost:8000/docs) page. 
And also you can find the API references in the [readme.io](https://jina-api.readme.io/reference/) page.

