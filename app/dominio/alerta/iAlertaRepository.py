from abc import ABC, abstractmethod

class IAlertaRepository(ABC):
    @abstractmethod
    def guardar(self, alerta):
        pass

    @abstractmethod
    def obtener_por_usuario(self, usuario_id):
        pass

    @abstractmethod
    def listar_todas(self):
        pass
