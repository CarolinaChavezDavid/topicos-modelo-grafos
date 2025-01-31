# topicos-modelo-grafos

## Project set up
1. Install FastAPI $ pip install "fastapi[standard]"
2. Memcached set up

TOPICOS-MODELO-GRAFOS/
│── app/
│   │── __init__.py
│   │── main.py             # Punto de entrada para FastAPI
│   │── authService.py      # Maneja la Autenticación
│   │── inferenceModel.py   # ML Model API
│   │── logService.py       # Loggea los request del usuario
│   │── database.py         # MongoDB and Memcached setup
│   │── models.py           # Pydantic models
│── .env
│── requirements.txt
│── Dockerfile
│── docker-compose.yml


# Service model
En este servicio se crea una funcion que carga el modelo y prepara las variables necesarias para procesar los request y entregar la lista con los ID's de los inmuebles similares. Se hace uso de LifeSpan Events de FastAPI para cargar el modelo cuando solo cuando se incia la aplicacion.