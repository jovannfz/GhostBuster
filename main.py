import sys
from tkinter import messagebox

# Mengimpor controller utama (App) dari file tyo.py
from tyo import App

def main():
    """
    File entry point utama untuk menjalankan game GhostBusters.
    File ini memanggil App controller dari tyo.py yang secara otomatis
    merangkai sistem login Jovan, gameplay Ozzy, dan menu-menu Daffa.
    """
    try:
        # Inisialisasi dan jalankan aplikasi Tkinter
        app = App()
        app.mainloop()
    except Exception as e:
        # Menampilkan log error ke terminal jika terjadi crash saat start
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