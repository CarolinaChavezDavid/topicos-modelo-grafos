# topicos-modelo-grafos
Este proyecto es una aplicación basada en microservicios que utiliza un modelo de aprendizaje automático (ML) basado en grafos de conocimiento. El sistema está diseñado para devolver una lista con los IDs de 10 grafos que representan inmueblese similares dado un `head_id` (un identificador único de una propiedad). La arquitectura está construida utilizando FastAPI para los servicios de backend, Docker para la contenedorización y Docker Compose para la orquestación.

El proyecto está dividido en múltiples microservicios, cada uno manejando una funcionalidad específica:

* **API Gateway:** Actúa como el punto de entrada para todas las solicitudes de los clientes y las dirige a los microservicios correspondientes.
* **Authentication Service:** Maneja la autenticación de usuarios y la limitación de solicitudes.
* **Model Service**: Aloja el modelo de ML y proporciona recomendaciones de propiedades basadas en el `head_id`.
* **Logging Service:** Registra todas las solicitudes y respuestas para monitoreo y depuración.

* **Base de Datos:** Utiliza MongoDB para los datos de usuario y Redis para almacenamiento en caché y limitación de tasa.

### Estructura del proyecto

![topicos2 drawio (1)](https://github.com/user-attachments/assets/fd0b0b37-8228-4b5c-abed-68bd08cf851c)


## Project set up
Como prerequisitios se debe tener instalado Docker y Docker compose.

1. Clonar o descargar el proyecto  
2. Ejecutar el comando:
```
docker-compose up --build
```
> En caso de error al ejecutar el comando revisar los logs de los servicios y revisar que los puertos utilizados en los servicios descritos en el docker-compose.yml esten disponibles

# API Getaway
El `API Gateway`  es un microservicio basado en FastAPI-based que funciona como punto central para manejar las solicitudes de los usuarios. La razon principal  de utilizar  este servicio es que los clientes interactuen unicamente con este, centralizando la logica y ayudando a la escalabilidad ya que cualquier nuevo servicio o reques que se agregue puede ser facilmente registrado (log) validado(authorization) y limitado(rate Limited), este es el encargado de enviar el los requests a los demas servicies.
El **API Gateway** con tres mircroservicios la comunicación entre estos serivicios se da usand  HTTP con `httpx.AsyncClient` que ayuda que los request no  sean bloqueantes. Además, aunque cada servicio maneja los posibles errores generando mensajes especificos para posibles casos, este servicio agrega una capa extra para manejar el error en caso de exista algun error de conexión con el servidor

* **Workflow**
 1. **Health Check** La api cuenta con un endpoint (getTestAPI en la colección de Postman) que retorna un mensaje de éxito, ayuda a determinar que el proyecto se ejecuto de manera correcta.
  * Endpoint :`http://localhost:8000`
  * Response:
```
{
    "message": "API Gateway esta funcionando!"
}
```
 2. **Registro de usuario** Los usuarios antes de realizar una petición para obtener el resultado del modelo de grafos debe registrarse con el endpoint de registro (userRegistration en la colección de Postman) y así obtener una `api_key` única que es obligatoria para poder hacer request al modelo y  revisar los logs. En el body del request deberá asignarse un nombre de usuario `username` y un tipo de cuenta `acount_type` de tipo **FREEPREMIUM** o **PREMIUM**
* Endpoint: `http://localhost:8000/register/`
* Body: 
```
{
    "username": "CaroTest",
    "account_type": "FREEMIUM"
}
```

* Response: 
    
```
{
    "message": "Usuario registrado exitosamente.",
    "api_key": "05cf974aefd7da50eca33ccd891ae06edf4ccd9f7718a83552a70e5947cfb44d"
}
```

![userRegister](https://github.com/user-attachments/assets/835b47ae-1126-4ff8-a407-cba1cae5c259)


Rate Limiting Check

Before processing a request, the API Gateway checks the rate limit by calling the Authentication Service:

Sends the request headers to /rate-limit-check.

If allowed, proceeds; otherwise, returns a 429 Too Many Requests response.

2. Processing Requests

User Registration (POST /register/)

Forwards user registration data to the Authentication Service.

Returns the response from the Authentication Service to the client.

Finding Similar Properties (POST /similars/{head_id})

Validates the request and applies rate limiting.

Calls the Model Service to retrieve similar properties.

Logs the request to the Log Service.

Returns the list of similar properties to the client.

Fetching Logs (GET /logs/)

Forwards the request to the Log Service.

Returns stored logs to the client.

3. Logging Requests

After processing each request, the API Gateway logs details such as:

API Key

Endpoint accessed

Timestamps (start & end)

Processing time
These logs are sent to the Log Service for storage.

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
  # log-service
El `log-service` es un microservicio responsable de registrar las solicitudes de los usuarios y almacenarlas en Memcached, un sistema de almacenamiento en caché de memoria distribuida de alto rendimiento. El servicio registra detalles como la clave de API, el endpoint, las marcas de tiempo y los tiempos de procesamiento de cada solicitud. Además, proporciona un endpoint para recuperar los registros de un usuario específico.

# Result 

![topicos2](https://github.com/user-attachments/assets/bf5c2f56-9306-4f98-bc4f-9037ce7bf784)
