import os
import sys
import subprocess
import glob
import threading
import yt_dlp
from tkinter import Tk, messagebox, Label, Button, StringVar, Entry, Frame, ttk, DoubleVar

class ConvertidorMP3:
    def __init__(self):
        self.root = Tk()
        self.root.title("Convertidor Video a MP3")
        self.root.geometry("580x310")
        self.root.resizable(False, False)
        
        self.url_var = StringVar()
        self.status_var = StringVar()
        self.status_var.set("Pega un enlace de YouTube u otra plataforma")
        self.progress_var = DoubleVar()
        self.detail_var = StringVar()
        self.detail_var.set("")
        
        if getattr(sys, 'frozen', False):
            self.carpeta_proyecto = r"C:\dev\convertidormp3"
        else:
            self.carpeta_proyecto = os.path.dirname(os.path.abspath(__file__))
        
        self.carpeta_musica = os.path.join(self.carpeta_proyecto, "musica")
        os.makedirs(self.carpeta_musica, exist_ok=True)
        
        self.convirtiendo = False
        self.ultimo_archivo = None
        self.crear_interfaz()
    
    def crear_interfaz(self):
        main_frame = Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        Label(main_frame, text="Convertidor Video a MP3", font=("Arial", 14, "bold")).pack(pady=(0, 15))
        
        Label(main_frame, text="URL del video o playlist:", anchor="w").pack(fill="x")
        Entry(main_frame, textvariable=self.url_var, width=70).pack(pady=(0, 10))
        
        frame_botones = Frame(main_frame)
        frame_botones.pack(pady=5)
        
        self.btn_convertir = Button(frame_botones, text="Convertir a MP3", command=self.iniciar_conversion, bg="#4CAF50", fg="white", height=2, width=15)
        self.btn_convertir.pack(side="left", padx=5)
        
        self.btn_reproducir = Button(frame_botones, text="Reproducir", command=self.reproducir, bg="#2196F3", fg="white", height=2, width=15, state="disabled")
        self.btn_reproducir.pack(side="left", padx=5)
        
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100, length=500)
        self.progress_bar.pack(pady=(5, 2))
        
        Label(main_frame, textvariable=self.status_var, fg="gray").pack()
        Label(main_frame, textvariable=self.detail_var, fg="#333", font=("Arial", 8)).pack()
    
    def progress_hook(self, d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded = d.get('downloaded_bytes', 0)
            if total > 0:
                porcentaje = (downloaded / total) * 100
                self.progress_var.set(porcentaje)
            
            velocidad = d.get('_speed_str', '')
            eta = d.get('_eta_str', '')
            self.detail_var.set(f"Velocidad: {velocidad} | Tiempo restante: {eta}")
            self.root.update_idletasks()
        
        elif d['status'] == 'finished':
            self.progress_var.set(100)
            self.detail_var.set("Convirtiendo a MP3...")
            self.root.update_idletasks()
    
    def iniciar_conversion(self):
        if self.convirtiendo:
            return
        
        url = self.url_var.get().strip()
        
        if not url:
            messagebox.showerror("Error", "Ingresa una URL")
            return
        
        self.convirtiendo = True
        self.btn_convertir.config(state="disabled", bg="gray")
        self.btn_reproducir.config(state="disabled")
        self.progress_var.set(0)
        
        thread = threading.Thread(target=self.convertir, args=(url,), daemon=True)
        thread.start()
    
    def convertir(self, url):
        try:
            self.status_var.set("Obteniendo información...")
            self.detail_var.set("")
            self.root.update_idletasks()
            
            archivos_antes = set(glob.glob(os.path.join(self.carpeta_musica, "*.mp3")))
            
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': os.path.join(self.carpeta_musica, '%(title)s.%(ext)s'),
                'js_runtimes': {'node': {}},
                'ignoreerrors': True,
                'progress_hooks': [self.progress_hook],
                'noplaylist': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if info is None:
                    raise Exception("No se pudo obtener información del video")
                
                es_playlist = 'entries' in info
                
                if es_playlist:
                    entries = list(info['entries'])
                    total = len(entries)
                    self.status_var.set(f"Descargando playlist: {total} videos")
                    self.detail_var.set("Preparando descarga...")
                    self.root.update_idletasks()
                    
                    ydl.download([url])
                    
                    archivos_despues = set(glob.glob(os.path.join(self.carpeta_musica, "*.mp3")))
                    archivos_nuevos = sorted(archivos_despues - archivos_antes)
                    
                    if archivos_nuevos:
                        self.ultimo_archivo = archivos_nuevos[0]
                    
                    self.status_var.set("Conversión completada")
                    self.detail_var.set(f"{total} archivos MP3 guardados en carpeta 'musica'")
                else:
                    titulo = info.get('title', 'audio')
                    self.status_var.set(f"Descargando: {titulo[:50]}...")
                    self.root.update_idletasks()
                    
                    ydl.download([url])
                    
                    archivo = os.path.join(self.carpeta_musica, f"{titulo}.mp3")
                    if os.path.exists(archivo):
                        self.ultimo_archivo = archivo
                    
                    self.status_var.set("Conversión completada")
                    self.detail_var.set(f"Guardado: {titulo}.mp3")
                
                self.btn_reproducir.config(state="normal")
            
        except Exception as e:
            self.status_var.set("Error en la conversión")
            self.detail_var.set(str(e)[:80])
        finally:
            self.convirtiendo = False
            self.btn_convertir.config(state="normal", bg="#4CAF50")
            self.root.update_idletasks()
    
    def reproducir(self):
        if self.ultimo_archivo and os.path.exists(self.ultimo_archivo):
            os.startfile(self.ultimo_archivo)
        else:
            messagebox.showerror("Error", "No se encontró el archivo para reproducir")
    
    def ejecutar(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ConvertidorMP3()
    app.ejecutar()
