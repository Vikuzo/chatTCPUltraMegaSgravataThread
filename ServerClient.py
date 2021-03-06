from tkinter import messagebox
from tkinter import scrolledtext
from threading import Thread
from PIL import Image, ImageTk
import Crittografia as Cr
import tkinter.font as tf
import tkinter as tk
import socket
import SocketFunction
import yaml


class choiceWindow(tk.Frame):
    def __init__(self, width, height, master=None):
        super().__init__(master)

        self.master.title('Menù')
        self.master.geometry("%sx%s" % (width, height))
        self.master.resizable(False, False)

        self.choiceLabel = tk.Label(self.master, text='Inserire il tuo username')
        self.choiceLabel.place(relx=0.025, rely=0.1, relwidth=1, relheight=0.125)

        self.entry = tk.Entry(self.master)
        self.entry.place(relx=0.25, rely=0.3, relwidth=0.5, relheight=0.125)

        self.clientButton = tk.Button(self.master, text='Client', command=self.client_is_the_choice)
        self.clientButton.place(relx=0.4, rely=0.5, relwidth=0.2, relheight=0.125)

        self.serverButton = tk.Button(self.master, text='Server', command=self.server_is_the_choice)
        self.serverButton.place(relx=0.4, rely=0.7, relwidth=0.2, relheight=0.125)

    def delete_all(self):
        self.clientButton.destroy()
        self.serverButton.destroy()
        self.choiceLabel.destroy()
        self.entry.destroy()
        self.destroy()

    def server_is_the_choice(self):
        username = self.entry.get()
        if '' != username:
            self.delete_all()
            chat = chatWindow(500, 500, username, '', 's')
            chat.mainloop()
        else:
            messagebox.showerror('Errore di immissione', 'Il campo USERNAME non può rimanere vuoto!')

    def client_is_the_choice(self):
        username = self.entry.get()
        if '' != username:
            self.delete_all()
            self.wordLabel = tk.Label(self.master, text='Inserire la chiave di crittografia')
            self.wordLabel.place(relx=0.025, rely=0.1, relwidth=1, relheight=0.125)
            self.wordButton = tk.Button(self.master, text='Mettiti in attesa',
                                        command=lambda: self.chat_as_client(username, self.entry.get()))
            self.wordButton.place(relx=0.25, rely=0.5, relwidth=0.5, relheight=0.125)
            self.entry = tk.Entry(self.master)
            self.entry.place(relx=0.25, rely=0.3, relwidth=0.5, relheight=0.125)
        else:
            messagebox.showerror('Errore di immissione', 'Il campo USERNAME non può rimanere vuoto!')

    def chat_as_client(self, username, word):
        chat = chatWindow(500, 500, username, word, 'c')
        chat.mainloop()


class chatWindow(tk.Frame):
    __width = 0
    __height = 0
    __username = ''
    __word = ''

    def __init__(self, width, height, username, word, choice, master=None):
        super().__init__(master)
        with open('Configuration.yaml', 'r') as yamlconfig:
            config = yaml.load(yamlconfig, Loader=yaml.FullLoader)

        self.__username = username
        self.__serverName = config['serverIP']
        self.__serverPort = config['serverPORT']
        self.__buffer = config['buffer']
        self.__word = word

        if 's' == choice:
            self.serverSocket = SocketFunction.socket_tcp_generation()
            try:
                SocketFunction.server_bind(self.serverSocket, self.__serverName, self.__serverPort)
            except socket.error:
                messagebox.showerror('Errore', 'Errore di creazione del socket')
                return

            messagebox.showinfo('Info', 'In attesa della connessione di un client')
            self.graphic_generation(width, height)

            try:
                self.clientSocket, self.address = SocketFunction.server_waiting_for_connection(self.serverSocket)
            except socket.error:
                messagebox.showerror('Errore', 'Problemi nella connessione col client')

            self.chatArea.config(state='normal')
            self.chatArea.insert('end', '{SISTEMA}Connessione da parte di: ' + str(self.address) + '{SISTEMA}\n')
            self.chatArea.yview('end')
            self.chatArea.config(state='disabled')

            self.clientUsername = self.username_exchange()
            self.exchange_word_server()

            receivingThread = Thread(target=self.receive_message)
            receivingThread.start()
        else:
            self.clientSocket = SocketFunction.socket_tcp_generation()
            try:
                SocketFunction.client_connection(self.clientSocket, self.__serverName, self.__serverPort)
            except socket.error:
                messagebox.showwarning('Attenzione', 'Non sembra esserci nessun server in ascolto!')
                choice_window = choiceWindow(200, 200)
                choice_window.mainloop()
                return

            self.graphic_generation(width, height)

            self.clientUsername = self.username_exchange()
            self.exchange_word_client()

            receivingThread = Thread(target=self.receive_message)
            receivingThread.start()

    def graphic_generation(self, width, height):
        self.__width = width
        self.__height = height

        self.master.title('Chat di '+self.__username)
        self.__username += '>'
        self.master.geometry("%sx%s" % (width, height))
        self.master.resizable(False, False)

        self.image = Image.open("Resources/Images/background.jpg")
        self.img_copy = self.image.copy()
        self.background_image = ImageTk.PhotoImage(self.image)
        self.background = tk.Label(self.master, image=self.background_image)
        self.background.pack(fill=tk.BOTH, expand=tk.YES)
        self.background.bind('<Configure>', self._resize_image)

        self.frame = tk.Frame(self.master, bg='#6016a2', bd=5)
        self.frame.place(relx=0.5, rely=0.88, relwidth=0.75, relheight=0.100, anchor='n')

        self.chatArea = tk.scrolledtext.ScrolledText(self.master)
        self.chatArea.place(relx=0.5, rely=0.100, relwidth=0.75, relheight=0.725, anchor='n')
        self.chatArea.config(state='disabled')

        self.entry = tk.Entry(self.master, font=40)
        self.entry.place(relx=0.135, rely=0.8925, relwidth=0.55, relheight=0.075)

        self.sendButton = tk.Button(self.master, text='Invio', command=lambda: self.send_message(self.entry.get()))
        self.sendButton.place(relx=0.70, rely=0.8925, relwidth=0.165, relheight=0.075)

    def username_exchange(self):
        try:
            SocketFunction.send(self.clientSocket, self.__username)
            return SocketFunction.receive(self.clientSocket, self.__buffer)
        except socket.error:
            messagebox.showerror('Errore', 'Errore in invio o ricezione del messaggio')
            return

    def exchange_word_server(self):
        self.__word = SocketFunction.receive(self.clientSocket, self.__buffer)

    def exchange_word_client(self):
        SocketFunction.send(self.clientSocket, self.__word)

    def send_message(self, message):
        if '' != message:
            self.entry.delete(0, tk.END)
            self.chatArea.config(state='normal')
            self.chatArea.insert('end', (self.__username + message + '\n'))
            self.chatArea.yview('end')
            self.chatArea.config(state='disabled')
            try:
                matrix = Cr.generating_coding_matrix(self.__word, message)
                encrypted_message = Cr.encrypt(self.__word, matrix)
                self.show_matrix(matrix, self.__word, 'c')
                SocketFunction.send(self.clientSocket, encrypted_message)
            except socket.error:
                messagebox.showerror('Errore', 'Errore in invio')
                return

    def receive_message(self):
        while True:
            try:
                message = SocketFunction.receive(self.clientSocket, self.__buffer)
                matrix = Cr.generating_decoding_matrix(self.__word, message)
                message = Cr.decrypt(matrix)
            except socket.error:
                messagebox.showerror('Errore', 'Errore in ricezione')
                return
            self.chatArea.config(state='normal')
            self.chatArea.insert('end', (self.clientUsername + message + '\n'))
            self.chatArea.yview('end')
            self.chatArea.config(state='disabled')

            if 'bye' == message:
                SocketFunction.send(self.clientSocket, 'bye')
                SocketFunction.client_close(self.clientSocket)
                return

            self.show_matrix(matrix, self.__word, 'd')

    def show_matrix(self, matrix, word, choice):
        self.frame.place_forget()
        self.chatArea.place_forget()
        self.entry.place_forget()
        self.sendButton.place_forget()

        self.matrixFrame = tk.Frame(self.master, bg='#6016a2', bd=5)
        self.matrixFrame.place(relx=0.5, rely=0.100, relwidth=0.75, relheight=0.725, anchor='n')

        fontStyle = tf.Font(family='Calibri', size=16)
        fontStyle2 = tf.Font(family='Arial', size=12)

        c = 0
        for item in word:
            self.label = tk.Label(self.matrixFrame, text=item, font=fontStyle, bg='#6016a2', bd=5)
            self.label.grid(row=0, column=c)
            c += 1

        if 'c' == choice:
            k = 0
            for lists in matrix:
                c = 1
                for item in lists:
                    self.label = tk.Label(self.matrixFrame, text=item, font=fontStyle2, bg='#6016a2', bd=5)
                    self.label.grid(row=c, column=k)
                    c += 1
                k += 1
        else:
            k = 1
            for lists in matrix:
                c = 0
                for item in lists:
                    self.label = tk.Label(self.matrixFrame, text=item, font=fontStyle2, bg='#6016a2', bd=5)
                    self.label.grid(row=k, column=c)
                    c += 1
                k += 1

        self.goBackButton = tk.Button(self.matrixFrame, text='Torna ai messaggi', command=self.go_back_to_chat)
        self.goBackButton.place(relx=0.5, rely=0.88, relwidth=0.75, relheight=0.100, anchor='n')

    def go_back_to_chat(self):
        self.goBackButton.destroy()
        self.label.destroy()
        self.matrixFrame.destroy()

        self.frame.place(relx=0.5, rely=0.88, relwidth=0.75, relheight=0.100, anchor='n')
        self.chatArea.place(relx=0.5, rely=0.100, relwidth=0.75, relheight=0.725, anchor='n')
        self.entry.place(relx=0.135, rely=0.8925, relwidth=0.55, relheight=0.075)
        self.sendButton.place(relx=0.70, rely=0.8925, relwidth=0.165, relheight=0.075)

    def _resize_image(self, event):
        new_width = self.__width
        new_height = self.__height

        self.image = self.img_copy.resize((new_width, new_height))

        self.background_image = ImageTk.PhotoImage(self.image)
        self.background.configure(image=self.background_image)


def __main__():
    choice_window = choiceWindow(200, 200)
    choice_window.mainloop()


if __name__ == "__main__":
    __main__()
