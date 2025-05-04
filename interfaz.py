import tkinter as tk
from tkinter import filedialog, Label, Button, Text, ttk, messagebox
from PIL import Image, ImageTk
from detector import detectar_objetos
import threading
import os

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("🧠 Detector de Casas y Árboles")
        self.root.geometry("800x650")
        self.root.resizable(False, False)
        self.root.configure(bg="#f8f9fa")

        self.image_path = None
        self.resultado_texto = ""  # Para guardar en archivo

        # Panel de imagen
        self.image_panel = Label(self.root, bg="#cccccc")
        self.image_panel.pack(pady=(20, 10))

        # Mostrar imagen vacía gris por defecto
        imagen_vacia = Image.new("RGB", (600, 400), "#cccccc")
        img_tk = ImageTk.PhotoImage(imagen_vacia)
        self.image_panel.config(image=img_tk)
        self.image_panel.image = img_tk

        # Botones en fila
        botones_frame = tk.Frame(self.root, bg="#f8f9fa")
        botones_frame.pack(pady=5)

        boton_estilo = {
            "font": ("Arial", 12),
            "bg": "#ffffff",
            "fg": "#333333",
            "activebackground": "#e0e0e0",
            "relief": "flat",
            "bd": 1,
            "width": 20
        }

        self.btn_cargar = Button(botones_frame, text="📂 Cargar Imagen", command=self.cargar_imagen, **boton_estilo)
        self.btn_cargar.grid(row=0, column=0, padx=10)

        self.btn_escanear = Button(botones_frame, text="🔍 Escanear Imagen", command=self.iniciar_deteccion, **boton_estilo)
        self.btn_escanear.grid(row=0, column=1, padx=10)

        self.btn_guardar = Button(botones_frame, text="💾 Guardar Resultados", command=self.guardar_resultado, **boton_estilo)
        self.btn_guardar.grid(row=0, column=2, padx=10)

        # Estado + barra de progreso
        self.estado_frame = tk.Frame(self.root, bg="#f8f9fa")
        self.estado_frame.pack()

        self.estado_label = Label(self.estado_frame, text="", font=("Arial", 10), bg="#f8f9fa", fg="#555555")
        self.estado_label.pack()

        style = ttk.Style()
        style.theme_use('default')
        style.configure("TProgressbar", troughcolor='#f8f9fa', background='#4caf50', thickness=6)

        self.progress = ttk.Progressbar(self.estado_frame, mode='indeterminate', length=200)

        # Área de resultados con scroll
        resultado_frame = tk.Frame(self.root, bg="#d0d0d0", bd=2, relief="groove")
        resultado_frame.pack(padx=30, pady=20, fill="both", expand=True)

        scrollbar = tk.Scrollbar(resultado_frame)
        scrollbar.pack(side="right", fill="y")

        self.resultado = Text(
            resultado_frame,
            height=8,
            font=("Segoe UI", 11),
            bg="#ffffff",
            fg="#333333",
            wrap="word",
            bd=0,
            padx=10,
            pady=10,
            yscrollcommand=scrollbar.set
        )
        self.resultado.pack(fill="both", expand=True)
        scrollbar.config(command=self.resultado.yview)
        self.resultado.config(state="disabled")

        self.color_por_clase = {
            "casa": "#1E90FF",
            "árbol": "#228B22"
        }

    def cargar_imagen(self):
        path = filedialog.askopenfilename(filetypes=[("Imágenes", "*.png;*.jpg;*.jpeg")])
        if path:
            self.image_path = path
            self.mostrar_imagen(path)
            self.limpiar_resultado()

    def iniciar_deteccion(self):
        if not self.image_path:
            self.mostrar_mensaje("⚠️ No se ha cargado una imagen.")
            return

        self.btn_cargar.config(state="disabled")
        self.btn_escanear.config(state="disabled")
        self.btn_guardar.config(state="disabled")

        self.estado_label.config(text="⏳ Procesando imagen...")
        self.progress.pack(pady=5)
        self.progress.start()

        threading.Thread(target=self.detectar).start()

    def detectar(self):
        try:
            ruta_resultado, conteo = detectar_objetos(self.image_path)
            self.root.after(0, lambda: self.mostrar_imagen(ruta_resultado))
            self.root.after(0, lambda: self.mostrar_resultado(conteo))
        except Exception as e:
            self.root.after(0, lambda: self.mostrar_mensaje(f"❌ Error: {str(e)}"))
        finally:
            self.root.after(0, self.restaurar_interfaz)

    def restaurar_interfaz(self):
        self.progress.stop()
        self.progress.pack_forget()
        self.estado_label.config(text="")
        self.btn_cargar.config(state="normal")
        self.btn_escanear.config(state="normal")
        self.btn_guardar.config(state="normal")

    def mostrar_imagen(self, path):
        img = Image.open(path)
        img.thumbnail((600, 400))
        photo = ImageTk.PhotoImage(img)
        self.image_panel.config(image=photo)
        self.image_panel.image = photo

    def mostrar_resultado(self, conteo):
        self.resultado.config(state="normal")
        self.resultado.delete("1.0", "end")
        texto_final = ""

        if conteo:
            texto_final += "📋 Se detectaron:\n\n"
            for clase, cantidad in conteo.items():
                emoji = "🏠" if clase == "casa" else "🌳"
                nombre = f"{clase}s" if cantidad > 1 else clase
                linea = f"{emoji} {nombre.capitalize()}: {cantidad}\n"
                texto_final += linea
                self.resultado.insert("end", linea, clase)
                self.resultado.tag_configure(clase, foreground=self.color_por_clase.get(clase, "black"))
        else:
            texto_final = "⚠️ No se detectaron objetos."
            self.resultado.insert("end", texto_final)

        self.resultado_texto = texto_final  # Para guardar luego
        self.resultado.config(state="disabled")
        self.resultado.yview_moveto(0)

    def guardar_resultado(self):
        if not self.resultado_texto.strip():
            messagebox.showinfo("Sin datos", "No hay resultados para guardar.")
            return

        archivo = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Archivo de texto", "*.txt")],
            title="Guardar resultado como..."
        )
        if archivo:
            with open(archivo, "w", encoding="utf-8") as f:
                f.write(self.resultado_texto)
            messagebox.showinfo("Guardado", "✅ Resultados guardados con éxito.")

    def mostrar_mensaje(self, mensaje):
        self.resultado.config(state="normal")
        self.resultado.delete("1.0", "end")
        self.resultado.insert("end", mensaje)
        self.resultado_texto = mensaje
        self.resultado.config(state="disabled")

    def limpiar_resultado(self):
        self.resultado.config(state="normal")
        self.resultado.delete("1.0", "end")
        self.resultado_texto = ""
        self.resultado.config(state="disabled")

# Ejecutar interfaz
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
