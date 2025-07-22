# 🌐 Mapa Interactivo Colaborativo

El presente proyecto tiene como objetivo aprender sobre el desarrollo de software con tecnologias moderdas explorando arquitecturas de software, frameworks, DDD, Herramientas de desarrollo agil y demas que estan detalladas en el presente. El proyecto es grupal y su objetivo es conectar personas mediante un **mapa de calor en línea** y **Sistema de reportes**, permitiendo la interacción y colaboración en tiempo real.

---

---

# lab 11 CLEAN CODE

1. **Nombres**
   Se aplican buenas prácticas:
   Clases como ReporteColaborativo, ReporteIncidentView, ReporteColaborativoForm usan CamelCase.
   Nombres como get_coords_from_address, form_valid, success_url son expresivos y concisos.
   En los modelos, campos como usuario_reportador, votos_positivos, imagen_geolocalizada reflejan claramente su propósito y están en snake_case.

2. **Funciones**
   Se cumplen principios de funciones limpias:
   Las funciones get_address_from_coords y get_coords_from_address realizan una sola tarea específica.
   form_valid está ligeramente larga, pero sigue una lógica clara, con validación progresiva y sin anidar en exceso.

3. **Comentarios**
   \# Si el usuario escribió una ubicación, geocodificamos con ORS
   Este es útil y no obvio.

4. **Estructura del Código Fuente**
   Importaciones están agrupadas y ordenadas (standard, luego Django, luego terceros, luego locales).
   Clases y funciones están bien separadas por líneas en blanco.
   La vista, el formulario y el modelo están en módulos separados, conforme al patrón de Django.

5. **Objetos / Estructuras de Datos**
   ReporteColaborativo y Alerta están modelados como clases Django models.Model, encapsulando datos y responsabilidades de persistencia.
   Se usa correctamente ManyToManyField para usuarios_votantes y destinatarios, lo cual refleja bien las relaciones de dominio.

6. **Tratamiento de Errores**
   Se manejan errores correctamente con try/except:
   En get_address_from_coords y get_coords_from_address, se hace response.raise_for_status() seguido de try/except, lo cual es buena práctica.

7. **Clases**
   ReporteColaborativoForm hereda de forms.ModelForm, respetando el principio de especialización progresiva.
   ReporteIncidentView usa mixins (LoginRequiredMixin) correctamente.

---

# lab 10

## Estilos de programación

- Programación orientada a objetos
  - Herencia (CreateView, ModelForm, Model)
  - Encapsulación de datos (atributos del modelo)
- Estilo declarativo

  Lo usamos cuando definimos:

  - Modelos (titulo = models.CharField(...))
  - Formularios (widgets = { 'titulo': forms.TextInput(...) })
  - Templates ({{ form.as_p }} declara cómo se debe renderizar)

- Cookbook

  Lo usamos para trabajar con imagenes, declarando:

  - MEDIA_URL, MEDIA_ROOT, enctype para poder guardarlas

- Error / Exception Handling

  Django maneja automaticamente muchos errores y excepciones,
  las usamos por ejemplo para validar si el usuario esta logeado

---

# lab 9

## Convenciones y practicas en esta rama

- 4 espacios de tabulación
- Nombre de variables y funciones
  username
- Nombre de clases
  class RegistroUsuarioForm(UserCreationForm):
- Longitud de linea máximo 79 caracteres
- Evitar logica compleja
- Arquitectura MTV (Model Template View)
- Modularidad
- Agrupar apps en 'apps/' y organizar templates,static y media
- Cargar clave secreta desde '.env'
- Usar 'reverse_lazy()' en URLs y redirreciones
- Incluir requerements.txt

---

## Rerporte de Sonarqube

#### alert_method_empty

![Method Empty](scr/imgs/alert_method_empty.jpeg)

#### alert_string_duplicated

![String Duplicate](scr/imgs/alert_string_duplicated.jpeg)

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

**Usuario**

- Ver y navegar el mapa
- Iniciar sesion
- Reportar estado del trafico
- Consultar mapa de trafico
- Actualizar perfil
- Filtrar reportes por zona
- Recibir notificaciones de trafico
  **Administrador**
- Gestionar usuarios
- Moderar reportes
- Generar estadisticas
- Configurar zonas de la ciudad
- Eliminar reportes inapropiados

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

- `MapaInteractivo`: manejo del mapa y sus capas.
- `Usuario`: autenticación, datos y preferencias.
- `Comunicacion`: chat y mensajería en tiempo real.
- `BaseDeDatos`: acceso a datos geoespaciales.
- `InterfazWeb`: componentes y vista frontend.

---

## 🏗️ Vista General de Arquitectura

### 📁 Diagrama de Paquetes

Distribución de los módulos del sistema:

(hacer un diagrama del UML pero simplifcado)

### 🔧 Clases Principales

- `HeatMapController`: lógica de control del mapa.
- `UserService`: gestión de usuarios.
- `ReportManager`: controlador de mensajes en vivo.
- `MapRenderer`: renderizado visual del mapa.

---

## 👥 Equipo de Desarrollo

| Integrante                        | Rol                              | Contacto                |
| --------------------------------- | -------------------------------- | ----------------------- |
| Afaro Buiza, Jesus Alberto        | Coordinador / Dev Full           | jalfarob@unsa.edu.pe    |
| Carpio Paiva Cesar Gonzalo        | Frontend Developer               | ccarpiop@unsa.edu.pe    |
| Colque Flores, Gerardo Javier     | Backend Developer                | @unsa.edu.pe            |
| Ccolque Quispe, Anthony Criz      | Backend Developer                | @unsa.edu.pe            |
| Cornejo Alvarez, Mauricio Andres  | Arquitecto de proyecto           | mcornejoalv@unsa.edu.pe |
| Espinoza Barrios, DAvid Alejandro | Director del proyecto / Dev Full | despinozab@unsa.edu.pe  |
| Yavar Guillen, Roberto Gustavo    | Documentación                    | @unsa.edu.pe            |

---

## 📄 Licencia

Este proyecto está bajo la licencia (creo q borramos esto (?)).  
Consulta el archivo `LICENSE` para más información.

---

## 🛠️ Tecnologías Utilizadas

- Lenguajes de programacion: `Python`
- Framework: `Bootstrap`
- Base de Datos: `PostgreSQL`
- APIs: `Leaflet`

### Enlace a tablero TRELLO

Enlace para visualizar como distribuimos el trabajo mediante tecnologias agiles:

visita nuestro [Trello](https://trello.com/b/VHHYqcFk/is-sistema-de-reportes-de-trafico-arequipa).
