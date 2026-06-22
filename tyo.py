import tkinter as tk 
import tkinter.messagebox as messagebox

jendela = tk.Tk()
jendela.title("GhostBuster") 
jendela.geometry("400x300")
label = tk.Label(jendela, text="Selamat Datang di GhostBuster!", font=("Arial", 16)) 
label.pack(pady=20)
button = tk.Button(jendela, text="Mulai", font=("Arial", 14), command=lambda: messagebox.showinfo("Mulai", "Mulai GhostBuster!"))
button.pack(pady=10) 

class GhostBuster:
    def __init__(self, master):
        self.master = master
        self.master.title("GhostBuster Game")
        self.master.geometry("400x300")
        self.label = tk.Label(self.master, text="GhostBuster Game", font=("Arial", 16))
        self.label.pack(pady=20)
        self.start_button = tk.Button(self.master, text="Start Game", font=("Arial", 14), command=self.start_game)
        self.start_button.pack(pady=10)

    def start_game(self):
        messagebox.showinfo("Game Started", "The GhostBuster game has started!") 