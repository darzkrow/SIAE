# Plan de Corrección de Errores

Basado en los errores reportados en la consola del navegador, se ha elaborado el siguiente plan de acción para solucionarlos.

## Errores Reportados

1.  `GET http://localhost/api/movimientos/?limit=5 500 (Internal Server Error)`: Error crítico del backend.
2.  `Error fetching stats ... 'Request failed with status code 500'`: Error del frontend como consecuencia del error del backend.
3.  `Uncaught (in promise) Error: No checkout popup config found`: Posiblemente un error de un script de terceros.
4.  `Failed to get subsystem status for purpose {rejected: true, message: 'UNSUPPORTED_OS'}`: Posiblemente un error de una extensión del navegador.

## Plan de Tareas

1.  **[ ] Backend: Investigar y corregir el error 500 en `/api/movimientos/`**
    -   **Subtarea:** Analizar el código de la vista de Django que maneja el endpoint `/api/movimientos/` para identificar la causa del error. La vista se encuentra probablemente en `inventario/views.py` o un archivo similar.
    -   **Subtarea:** Depurar el código para entender por qué se produce el `Internal Server Error`. Se puede usar el debugger de Django o agregar logs.
    -   **Subtarea:** Implementar la corrección necesaria en el backend.
    -   **Subtarea:** Crear una prueba (aunque sea temporal) para verificar que el endpoint `/api/movimientos/` ya no devuelve un error 500 y retorna los datos esperados.

2.  **[ ] Frontend: Verificar la correcta visualización de los datos**
    -   **Subtarea:** Una vez que el backend esté corregido, verificar que el dashboard (`Dashboard-j-aD7ixM.js`) muestra correctamente las estadísticas obtenidas de `/api/movimientos/`.
    -   **Subtarea:** Asegurarse de que no aparecen nuevos errores en la consola relacionados con el manejo de los datos recibidos.

3.  **[ ] Investigación de errores de terceros**
    -   **Subtarea:** Investigar los errores "No checkout popup config found" y "Failed to get subsystem status".
    -   **Subtarea:** Determinar si estos errores provienen de extensiones del navegador o scripts de terceros no relacionados con la aplicación.
    -   **Subtarea:** Si se confirma que son externos, documentarlo y considerarlos fuera del alcance de la corrección de la aplicación.
