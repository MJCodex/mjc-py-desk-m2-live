class GlobalConsole:
    """Clase estática para manejar la consola global."""
    console = None
    web_console = None

    @staticmethod
    def set_console(console_widget):
        GlobalConsole.console = console_widget

    @staticmethod
    def set_web_handler(handler):
        GlobalConsole.web_console = handler

    @staticmethod
    def log(message):
        """Escribe un mensaje en la consola global."""
        if GlobalConsole.console is not None:
            GlobalConsole.console.configure(state="normal")
            GlobalConsole.console.insert("end", f"{message}\n")
            GlobalConsole.console.configure(state="disabled")
            GlobalConsole.console.see("end")
        if GlobalConsole.web_console is not None:
            GlobalConsole.web_console(message)
