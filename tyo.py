import tkinter as tk 

jendela = tk.Tk()
jendela.title("GhostBuster") 
jendela.geometry("400x300")
label = tk.Label(jendela, text="Selamat Datang di GhostBuster!", font=("Arial", 16)) 
label.pack(pady=20)
button = tk.Button(jendela, text="Mulai", font=("Arial", 14), command=lambda: print("Mulai GhostBuster!"))
button.pack(pady=10) 