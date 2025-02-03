# topicos-modelo-grafos

## Project set up
1. Install FastAPI $ pip install "fastapi[standard]"
2. Memcached set up

TOPICOS-MODELO-GRAFOS/
│── app/
│   │── __init__.py
│   │── main.py             # Punto de entrada para FastAPI
│   │── authService.py      # Maneja la Autenticación
│   │── modelService.py   # ML Model API
│   │── logService.py       # Loggea los request del usuario
│   │── database.py         # MongoDB and Memcached setup
│   │── models.py           # Pydantic models
│── .env
│── requirements.txt
│── Dockerfile
│── docker-compose.yml


TOPICOS-MODELO-GRAFOS/
│── auth-service/
│   │── app/
│   │   │── main.py
│   │   │── auth.py
│   │   │── models.py
│   │── Dockerfile
│── model-service/
│   │── app/
│   │   │── main.py
│   │   │── model.py
│   │   │── models.py
│   │── Dockerfile
│── log-service/
│   │── app/
│   │   │── main.py
│   │   │── logger.py
│   │── Dockerfile
│── api-gateway/
│   │── app/
│   │   │── main.py
│   │   │── routes.py
│   │── Dockerfile
│── db-service/
│   │── docker-compose.yml  # MongoDB and Memcached setup
│── docker-compose.yml
│── .env


# Service model
En este servicio se crea una funcion que carga el modelo y prepara las variables necesarias para procesar los request y entregar la lista con los ID's de los inmuebles similares. Se hace uso de LifeSpan Events de FastAPI para cargar el modelo cuando solo cuando se incia la aplicacion.

2. Registering Through the api-gateway
In this approach, clients interact only with the api-gateway (http://api-gateway:8000/register/), which forwards the request to the auth-service. This is the recommended approach in a microservices architecture.

Pros:
Single entry point: Clients interact only with the api-gateway, which simplifies client-side logic.

Centralized logic: You can add additional validation, logging, or transformations in the api-gateway before forwarding the request.

Security: Internal services like auth-service are not exposed directly to clients.

Scalability: You can easily add rate limiting, caching, or load balancing at the api-gateway level.