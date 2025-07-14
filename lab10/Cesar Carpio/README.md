# 📢 Proyecto Final: Reporte de Incidentes de Tráfico

## 🧠 Objetivo
Aplicar estilos de programación consistentes en los módulos asignados como parte del proyecto final del curso.

---

## ✅ Estilos de Programación Aplicados

1. **Pipeline / Lazy Rivers**  
   Flujo claro: `initForm()` → setup de eventos → validaciones → envío.  
   ![initForm y handlers JS](path/to/imagen_pipeline.png)

2. **Things (Componentes autocontenidos)**  
   Componente `PhotoHandler` que encapsula la lógica de la foto.  
   ![PhotoHandler Component JS code](path/to/imagen_photohandler.png)

3. **Error / Exception Handling**  
   - Reemplazo de `alert()` por mensajes inline.  
   - Manejo de errores en `FileReader.onerror`.  
   ![Manejo inline de errores y FileReader.onerror](path/to/imagen_error_handling.png)

4. **Cookbook / DRY (Don't Repeat Yourself)**  
   Funciones reutilizables para validación (`validateLength()`, `validateRequired()`).  
   ![Funciones validateLength y validateRequired](path/to/imagen_validacion.png)

5. **Trinity (Separación MVC mínima)**  
   - **Modelo**: lectura de datos del formulario.  
   - **Vista**: funciones `showError()`, `showPreview()`.  
   - **Controlador**: `handleSubmit()` orquesta el flujo.  
   ![Modelo, Vista, Controlador JS](path/to/imagen_trinity.png)

---

## 📄 Estructura del Proyecto

