entry poin 

if __name__ == "__main__":
    try:
        app().mainloop()
    except Exception as e:    
        import traceback; traceback.print_exc()
    try:
        messagebox.showerror("error fatal",
            f"gagal menjalankan aplikasi:\n\n"{e}\n\n"
            "pastikan mysql sudah berjalan dan konfigurasi\n"
            