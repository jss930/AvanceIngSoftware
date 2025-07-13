# Análisis de Calidad de Código con SonarQube

## Herramientas utilizadas
- IDE: PyCharm
- Plugin: SonarQube
- Lenguaje: Python (Django)
- Convenciones: PEP8

## Archivos analizados

### 1. `config/urls.py`

- Resultado: **Limpio**
- Comentario: Archivo de rutas del proyecto Django. Contiene la definición principal de URLs, sin errores de codificación ni prácticas inseguras.

---

### 2. `web/views.py`

- Resultado: **Limpio**
- Comentario: Las funciones de vista siguen las convenciones `snake_case`, contienen comentarios donde es necesario y estructuras claras.

---

### 3. `web/models.py`

- Resultado: **Limpio**
- Comentario: Modelos bien definidos, con atributos nombrados correctamente. Uso adecuado de clases y herencia desde `models.Model`.

---

### 4. `web/urls.py`

- Resultado: **Limpio**
- Comentario: Las rutas están declaradas de forma ordenada, con funciones de vista bien nombradas. Sin imports innecesarios ni errores.

---

### 5. `app/dominio/reporte/iReporteColaborativoRepository.py`

- Práctica aplicada:
	Aplicación de principios de diseño limpio (Clean Code) y convenciones de codificación para clases abstractas en Python (PEP8 y abc.ABC).
- Problema detectado por SonarQube: "Add a nested comment explaining why this method is empty or complete the implementation."
- Correcion: Se documentó cada método con un docstring descriptivo.

---

### 6. `app/presentation/controladores/reporteColaborativoController.py`

- Práctica aplicada:
	Aplicación de principios de diseño limpio (Clean Code) y convenciones de codificación para clases abstractas en Python (PEP8 y abc.ABC).
- Problema detectado por SonarQube: "Add a nested comment explaining why this method is empty or complete the implementation."
- Correcion: Se agregaron comentarios explicativos (TODO) en los métodos sin implementar, indicando que están pendientes de desarrollo.

---

### 7. `app/repositorio/reporte/reporteColaborativoRepositoryImpl.py`

- Resultado: **Limpio**
- Comentario: Se usa correctamente el patrón Repository para desacoplar la lógica de acceso a datos.
              El método obtener_todos tiene una única responsabilidad.
              Código limpio, directo y sin redundancias..

---

### 8. `app/servicios/reporteColaborativoApplicationService.py`

- Práctica aplicada:
	Se sigue el patrón de Aplicación de Servicios para orquestar la lógica de negocio relacionada con los reportes colaborativos. Aunque varios métodos aún están vacíos, se aplicó la convención PEP8, se organizaron correctamente las dependencias y se dejó espacio estructurado para futuras implementaciones.
- Problema detectado por SonarQube: 10 code smells encontrados por métodos vacíos (pass) sin comentario explicativo.
- Correcion: Se agregaron comentarios aclaratorios que justifican la ausencia de implementación actual.
