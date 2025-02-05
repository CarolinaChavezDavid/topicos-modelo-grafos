# topicos-modelo-grafos
Este proyecto es una aplicación basada en microservicios que utiliza un modelo de aprendizaje automático (ML) de grafos de conocimiento. El sistema está diseñado para devolver una lista con los IDs de 10 grafos que representan inmuebles similares dado un `head_id` (un identificador único de una propiedad). La arquitectura está construida utilizando FastAPI para los servicios de backend, Docker para el uso y manejo de contenedores y Docker Compose para la orquestación.

El proyecto está dividido en múltiples microservicios, cada uno manejando una funcionalidad específica:

* **API Gateway:** Actúa como el punto de entrada para todas las solicitudes y las dirige a los microservicios correspondientes.
* **Authentication Service:** Maneja la autenticación de usuarios y la limitación de solicitudes.
* **Model Service**: Aloja el modelo de ML y proporciona la lista de inmuebles similares basadas en un `head_id` proporcionado.
* **Logging Service:** Registra todas las solicitudes con sus tiempos de procesamiento.

* **Base de Datos:**  se utiliza MongoDB para los datos de usuario y Redis para almacenamiento en cache de las respuestas del modelo y limitación del número de requests. Por último Memcached fue utilizado para guardar en cache los logs.

### Estructura del proyecto

![topicos2 drawio (1)](https://github.com/user-attachments/assets/fd0b0b37-8228-4b5c-abed-68bd08cf851c)

Los servicios utilizados se establecieron por funcionalidades, las cuales estan dadas por el dominio del problema. Por otro lado las diversas bases de datos o sistemas de almacenamiento fueron elegidos para poner en practica su implementación ya que un solo sistema de almacenamiento se podría utilizar para toda la aplicación.

## Project set up
Como prerequisitios se debe tener instalado Docker y Docker compose.

1. Clonar o descargar el proyecto  
2. Ejecutar el comando:
```
docker-compose up --build
```
> En caso de error al ejecutar el comando revisar los logs de los servicios y revisar que los puertos utilizados en los servicios descritos en el docker-compose.yml esten disponibles.

# API Getaway
El `API Gateway`  es un microservicio basado en FastAPI que funciona como punto central para manejar las solicitudes de los usuarios. La razon principal  de utilizar  este servicio es que los clientes interactuen unicamente con este, centralizando la logica y ayudando a la escalabilidad ya que cualquier nuevo servicio o request que se agregue puede ser facilmente registrado (log) validado (authorization) y limitado(rate Limited).
El **API Gateway** se comunica con los otros microservicios usando  HTTP con `httpx.AsyncClient` que ayuda que los request no sean bloqueantes. Además, aunque cada servicio maneja los posibles errores generando mensajes especificos para posibles casos, este servicio agrega una capa extra para manejar el error en caso de que exista alguna falla en la conexión con los servicios.

## Workflow
 ### 1. Health Check 
La api cuenta con un endpoint (getTestAPI en la colección de Postman) que retorna un mensaje de éxito, ayuda a determinar que el proyecto se ejecuto de manera correcta.
  * **Endpoint:** `http://localhost:8000`
  * **Response:**
```
{
    "message": "API Gateway esta funcionando!"
}
```
 ### 2. Registro de usuario
Los usuarios antes de realizar una petición para obtener el resultado del modelo de grafos debe registrarse con el endpoint de registro (userRegistration en la colección de Postman) y así obtener una `api_key` única que es obligatoria para poder hacer request al modelo y revisar los logs. En el body del request deberá asignarse un nombre de usuario `username` y un tipo de cuenta `acount_type` de tipo **FREEPREMIUM** o **PREMIUM**
 * **Endpoint:** `http://localhost:8000/register/`
 * **Body:**
```
{
    "username": "CaroTest",
    "account_type": "FREEMIUM"
}
```

 * **Response:**
    
```
{
    "message": "Usuario registrado exitosamente.",
    "api_key": "05cf974aefd7da50eca33ccd891ae06edf4ccd9f7718a83552a70e5947cfb44d"
}
```

![userRegister](https://github.com/user-attachments/assets/835b47ae-1126-4ff8-a407-cba1cae5c259)

 ## 3. Consultar al modelo de grafos
 La API permite realizar peticiones al modelo de machine learning a través del endpoint que se comunica con el `model-service` (getSimilars en la colección de Postman).  
### Requisitos para la Solicitud  
Para realizar una solicitud, es necesario:  
- Incluir la **`api_key`** en el header, dentro del parámetro `Authorization`, obtenida durante el registro.  
- Proporcionar el **`head_id`** del grafo del cual se desean obtener los 10 IDs de los grafos más similares, según el procesamiento del modelo.  

### Funcionamiento Interno del API Gateway
   1. **Validación de la API Key**  
    - El API Gateway valida con el `auth-service` si la clave proporcionada en el encabezado existe en la base de datos (MongoDB).  
   2. **Verificación del Límite de Peticiones**  
    - Según el **`account_type`** del usuario asociado a la `api_key` entregada, se determina la cantidad de solicitudes permitidas por minuto:  
      - **FREEMIUM**: 5 peticiones por minuto.  
      - **PREMIUM**: 50 peticiones por minuto.  
    - Para este control, se utiliza **Redis**, donde se registra el número de solicitudes realizadas en un minuto.  
   3. **Procesamiento de la Solicitud**  
    - Si el usuario cumple con los requisitos anteriores, el **API Gateway** reenvía la petición al **`model_service`**, que procesa la solicitud y devuelve el resultado.  
  4. **Manejo de Errores**  
    - Durante cada etapa del proceso, se implementa un adecuado manejo de errores.  
    - En caso de fallos, se proporcionan respuestas claras indicando la causa del error.

 * **Endpoint:** `http://localhost:8000/similars/{head_id}` (ej: [334785, 252582, 301978, 304516, 327025, 280052, 309811, 294461])
 * **Header:** key:`Authorization`,  value:`api_key`

 * **Response:**
```
{
    "head_id": 326006,
    "similar_items": [
        384323,
        326006,
        359277,
        333006,
        298159,
        345471,
        335972,
        267264,
        306843,
        401661
    ]
}
```

![modelRequest](https://github.com/user-attachments/assets/0fee34ba-1bf1-41ae-9e10-7efd2226e55f)

### 4. Consulta de logs
Para revisar los logs de las solicitudes, se dispone de un endpoint en el API Gateway (`getLogs` en la colección de Postman).  
Para realizar la consulta, se debe incluir la **`api_key`** en el header del request. Como respuesta, se entregará una lista con los registros de las solicitudes asociadas a esa clave.  
Los logs se obtienen a partir de la información almacenada en **Memcached** por el `log-service`, y estarán disponibles durante una hora.  
 * **Endpoint:** `http://localhost:8000/logs/`
 * **Header:** key:`Authorization`,  value:`api_key`
 * **Response:**
```
[
    {
        "api_key": "05cf974aefd7da50eca33ccd891ae06edf4ccd9f7718a83552a70e5947cfb44d",
        "endpoint": "/similars/326006",
        "timestamp": "2025-02-05T00:32:32.906074",
        "model_processing_time": 4.263,
        "request_processing_time": 4.263
    },
    {
        "api_key": "05cf974aefd7da50eca33ccd891ae06edf4ccd9f7718a83552a70e5947cfb44d",
        "endpoint": "/similars/326006",
        "timestamp": "2025-02-05T00:32:34.685314",
        "model_processing_time": 0.0385,
        "request_processing_time": 0.0385
    }
]

```
>  ⭑ En este ejemplo se logra ver la diferencia en el tiempo de procesamiento de los request del mismo modelo, ya que la primera vez que se consulta un las similaridades de un grafo la respuesta es almacenada, por consiguiente la segunda que vez que se consulta se trae la informcación almacenada en cache.

# model-service 
El `model-service` es un microservicio que aloja un modelo de aprendizaje automático (ML) `trained_model.pkl` para encontrar propiedades similares entre grafos que representan inmuebles. Utiliza PyKeen, una biblioteca de Python para incrustaciones de gráficos de conocimiento, para cargar y procesar el modelo ML. El servicio también integra Redis para almacenar en caché los resultados y mejorar el rendimiento.
El servicio comienza  inicializando la aplicación FastAPI. Utiliza el **lifespan manager** de  FastAPI, un administrador de vida útil, para cargar el modelo ML cuando se inicia el servicio `load_model()` preparando así las listas necesarias para posteriormente ejecutar la lógica que entregara al API getway la lista de los 10 IDs de los grafos similares. Por último borrar el caché cuando se cierra el servicio.

* `load_model()`:
  1. El modelo preentrenado se carga desde el archivo serializado `trained_model.pkl` utilizando PyTorch.
  2. Se utiliza TriplesFactory de PyKeen para cargar los datos del grafo de conocimiento desde el archivo `dataset_train.tsv.gz`.
  3. El conjunto de datos se lee en un DataFrame de Pandas. Se filtran entidades y se extraen los IDs de entidades y relaciones, y se almacenan en variables globales `heads_id` y `relations_id`.
  4. Se crea el tensor `hr_batch` emparejando los IDs de entidades con los IDs de relaciones.
    
* `find_similars()`:
  1. Se verifica que el `head_id` exista en la lista `heads_id`. Si no se encuentra, se devuelve un error.
  2. El servicio comprueba si el resultado para el `head_id` ya está almacenado en Redis. Si el resultado está en cache, se devuelve inmediatamente.
  3. Si el resultado no está en cache, de lo contrario continua la ejecución.
  4. Se prepara una muestra de tensor para el `head_id` dado.
  5. El modelo calcula puntuaciones para todas las entidades en el grafo de conocimiento.
  6. Las puntuaciones se emparejan con sus índices y se ordenan.
  7. Se seleccionan los 10 índices principales y se asignan a los `heads_id`` originales.
  8. El resultado se guarda en Redis con un tiempo de expiración de 1 hora.
  9. Se devuelve la lista de propiedades similares al cliente.
 
  # auth-service
El `auth-service` es el microservicio responsable de registrar los usuarios, generar sus `api_key`, autenticar usuarios y limitar los requests de acuerdo al `acount_type` del usuario. Se asegura que solo los usuarios autenticados puedan acceder al sistema. El servicio comienza inicializando la aplicación FastAPI, utiliza un modelo de **Pydantic** (`UserCreate`) para validar los datos de registro de usuarios entrantes.  Para el almacenamiento se usa **MongoDB** para almacenar datos de usuarios (nombre de usuario, clave de API, tipo de cuenta) en el **`users_collection`** y se utiliza un  **`redis_client`** que rastrea la cantidad de solicitudes realizadas para aplicar la limitación de tasa (*rate limiting*).  

  # log-service
El `log-service` es un microservicio responsable de registrar las solicitudes de los usuarios y almacenarlas en Memcached, un sistema de almacenamiento en caché de memoria distribuida de alto rendimiento. El servicio registra detalles como la clave de API, el endpoint, las marcas de tiempo y los tiempos de procesamiento de cada solicitud. Además, proporciona un endpoint para recuperar los registros de un usuario específico.

# Result 

![topicos2](https://github.com/user-attachments/assets/bf5c2f56-9306-4f98-bc4f-9037ce7bf784)
