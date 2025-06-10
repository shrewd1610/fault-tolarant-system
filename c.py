import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import socket
import time
import psutil
import os
from datetime import datetime

HOST = '0.0.0.0'
PORT = 65432

class MasterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Master-Slave Communication System with Core Affinity")
        self.root.geometry("800x600")

        self.client_conn = None
        self.server_socket = None
        self.running = False
        self.comm_count = 0
        self.start_time = None

        self.master_workload = tk.IntVar(value=700000)
        self.slave_workload = tk.IntVar(value=700000)

        self.set_cpu_affinity(0)
        self.setup_gui()
        self.start_cpu_monitor()

    def set_cpu_affinity(self, core):
        try:
            psutil.Process(os.getpid()).cpu_affinity([core])
        except Exception as e:
            print(f"Affinity error: {e}")

    def setup_gui(self):
        frame = ttk.Frame(self.root, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Master-Slave Communication System", font=('Helvetica', 14, 'bold')).pack()

        # CPU usage
        usage_frame = ttk.LabelFrame(frame, text="CPU Usage")
        usage_frame.pack(fill=tk.X, pady=10)

        self.master_bar = ttk.Progressbar(usage_frame, maximum=100)
        self.master_bar.pack(fill=tk.X, padx=5, pady=2)
        self.master_label = ttk.Label(usage_frame, text="Core 0 (Master): 0.0%")
        self.master_label.pack()

        self.slave_bar = ttk.Progressbar(usage_frame, maximum=100)
        self.slave_bar.pack(fill=tk.X, padx=5, pady=2)
        self.slave_label = ttk.Label(usage_frame, text="Core 1 (Slave): 0.0%")
        self.slave_label.pack()

        # Workload
        ttk.Label(frame, text="Workload Adjustment").pack()
        ttk.Label(frame, text="Master:").pack()
        tk.Scale(frame, from_=100000, to=1540000, resolution=10000,
                 variable=self.master_workload, orient=tk.HORIZONTAL).pack(fill=tk.X)

        ttk.Label(frame, text="Slave:").pack()
        tk.Scale(frame, from_=100000, to=1540000, resolution=10000,
                 variable=self.slave_workload, orient=tk.HORIZONTAL).pack(fill=tk.X)

        # Log
        self.log = scrolledtext.ScrolledText(frame, height=12)
        self.log.pack(fill=tk.BOTH, expand=True, pady=5)

        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=5)

        self.start_btn = ttk.Button(btn_frame, text="Start", command=self.start_server)
        self.start_btn.pack(side=tk.LEFT, padx=5)

        ttk.Button(btn_frame, text="Clear Log", command=lambda: self.log.delete(1.0, tk.END)).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="Exit", command=self.on_close).pack(side=tk.RIGHT, padx=5)

    def start_cpu_monitor(self):
        def monitor():
            while True:
                usage = psutil.cpu_percent(interval=1, percpu=True)
                if len(usage) >= 2:
                    self.master_bar['value'] = usage[0]
                    self.master_label.config(text=f"Core 0 (Master): {usage[0]:.1f}%")
                    self.slave_bar['value'] = usage[1]
                    self.slave_label.config(text=f"Core 1 (Slave): {usage[1]:.1f}%")
        threading.Thread(target=monitor, daemon=True).start()

    def start_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((HOST, PORT))
        self.server_socket.listen(1)
        self.log_message("Listening for slave...")
        self.start_btn.config(state=tk.DISABLED)
        threading.Thread(target=self.accept_client, daemon=True).start()

    def accept_client(self):
        self.client_conn, addr = self.server_socket.accept()
        self.log_message(f"Connected by {addr}")
        self.running = True
        self.start_time = time.time()
        threading.Thread(target=self.communication_loop, daemon=True).start()

    def simulate_work(self, n):
        acc = 0
        for i in range(n):
            acc += (i % 7) * (i % 5)
 
    def communication_loop(self):
        while self.running and (time.time() - self.start_time < 60):
            msg = f"DATA_{self.comm_count}|{self.slave_workload.get()}"
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            self.simulate_work(self.master_workload.get())
            try:
                self.client_conn.sendall(msg.encode())
                self.log_message(f"{timestamp} Master -> Slave: {msg}")
                response = self.client_conn.recv(1024).decode()
                if response:
                    self.log_message(f"{timestamp} Slave -> Master: {response}")
                    self.comm_count += 1
            except Exception as e:
                self.log_message(f"Error: {e}")
                break
            time.sleep(0.05)
        if self.client_conn:
            try:
                self.client_conn.sendall(b"EXIT")
                self.client_conn.close()
            except:
                pass
        self.log_message("Communication ended.")

    def log_message(self, msg):
        self.log.insert(tk.END, msg + "\n")
        self.log.see(tk.END)

    def on_close(self):
        try:
            if self.client_conn:
                self.client_conn.sendall(b"EXIT")
                self.client_conn.close()
        except:
            pass
        if self.server_socket:
            self.server_socket.close()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = MasterGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
