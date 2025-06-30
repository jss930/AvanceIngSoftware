
# 🌐 Mapa Interactivo Colaborativo

El presente protecto tiene como objetivo aprender sobre el desarrollo de software con tecnologias moderdas explorando arquitecturas de software, frameworks, DDD, Herramientas de desarrollo agil y demas que estan detalladas en el presente. El proyecto es grupal y su objetivo es conectar personas mediante un **mapa de calor en línea** y **Sistema de reportes**, permitiendo la interacción y colaboración en tiempo real.

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

📎 _[Incluir aquí una imagen o enlace al diagrama]_  
`Ejemplo: docs/casos_de_uso.png`

- Ver y navegar el mapa
- Marcar ubicaciones
- Comentar o etiquetar zonas
- Interactuar con otros usuarios

### 🔸 Prototipo / GUI

Visual de la interfaz de usuario o boceto inicial del sistema:

📎 _[Incluir capturas del prototipo o mockup]_  
`Ejemplo: docs/prototipo_gui.png`

---

## 🧠 Modelo de Dominio

### 🧩 Diagrama de Clases UML

Representación de las principales entidades y sus relaciones dentro del sistema:

📎 _[Incluir aquí el diagrama de clases UML]_  
`Ejemplo: docs/diagrama_clases.png`

### 📦 Módulos

- `MapaInteractivo`: manejo del mapa y sus capas.
- `Usuario`: autenticación, datos y preferencias.
- `Comunicacion`: chat y mensajería en tiempo real.
- `BaseDeDatos`: acceso a datos geoespaciales.
- `InterfazWeb`: componentes y vista frontend.

---

## 🏗️ Vista General de Arquitectura

### 📁 Diagrama de Paquetes

Distribución de los módulos del sistema:

📎 _[Incluir diagrama de paquetes]_  
`Ejemplo: docs/diagrama_paquetes.png`

### 🔧 Clases Principales

- `MapaController`: lógica de control del mapa.
- `UsuarioService`: gestión de usuarios.
- `ChatManager`: controlador de mensajes en vivo.
- `MapRenderer`: renderizado visual del mapa.

---

## 👥 Equipo de Desarrollo

| Integrante        | Rol                   | Contacto              |
|-------------------|------------------------|------------------------|
| Afaro Buiza, Jesus Alberto   | Coordinador / Dev Full | ccarpiop@unsa.edu.pe     |
| Carpio Paiva Cesar Gonzalo  | Frontend Developer   | ccarpiop@unsa.edu.pe                      |
| Colque Flores, Gerardo Javier   | Backend Developer      |               @unsa.edu.pe        |
| Ccolque Quispe, Anthony Criz   | Documentación          |              @unsa.edu.pe         |
| Cornejo Alvarez, Mauricio Andres   | Documentación          |           @unsa.edu.pe            |
| Espinoza Barrios, DAvid Alejandro   | Documentación          |            @unsa.edu.pe           |
| Yavar Guillen, Roberto Gustavo  | Documentación          |                @unsa.edu.pe       |



---

## 📄 Licencia

Este proyecto está bajo la licencia MIT.  
Consulta el archivo `LICENSE` para más información.

---

## 🛠️ Tecnologías Utilizadas

- Lenguaje: `JavaScript`, `Python`, `Java` (ajustar según el caso)
- Framework: `React`, `Node.js`, `Django` (ajustar)
- Base de Datos: `PostgreSQL`, `MongoDB` (ajustar)
- APIs: `Leaflet`, `OpenStreetMap`, etc.
