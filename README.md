# Agente Literario

Este es un proyecto de Agente Literario.

## Captura de Pantalla

![Captura de pantalla](Captura%20de%20pantalla%202025-04-08%20201807.png)

## Instalación

### Backend

Para instalar y ejecutar el backend de este proyecto, siga estos pasos:

1.  Navegue al directorio del backend: `cd agente_literario_ui/backend`
2.  Cree un entorno virtual: `python3 -m venv venv`
3.  Active el entorno virtual: `source venv/bin/activate` (Linux/macOS) o `venv\Scripts\activate` (Windows)
4.  Instale las dependencias: `pip install -r requirements.txt`
5.  Ejecute la aplicación: `python main.py`

### Frontend

Para instalar y ejecutar el frontend de este proyecto, siga estos pasos:

1.  Navegue al directorio del frontend: `cd agente_literario_ui/frontend`
2.  Instale las dependencias: `npm install`
3.  Ejecute la aplicación: `npm run dev`

¡Disfrute de su Agente Literario!

## Advertencia

Este proyecto está diseñado para utilizar la API de Gemini. Para su correcto funcionamiento, necesitará proporcionar una API key de Gemini en el archivo .env.
Alternativamente, puede adaptar el proyecto para que funcione con Ollama u otro modelo de lenguaje de su elección.

El modelo ejecuta comandos en Powershel para hacer las operaciones, pero aún no se ha implementado el módulo de seguridad.

**Precauciones de seguridad:**

*   **No exponga su API key de Gemini a terceros.**
*   **Considere ejecutar el proyecto en un entorno aislado (Docker, Sandbox) para evitar posibles riesgos de seguridad.**
*   **Revise y comprenda el código antes de ejecutarlo.**

## Descripción del Proyecto

Agente Literario es un amiguete siempre dispuesto a ayudar, diseñado para facilitar la creación y gestión de contenido literario, permitiendo a los usuarios generar historias, personajes y escenarios de manera eficiente.

## Características Principales

*   Manejo de archivos con lenguaje natural: Facilita la creación y gestión de contenido literario.
*   Generación de historias: Permite crear historias completas a partir de ideas iniciales.
*   Gestión de personajes: Facilita la creación y el seguimiento de personajes a lo largo de la historia.
*   Creación de escenarios: Permite diseñar y describir escenarios detallados para ambientar las historias.
*   Sugerencia de ideas: Ofrece sugerencias para expandir y mejorar las historias.
*   Corrección de faltas: Ayuda a identificar y corregir errores gramaticales y ortográficos.
*   Reescritura: Permite reescribir secciones de la historia para mejorar la fluidez y el estilo.
*   Inspiración: Fomenta la imaginación y la creatividad en el proceso de escritura.

## Contribución

Si desea contribuir a este proyecto, siga estos pasos:

1.  **Cree una bifurcación (fork) del repositorio:** Esto crea una copia del repositorio en su propia cuenta de GitHub.
2.  **Realice los cambios deseados en su bifurcación:** Modifique el código, añada nuevas características o corrija errores.
3.  **Envíe una solicitud de extracción (pull request):** Proponga sus cambios para que sean incorporados al repositorio principal.

## Próximos Pasos

El siguiente paso es que el agente edite directamente en el canvas para una experiencia de usuario más interactiva.
