import serial
import serial.tools.list_ports
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from PIL import Image, ImageTk, ImageEnhance

# ===============================
# 成長良数値の計算
# ===============================
def calc_growth_index(temp, light):
    """
    植物の成長良数値を計算する簡易モデル
    temp: 温度（℃）
    light: 明るさ（任意の単位）
    """
    temp_score = max(0, 1 - abs(temp - 25) / 10)  # 15〜35℃をスコア化
    light_score = min(light / 200, 1.0)            # 明るさ200以上で最大スコア
    growth_index = round((temp_score * 0.5 + light_score * 0.5) * 100, 1)
    return growth_index


# ===============================
# シリアルポート更新
# ===============================
def update_ports():
    ports = serial.tools.list_ports.comports()
    port_list = [p.device for p in ports]
    combo_port['values'] = port_list
    if port_list:
        combo_port.current(0)
    else:
        combo_port.set('（ポートなし）')


# ===============================
# シリアル通信開始
# ===============================
def start_serial():
    port = combo_port.get()
    if not port or "ポートなし" in port:
        messagebox.showerror("エラー", "シリアルポートが選択されていません。")
        return

    try:
        ser = serial.Serial(port, 115200, timeout=1)
    except Exception as e:
        messagebox.showerror("接続エラー", f"ポートに接続できません：\n{e}")
        return

    messagebox.showinfo("接続成功", f"{port} に接続しました。")
    threading.Thread(target=read_serial, args=(ser,), daemon=True).start()


# ===============================
# シリアル受信スレッド
# ===============================
def read_serial(ser):
    while True:
        try:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if not line:
                continue
            # データ例: "24.5,600"
            try:
                temp_str, light_str = line.split(",")
                temp = float(temp_str)
                light = float(light_str)
                growth = calc_growth_index(temp, light)

                # テキスト表示
                text_log.insert(tk.END, f"温度: {temp:.1f}℃, 明るさ: {light:.0f}, 成長良数: {growth}\n")
                text_log.see(tk.END)

                # 葉っぱの色を更新
                update_leaf_color(growth)

            except ValueError:
                continue
        except serial.SerialException:
            break


# ===============================
# 葉っぱの色を変える関数
# ===============================
def update_leaf_color(growth):
    """
    成長良数に応じて葉っぱの色を変える。
    0〜100: 茶色 → 黄色 → 緑 に変化
    """
    # 明度・彩度を成長に応じて変化
    factor = growth / 100.0  # 0.0〜1.0
    if factor < 0: factor = 0
    if factor > 1: factor = 1

    # 彩度を上げ、明度もわずかに調整
    enhancer_color = ImageEnhance.Color(base_leaf)
    img_colored = enhancer_color.enhance(0.5 + 1.5 * factor)  # 緑の鮮やかさ
    enhancer_bright = ImageEnhance.Brightness(img_colored)
    img_final = enhancer_bright.enhance(1 + 0.2 * factor)

    # Tkinter表示用に更新
    leaf_img = ImageTk.PhotoImage(img_final)
    label_leaf.config(image=leaf_img)
    label_leaf.image = leaf_img  # 参照保持


# ===============================
# GUI構築
# ===============================
root = tk.Tk()
root.title("MicroBit 成長良数モニタ")
root.geometry("520x600")

# --- 上部フレーム ---
frame_top = ttk.Frame(root)
frame_top.pack(pady=10)

ttk.Label(frame_top, text="シリアルポート:").grid(row=0, column=0, padx=5)
combo_port = ttk.Combobox(frame_top, width=20)
combo_port.grid(row=0, column=1, padx=5)
ttk.Button(frame_top, text="更新", command=update_ports).grid(row=0, column=2, padx=5)
ttk.Button(frame_top, text="接続開始", command=start_serial).grid(row=0, column=3, padx=5)

# --- 葉っぱ画像 ---
try:
    base_leaf = Image.open("leaf.png").resize((200, 200))
except FileNotFoundError:
    messagebox.showerror("画像エラー", "leaf.png が見つかりません。\n同じフォルダに配置してください。")
    root.destroy()
    exit()

leaf_img = ImageTk.PhotoImage(base_leaf)
label_leaf = tk.Label(root, image=leaf_img)
label_leaf.pack(pady=10)

# --- ログ出力 ---
text_log = tk.Text(root, height=14, width=60)
text_log.pack(padx=10, pady=10)

# --- 初期化 ---
update_ports()

root.mainloop()
