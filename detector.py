import tkinter as tk
from src.app_ui import AppUI

def main():
    root = tk.Tk()
    # Creamos la interfaz gráfica pasándole la ventana principal
    AppUI(root)
    # Ejecutamos el bucle principal de Tkinter
    root.mainloop()

if __name__ == "__main__":
    main()