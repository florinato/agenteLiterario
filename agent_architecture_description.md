# Descripción de la Arquitectura del Agente Conversacional Autónomo

## 1. Concepto Central: Agente Autónomo Basado en Conversación y Acción

El núcleo de esta arquitectura es un **agente conversacional autónomo**. Este agente interactúa con el usuario en lenguaje natural para comprender un objetivo o tarea. Luego, de forma autónoma:

1.  **Descompone** la tarea en pasos lógicos.
2.  **Decide** la siguiente acción necesaria (que generalmente implica usar una herramienta externa o API).
3.  **Ejecuta** esa acción a través de un módulo "ejecutor".
4.  **Procesa** el resultado devuelto por la herramienta.
5.  **Itera**, usando el resultado como contexto para decidir el siguiente paso (otra acción o una respuesta final).
6.  **Finaliza** cuando la tarea está completa, comunicando el resultado final al usuario.

Este ciclo permite al agente manejar tareas complejas que requieren múltiples interacciones con sistemas externos, manteniendo el contexto a lo largo del proceso.

## 2. Diseño del Prompt (`TEMPLATE`) para la Generalización

El prompt principal (la variable `TEMPLATE` en `main.py`) es crucial para instruir al LLM sobre su comportamiento y es la pieza clave para adaptar el agente a nuevos dominios. Para generalizarlo:

*   **Rol y Herramienta:** Define claramente el rol (`Eres el agente X, experto en Y...`) y la herramienta principal (`Interactúas con [Sistema Externo] usando la función Z...`). Cambia `X`, `Y` y `Z` según el nuevo dominio.
*   **Capacidades (Acciones Soportadas):** Lista explícitamente las acciones específicas que la herramienta `Z` puede realizar. Esto guía al LLM sobre qué puede pedirle al ejecutor. Sé específico sobre los parámetros que cada acción puede necesitar.
*   **Flujo de Trabajo Estándar:** El prompt debe describir el ciclo iterativo:
    *   Analizar entrada (usuario o resultado anterior).
    *   Decidir si ejecutar una acción o responder al usuario.
    *   Si es acción, usar el formato `etiqueta_accion: payload`.
    *   Si es respuesta final, usar `respuesta_usuario: mensaje`.
    *   Esperar el resultado de la acción en formato `respuesta_sistema: resultado`.
    *   Usar `respuesta_sistema:` como entrada para la siguiente decisión.
*   **Protocolo de Comunicación (Etiquetas):** Define un conjunto de etiquetas claras y consistentes.
    *   `etiqueta_accion: payload`: Indica al código que debe ejecutar una acción. `etiqueta_accion` debe ser específica del dominio (ej. `consulta_mongo:`, `llamar_api_clima:`, `ejecutar_script_sql:`). El `payload` contiene la información necesaria para la acción (comando, parámetros JSON, etc.).
    *   `respuesta_sistema: resultado`: Usada por el código para devolver el resultado de la acción al LLM. Esta etiqueta puede ser genérica.
    *   `respuesta_usuario: mensaje`: Usada por el LLM para comunicarse directamente con el usuario (inicio, fin, aclaraciones, confirmaciones).
*   **Seguridad Adaptable:** Incluye una regla para acciones potencialmente peligrosas en el nuevo dominio. El LLM debe generar `respuesta_usuario: ¿Estás seguro de que quieres ejecutar [acción peligrosa]?` antes de generar la `etiqueta_accion:` correspondiente.
*   **Ejemplos:** Proporciona ejemplos concretos de secuencias de interacción (Usuario -> Agente(Acción) -> Sistema -> Agente(Acción) -> Sistema -> Agente(Respuesta)) adaptados al nuevo dominio.
*   **Placeholders:** `{history}` y `{input}` son universales y deben mantenerse para que Langchain (o el framework similar) inyecte el contexto.

## 3. Flujo Genérico del Agente (Lógica Reutilizable en `main.py`)

El código que orquesta el flujo es en gran parte reutilizable:

*   **Inicialización:** Cargar LLM, memoria, y la `ConversationChain` con el `TEMPLATE` específico del dominio.
*   **Bucle Principal (Usuario):** Espera la entrada del usuario.
*   **Bucle Interno (Autonomía):** Este es el motor principal y es genérico.
    1.  **Llamada al LLM:** `conversation.predict(input=current_input)` donde `current_input` es la consulta inicial o la `respuesta_sistema:` anterior.
    2.  **Parseo de Respuesta:** `communication.parse_message(model_response_raw)` extrae la `etiqueta` y el `contenido`.
    3.  **Despacho Condicional (Basado en Etiqueta):**
        *   **Si es `etiqueta_accion:`:**
            *   Llamar a `security.is_command_dangerous(contenido)` (adaptado al dominio).
            *   Si es peligroso, llamar a `security.request_authorization()`. Abortar si se deniega.
            *   Llamar a `executor.execute_action(etiqueta, contenido)`. **Punto Clave:** La función `execute_action` en `executor.py` actúa como un *despachador*. Recibe la etiqueta específica y el payload, y decide qué función interna o llamada API realizar. `main.py` no necesita conocer los detalles de cada acción.
            *   Recibir el `output` del ejecutor.
            *   Formatear: `respuesta_mongo_etiquetada = communication.create_respuesta_sistema(output)`.
            *   Actualizar `current_input = respuesta_mongo_etiquetada` para la siguiente iteración.
            *   Continuar el bucle interno.
        *   **Si es `respuesta_usuario:`:**
            *   Mostrar `contenido` al usuario.
            *   Romper el bucle interno (tarea completada para esa consulta).
        *   **Si es error/desconocido:** Manejar el error y romper el bucle interno.
*   **Manejo de Memoria:** `ConversationBufferMemory` (o similar) gestiona el historial automáticamente.

## 4. Adaptación por Módulos para un Nuevo Dominio

Para crear un agente para una nueva función (ej. interactuar con una API de clima):

*   **Reutilizables (Generalmente sin cambios):**
    *   `main.py`: La lógica del bucle principal e interno.
    *   `communication.py`: Las funciones `parse_message` y `create_respuesta_sistema` son genéricas.
    *   `model_integration.py`: La conexión al LLM es independiente del dominio.
    *   `logging_manager.py`: El registro es genérico.
*   **Adaptables (Requieren modificación/reescritura):**
    *   **`TEMPLATE` (en `main.py`):** Reescribir completamente el texto del prompt: definir el nuevo rol, la nueva herramienta (`llamar_api_clima`), las acciones soportadas (`obtener_temperatura`, `obtener_pronostico`), los formatos de payload esperados, y los ejemplos específicos del clima. Definir la nueva `etiqueta_accion` (ej. `consulta_clima:`).
    *   **`executor.py`:** Implementar la nueva lógica. Crear funciones como `_call_weather_api(endpoint, params)` y modificar/crear `execute_action(etiqueta, contenido)` para que, si `etiqueta == 'consulta_clima:'`, parseé el `contenido` y llame a `_call_weather_api`. Necesitará manejar la configuración de la API Key del clima (probablemente desde `.env`).
    *   **`security.py`:** Actualizar `DANGEROUS_COMMANDS` (o renombrarlo a `DANGEROUS_ACTIONS`) con las acciones consideradas peligrosas en el nuevo dominio (si las hay). La lógica de `request_authorization` puede reutilizarse.
    *   **`requirements.txt`:** Añadir las nuevas dependencias (ej. `requests` si llamas a una API REST).
    *   **`.env`:** Añadir las nuevas variables de entorno necesarias (ej. `WEATHER_API_KEY`).

Siguiendo estos pasos, puedes replicar la estructura del agente MongoDB para interactuar con prácticamente cualquier herramienta o API que pueda ser controlada mediante llamadas de función o comandos textuales.
