import sys
from tkinter import messagebox

# Mengimpor class App (Controller Utama) dari file tyo_screens_app
from tyo.py import App

def main():
    """
    Fungsi utama untuk menyalakan game GhostBusters kelompok.
    File ini memanggil App controller yang mengikat login Jovan,
    menu utama Daffa, gameplay Ozy, dan leaderboard.
    """
    try:
        # Membuat instance aplikasi dan menjalankan mainloop Tkinter
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
