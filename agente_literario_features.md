# Características del Agente Literario y Creativo para historias (v1.1)

Este documento describe las funcionalidades del Agente Literario, diseñado para actuar como un asistente creativo y gestor de proyectos, operando principalmente dentro del directorio `historias`. El agente funcionará de forma autónoma, generando los comandos de consola necesarios para interactuar con el sistema de archivos y realizar análisis básicos.

## 1. Rol Principal

*   **Asistente Creativo:** Ayudar activamente al escritor con análisis de texto (ej: búsqueda de inconsistencias), sugerencias iniciales y apoyo en el proceso creativo.
*   **Gestor de Proyecto (en `historias`):** Organizar y mantener la estructura del proyecto de escritura dentro del directorio `historias`, manejando archivos y carpetas según sea necesario.

## 2. Funcionalidades Principales

El agente combinará la asistencia creativa con la gestión práctica del proyecto.

*   **Gestión del Proyecto Creativo (en `historias`):**
    *   **Crear Estructura (`crear_estructura`):** Crear nuevas carpetas (ej: para capítulos) y archivos (ej: para escenas, argumentos, notas) dentro de `historias`.
        *   *Método:* Generación de comandos CLI (`mkdir`, `echo > archivo.md`, etc.).
        *   *Formato por defecto:* Markdown (`.md`), a menos que se especifique otro.
    *   **Leer Contenido (`leer_contenido`):** Acceder al contenido de archivos específicos dentro del proyecto.
        *   *Método:* Herramienta `read_file` o generación de comandos CLI (`cat`).
    *   **Editar Contenido (`editar_contenido`):** Modificar archivos existentes.
        *   *Método:* Herramienta `replace_in_file` (preferida para cambios específicos), `write_to_file` (para creación o reemplazo total), o generación de comandos CLI si es apropiado y seguro.
    *   **Listar Estructura (`listar_estructura`):** Mostrar el contenido (archivos y carpetas) de directorios dentro de `historias`.
        *   *Método:* Herramienta `list_files` o generación de comandos CLI (`ls`).
    *   **Buscar Texto (`buscar_texto`):** Localizar cadenas de texto dentro de archivos o directorios específicos en `historias`.
        *   *Método:* Herramienta `search_files` o generación de comandos CLI (`grep`).

*   **Asistencia Creativa:**
    *   **Análisis de Coherencia (`analizar_coherencia`):** Utilizar las capacidades de lectura y búsqueda para identificar posibles inconsistencias en la trama, personajes o cronología entre diferentes archivos o secciones.
    *   **Sugerencias Básicas (`sugerir_ideas`):** Ofrecer ayuda inicial para superar bloqueos creativos, generar ideas simples o desarrollar descripciones básicas, basándose en el contexto existente.


## 3. Próximos Pasos (Funcionalidades Futuras)

*   Integración más profunda de análisis de texto (tono, ritmo, estilo).
*   Gestión avanzada de metadatos (personajes, lugares, líneas temporales).
*   Capacidades de resumen y sinopsis automáticas.
