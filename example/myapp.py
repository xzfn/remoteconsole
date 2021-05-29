import tkinter as tk

import remoteconsole.server


class MyApp:
    def __init__(self, master):
        self.master = master

        server_address = ('127.0.0.1', 9000)
        self.console_environment = {}
        self.console_server = remoteconsole.server.ConsoleServer(server_address)
        console_handler = remoteconsole.server.PythonCodeHandler(self.console_environment)
        self.console_server.set_request_handler(console_handler)

        self.create_widgets()

        self.master.after(100, self.update)
        self.master.protocol('WM_DELETE_WINDOW', self.on_closing)

    def create_widgets(self):
        self.mainframe = tk.Frame(self.master)
        self.mainframe.pack(fill=tk.BOTH, expand=True)
        self.label = tk.Label(self.mainframe, text='hello')
        self.label.pack()

    def update(self):
        self.master.after(100, self.update)
        self.console_server.service()

    def on_closing(self):
        self.console_server.shutdown()
        self.master.destroy()


if __name__ == '__main__':
    root = tk.Tk()
    root.geometry('400x200')
    app = MyApp(root)
    root.mainloop()
