import sys
from tkinter import messagebox

from tyo import App

def main():
    """
    File entry point utama untuk menjalankan game GhostBusters.
    File ini memanggil App controller dari tyo.py yang secara otomatis
    merangkai sistem login Jovan, gameplay Ozzy, dan menu-menu Daffa.
    """
    try:
        app = App()
        app.mainloop()
    except Exception as e:
        import traceback
        traceback.print_exc()
        try:
            messagebox.showerror(
                "Error Fatal",
                f"Gagal menjalankan aplikasi GhostBusters:\n\n{e}"
            )
        except:
            pass

if __name__ == "__main__":
    main()