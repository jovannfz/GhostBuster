APP CONTROLLER 

class app(tk.Tk):
    width = 800
    height = 600

    def __init__(self):
        super().__init__()
        self.title("GhostBusters 👻")
        self.geometry(f"{self.WIDTH}x{self.HEIGHT}+0+0")
        self.resizable(False, False)
        self.configure(bg="#0a0f1e")

        self.current_user = None

        container = tk.Frame(self, bg="#0a0f1e")
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1) 

        self.frames = {}
        for Cls in [AuthScreen, MenuScreen, GameScreen,
                    GameOverScreen, LeaderboardScreen, SettingsScreen]:
            name = Cls.__name__
            f    = Cls(parent=container, controller=self)
            self.frames[name] = f
            f.grid(row=0, column=0, sticky="nsew")

        self.show("AuthScreen")
        self.protocol("WM_DELETE_WINDOW", self._on_close) 
    
    def show(self, name: str):
        frame = self.frames[name]
        frame.tkraise()
        frame.on_show()

    def set_user(self, user):
        self.current_user = user

    def _on_close(self):
        if messagebox.askokcancel("Keluar", "Yakin ingin keluar dari GhostBusters?"):
            self.destroy()

    def quit(self):
        self._on_close() 



BAGIAN ENTRY POINT

if __name__ == "__main__":
    try:
        app().mainloop()
    except Exception as e:    
        import traceback; traceback.print_exc()
    try:
        messagebox.showerror("error fatal",
            f"gagal menjalankan aplikasi:\n\n"{e}\n\n"
            "pastikan mysql sudah berjalan dan konfigurasi\n"
            "DB_CONFIG di bagian atas file sudah benar.")
    except Exception:
        pass

            