import os
from typing import Optional, Tuple
import tempfile
from datetime import datetime
import pyautogui
from src.pushbullet_base import PushbulletBase

class ScreenshotManager(PushbulletBase):
    def __init__(self):
        super().__init__()
        self.temp_dir = tempfile.gettempdir()

    def take_screenshot(
        self,
        region: Optional[Tuple[int, int, int, int]] = None,
        filename: Optional[str] = None
    ) -> str:
        """
        Toma una captura de pantalla y la guarda temporalmente.
        
        Args:
            region: Tupla opcional (x, y, width, height) para capturar una región específica
            filename: Nombre opcional para el archivo. Si no se proporciona, se genera uno.
        
        Returns:
            str: Ruta del archivo temporal donde se guardó la captura
        """
        try:
            # Generar nombre de archivo si no se proporcionó
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"
            
            # Ruta completa del archivo temporal
            filepath = os.path.join(self.temp_dir, filename)
            
            # Tomar la captura
            if region:
                screenshot = pyautogui.screenshot(region=region)
            else:
                screenshot = pyautogui.screenshot()
            
            # Guardar la captura
            screenshot.save(filepath)
            return filepath
            
        except OSError as e:
            raise RuntimeError(f"Error al tomar la captura de pantalla: {str(e)}")
    
    def send_screenshot_file(
        self,
        filepath: str,
        title: Optional[str] = None,
        body: Optional[str] = None
    ) -> dict:
        """
        Envía un archivo de captura de pantalla existente a través de Pushbullet.
        
        Args:
            filepath: Ruta al archivo de la captura
            title: Título opcional para la notificación
            body: Texto opcional para el cuerpo de la notificación
            device: Dispositivo específico al cual enviar (nombre o objeto device)
        
        Returns:
            dict: Respuesta de la API de Pushbullet
        """
        try:
            # Verificar que el archivo existe
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"No se encontró el archivo: {filepath}")
            
            # Preparar el título
            if title is None:
                title = "Captura de pantalla"
            
            # Enviar el archivo
            with open(filepath, "rb") as file:
                file_data = self.pb.upload_file(file, os.path.basename(filepath))
                
                push = self.pb.push_file(
                    file_url=file_data["file_url"],
                    file_name=file_data["file_name"],
                    file_type=file_data["file_type"],
                    title=title,
                    body=body
                )
                
            return push
            
        except OSError as e:
            raise RuntimeError(f"Error al enviar la captura de pantalla: {str(e)}")
        
    def capture_and_send(
        self,
        region: Optional[Tuple[int, int, int, int]] = None,
        title: Optional[str] = None,
        body: Optional[str] = None,
        delete_after: bool = True
    ) -> dict:
        """
        Toma una captura de pantalla y la envía inmediatamente.
        
        Args:
            region: Región opcional para capturar (x, y, width, height)
            title: Título opcional para la notificación
            body: Texto opcional para el cuerpo de la notificación
            device: Dispositivo específico al cual enviar
            delete_after: Si se debe eliminar el archivo temporal después de enviar
        
        Returns:
            dict: Respuesta de la API de Pushbullet
        """
        try:
            # Tomar la captura
            filepath = self.take_screenshot(region)
            
            # Enviar la captura
            result = self.send_screenshot_file(filepath, title, body)
            
            # Eliminar el archivo temporal si se solicitó
            if delete_after and os.path.exists(filepath):
                os.remove(filepath)
                
            return result
            
        except OSError as e:
            raise RuntimeError(f"Error en capture_and_send: {str(e)}")