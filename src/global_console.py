class GlobalConsole:
    """Clase estática para manejar la consola global."""
    console = None

    @staticmethod
    def set_console(console_widget):
        GlobalConsole.console = console_widget

    @staticmethod
    def log(message):
        """Escribe un mensaje en la consola global."""
        if GlobalConsole.console:
            GlobalConsole.console.configure(state="normal")
            GlobalConsole.console.insert("end", f"{message}\n")
            GlobalConsole.console.configure(state="disabled")
            GlobalConsole.console.see("end")
        else:
            print("Consola no inicializada.")
