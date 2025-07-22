#  Laboratorio 12: Principios SOLID

## Autor

**David A. Espinoza B.**
**Módulo:** Panel Administrativo (Control de Reportes)

## Principios Aplicados

---

### **S - Single Responsibility Principle (SRP)**

**Cada clase o función tiene una única responsabilidad.**

#### Ejemplo:

`ReporteColaborativoRepositoryImpl.py`

```python
class ReporteColaborativoRepositoryImpl(IReporteColaborativoRepository):
    def obtener_todos(self):
        return ReporteColaborativo.objects.all()

    def buscar_por_id(self, reporte_id):
        return ReporteColaborativo.objects.filter(id=reporte_id).first()

    def actualizar(self, reporte):
        reporte.save()
```

**Explicación:**
Esta clase se encarga **únicamente del acceso a datos del modelo `ReporteColaborativo`**, respetando SRP. No contiene lógica de validación ni de negocio.

---

### **O - Open/Closed Principle (OCP)**

**El código está abierto a extensión pero cerrado a modificación.**

#### Ejemplo:

`ReporteColaborativoApplicationService.py`

```python
class ReporteColaborativoApplicationService:
    def __init__(self):
        self.reporte_repository = ReporteColaborativoRepositoryImpl()
        ...
```

**Explicación:**
Podemos extender el comportamiento cambiando la implementación del repositorio (`ReporteColaborativoRepositoryImpl`) sin modificar el servicio.
Esto es posible gracias a la **inyección de dependencias** basada en interfaces (`IReporteColaborativoRepository`), lo que permite sustituir el backend de datos sin alterar la lógica del servicio.

---

### **L - Liskov Substitution Principle (LSP)**

**Una subclase debe poder sustituir a su clase base sin alterar el comportamiento del sistema.**

#### Ejemplo:

`ReporteColaborativoRepositoryImpl` implementa la interfaz `IReporteColaborativoRepository`.

```python
class ReporteColaborativoRepositoryImpl(IReporteColaborativoRepository):
    ...
```

**Explicación:**
Cualquier otra clase que implemente esta interfaz puede ser usada en su lugar, sin romper la lógica de `ReporteColaborativoApplicationService`, cumpliendo con LSP.

---

### Otros principios que se están respetando:

* **I - Interface Segregation Principle (ISP):**
  Aunque no se ve múltiples interfaces aún, el uso de `IReporteColaborativoRepository`muestra de forma clara el diseño por interfaces específicas.

* **D - Dependency Inversion Principle (DIP):**
  La clase `ReporteColaborativoApplicationService` depende de la **abstracción**, no de la implementación directa, al usar una interfaz para el repositorio.

---

## Análisis con SonarLint

✅ Se corrigieron o no se detectaron **bugs críticos ni vulnerabilidades** en los archivos revisados (`views.py`, `reporteColaborativoController`, `repository`, `applicationService`).
