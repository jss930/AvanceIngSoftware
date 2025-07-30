# 🌐 Mapa Interactivo Colaborativo

El presente proyecto tiene como objetivo aprender sobre el desarrollo de software con tecnologias moderdas explorando arquitecturas de software, frameworks, DDD, Herramientas de desarrollo agil y demas que estan detalladas en el presente. El proyecto es grupal y su objetivo es conectar personas mediante un **mapa de calor en línea** y **Sistema de reportes**, permitiendo la interacción y colaboración en tiempo real.

---

## 📌 Propósito

El propósito de este software es brindar una **plataforma online** donde los usuarios puedan:

- Analizar un mapa de calor para poder evitar ciertas zonas de alto transito.
- Compartir ubicaciones, comentarios o información sobre posibles incidencias que perjudiquen el trafico.
- Colaborar en tiempo real con otros usuarios conectados.
- Potenciar actividades sociales como el ciclismo o la exploracion de rutas alternativas.

---

## 🚀 Funcionalidades

### 🔹 Funcionalidades de Alto Nivel

A continuación, se presenta el **Diagrama de Casos de Uso UML** que representa las principales interacciones del usuario con el sistema:

![Casos de Uso](scr/rm/casosDeUso.jpeg)


### 🔸 Prototipo / GUI

Visual de la interfaz de usuario o boceto inicial del sistema:

![Prototipo](scr/rm/prototipo.png)

---

## 🧠 Modelo de Dominio

Representación abstracta de las clases conceptuales y objetos extraídos del área en cuestión

![Dominio](scr/rm/dominio.png)

### 🧩 Arquitectura de Capas

Representación de las principales entidades y sus relaciones dentro del sistema:

![UML](scr/rm/uml.jpg)

### 📦 Módulos

- `Presentacion/vista`: capa que contacta con el usuario.
- `Servicios`: capa designada a comunicar los controladores con los servicios.
- `Dominio`: Capa que contiene el entorno real de manera digitalizada.
- `Repositorio`: Conexiones con la base de datos y fuente de informacion.

---

## 🏗️ Vista General de Arquitectura

### 📐 Patrón de Diseño: MVC

La aplicación sigue la arquitectura **Modelo - Vista - Controlador (MVC)**:

- **Modelo (Model)**: Maneja la lógica de negocio y el acceso a datos.
  - Ejemplos: `User`, `Report`, `HeatMapData`.

- **Vista (View)**: Presenta los datos al usuario mediante interfaces visuales.
  - Ejemplos: Plantillas HTML para el mapa, formularios de envío de reportes.

- **Controlador (Controller)**: Recibe las peticiones del usuario, procesa la lógica y devuelve respuestas.
  - Ejemplos: `HeatMapController`, `UserController`, `ReportController`.

---

## 👥 Equipo de Desarrollo

| Integrante                        | Rol                              | Contacto                |
| --------------------------------- | -------------------------------- | ----------------------- |
| Afaro Buiza, Jesus Alberto        | Coordinador / Dev Full           | jalfarob@unsa.edu.pe    |
| Carpio Paiva Cesar Gonzalo        | Frontend Developer               | ccarpiop@unsa.edu.pe    |
| Colque Flores, Gerardo Javier     | Backend Developer                | gcolqueq@unsa.edu.pe    |
| Ccolque Quispe, Anthony Criz      | Backend Developer                | accolqueq@unsa.edu.pe   |
| Cornejo Alvarez, Mauricio Andres  | Arquitecto de proyecto           | mcornejoalv@unsa.edu.pe |
| Espinoza Barrios, DAvid Alejandro | Director del proyecto / Dev Full | despinozab@unsa.edu.pe  |
| Yavar Guillen, Roberto Gustavo    | Documentación                    | ryavarg@unsa.edu.pe     |

---

## 📄 Licencia

Este proyecto no está bajo la licencia, su proposito es educativo.  
Consulta el archivo `LICENSE` para más información.

---

## 🛠️ Tecnologías Utilizadas

- Lenguajes de programacion: `Python`, `HTML` 
- Framework: `Bootstrap`
- Base de Datos: `SQLite`
- APIs: `Leaflet`

### Enlace a tablero TRELLO

Enlace para visualizar como distribuimos el trabajo mediante tecnologias agiles:

visita nuestro [Trello](https://trello.com/b/VHHYqcFk/is-sistema-de-reportes-de-trafico-arequipa).
