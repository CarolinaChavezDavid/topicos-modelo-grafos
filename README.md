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
La razon principal  de utilizar  este servicio es que los clientes interactuen unicamente con este, centralizando la logica y ayudando a la escalabilidad ya que cualquier nuevo servicio o reques que se agregue puede ser facilmente registrado (log) validado(authorization) y limitado(rate Limited), este es el encargado de enviar el los requests a los demas servicies
# Service model
En este servicio se crea una funcion que carga el modelo y prepara las variables necesarias para procesar los request y entregar la lista con los ID's de los inmuebles similares. Se hace uso de LifeSpan Events de FastAPI para cargar el modelo cuando solo cuando se incia la aplicacion.

# Result 

![topicos2](https://github.com/user-attachments/assets/bf5c2f56-9306-4f98-bc4f-9037ce7bf784)
