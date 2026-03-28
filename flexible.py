import math
import tkinter as tk
from tkinter import messagebox

# ==============================
# ฟังก์ชันคำนวณ SN
# ==============================
def calculate_SN(W18, Zr, So, delta_PSI, Mr):
    SN = 3.0  
    
    for i in range(1000):
        term1 = Zr * So
        term2 = 9.36 * math.log10(SN + 1)
        term3 = -0.20
        term4 = math.log10(delta_PSI / (4.2 - 1.5)) / (0.4 + (1094 / (SN + 1)**5.19))
        term5 = 2.32 * math.log10(Mr)
        term6 = -8.07

        logW18_calc = term1 + term2 + term3 + term4 + term5 + term6
        W18_calc = 10 ** logW18_calc

        error = W18 - W18_calc
        SN = SN + error / 1e7
        
        if abs(error) < 1e3:
            break

    return SN


# ==============================
# คำนวณความหนาแต่ละชั้น
# ==============================
def calculate_layers(SN, a1=0.44, a2=0.14, a3=0.11, m2=1.0, m3=1.0):
    D1 = SN * 0.4 / a1
    D2 = SN * 0.3 / (a2 * m2)
    D3 = SN * 0.3 / (a3 * m3)
    return D1, D2, D3


# ==============================
# ฟังก์ชันปุ่มคำนวณ
# ==============================
def run_calculation():
    try:
        W18 = float(entry_W18.get())
        Zr = float(entry_Zr.get())
        So = float(entry_So.get())
        delta_PSI = float(entry_PSI.get())
        Mr = float(entry_Mr.get())

        SN = calculate_SN(W18, Zr, So, delta_PSI, Mr)
        D1, D2, D3 = calculate_layers(SN)

        result_text.set(
            f"SN = {SN:.2f}\n"
            f"AC = {D1:.2f} in\n"
            f"Base = {D2:.2f} in\n"
            f"Subbase = {D3:.2f} in"
        )

    except:
        messagebox.showerror("Error", "กรุณากรอกตัวเลขให้ถูกต้อง")


# ==============================
# GUI
# ==============================
root = tk.Tk()
root.title("AASHTO 1993 Pavement Design")
root.geometry("400x450")

# Input fields
tk.Label(root, text="W18 (ESAL)").pack()
entry_W18 = tk.Entry(root)
entry_W18.pack()

tk.Label(root, text="Zr (Reliability)").pack()
entry_Zr = tk.Entry(root)
entry_Zr.pack()

tk.Label(root, text="So").pack()
entry_So = tk.Entry(root)
entry_So.pack()

tk.Label(root, text="ΔPSI").pack()
entry_PSI = tk.Entry(root)
entry_PSI.pack()

tk.Label(root, text="Mr (psi)").pack()
entry_Mr = tk.Entry(root)
entry_Mr.pack()

# ปุ่มคำนวณ
tk.Button(root, text="คำนวณ", command=run_calculation, bg="green", fg="white").pack(pady=10)

# ผลลัพธ์
result_text = tk.StringVar()
tk.Label(root, textvariable=result_text, font=("Arial", 12)).pack(pady=20)

root.mainloop()
