import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
from Crypto.Cipher import DES
from Crypto.Util.Padding import pad
import numpy as np
import os

# Función para cargar la imagen
def load_image():
    global img_path
    img_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
    if img_path:
        lbl_img_path.config(text=img_path)

# Función para cifrar o descifrar la imagen
def process_image(action):
    if not img_path:
        messagebox.showwarning("Advertencia", "Por favor, selecciona una imagen.")
        return
    
    key = entry_key.get()
    iv = entry_iv.get()
    mode = mode_var.get()
    
    if len(key) != 8 or (mode != "ECB" and len(iv) != 8):
        messagebox.showerror("Error", "La clave y el vector de inicialización deben tener 8 caracteres.")
        return

    # Configurar modo de cifrado
    if mode == "ECB":
        cipher_mode = DES.MODE_ECB
    elif mode == "CBC":
        cipher_mode = DES.MODE_CBC
    elif mode == "CFB":
        cipher_mode = DES.MODE_CFB
    elif mode == "OFB":
        cipher_mode = DES.MODE_OFB
    else:
        messagebox.showerror("Error", "Modo de cifrado no soportado.")
        return
    
    try:
        aux = img_path.split("/")
        img_name = aux[-1].split(".")
        new_path = img_path.replace(aux[-1],"")

        # Leer la imagen y convertirla a un array de bytes
        img = Image.open(img_path)
        new_img = np.array(img)
        img_size = img.size

        # Nuevo nombre del archivo
        new_url = new_path + img_name[0] + action + mode + "." + img_name[-1]

        # Crear el objeto de cifrado DES
        des = None
        if mode != "ECB":
            des = DES.new(key.encode('UTF-8'), cipher_mode, iv.encode('UTF-8'))
        else:
            des = DES.new(key.encode('UTF-8'), cipher_mode)

        if action == "_e":  # Cifrado
            encrypted_body = des.encrypt(pad(new_img.tobytes(), DES.block_size))
            processed_data = np.frombuffer(encrypted_body)
        elif action == "_d":  # Descifrado
            var_aux = new_img.tobytes()
            decrypted_body = des.decrypt(var_aux)
            processed_data = np.frombuffer(decrypted_body)

        # Crear la imagen a partir de los datos procesados
        nueva_img = Image.frombuffer("RGB",img_size,processed_data)
        
        nueva_img.save(new_url)

        messagebox.showinfo("Guardado", f"Archivo guardado como {img_name[0] + action + mode + "." + img_name[-1]}")
        
    except ValueError as ve:
        messagebox.showerror("Error de Padding", f"Error al descifrar la imagen: {str(ve)}. "
                                                 f"Es posible que la clave o el modo no coincidan con el archivo.")
    except Exception as e:
        messagebox.showerror("Error", f"Error al procesar la imagen: {str(e)}")

# Interfaz gráfica
root = tk.Tk()
root.title("Cifrado y Descifrado de Imágenes con DES")

# Selección de la imagen
tk.Button(root, text="Cargar Imagen", command=load_image).pack(pady=5)
lbl_img_path = tk.Label(root, text="No se ha cargado ninguna imagen")
lbl_img_path.pack(pady=5)

# Entrada de clave y vector de inicialización
tk.Label(root, text="Clave (8 caracteres):").pack(pady=5)
entry_key = tk.Entry(root, show="*", width=10)
entry_key.pack(pady=5)

tk.Label(root, text="Vector de Inicialización (8 caracteres):").pack(pady=5)
entry_iv = tk.Entry(root, show="*", width=10)
entry_iv.pack(pady=5)

# Selección del modo de cifrado
tk.Label(root, text="Modo de Cifrado:").pack(pady=5)
mode_var = tk.StringVar(value="ECB")
tk.OptionMenu(root, mode_var, "ECB", "CBC", "CFB", "OFB").pack(pady=5)

# Botones de cifrado y descifrado
tk.Button(root, text="Cifrar Imagen", command=lambda: process_image("_e")).pack(pady=5)
tk.Button(root, text="Descifrar Imagen", command=lambda: process_image("_d")).pack(pady=5)

root.mainloop()
