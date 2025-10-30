# Plant_Growth_Index
# 🌱 Micro:bit Growth Monitor

A Python desktop app that visualizes plant growth conditions in real time based on **temperature** and **light** data sent from a **Micro:bit**.  
When the environment is ideal, the leaf appears **bright and vivid green**; when conditions worsen, it turns into a **darker, duller green** 🍃🌿

---

## 🧩 Overview
- Receives `temperature` and `light` values via serial communication from a Micro:bit  
- Calculates a **Growth Index (0–100)** representing plant growth conditions  
- Displays real-time sensor data and a color-changing **leaf image** using Tkinter + Pillow  
- Great for environmental sensing, IoT demos, or educational projects

---

## 🎨 Leaf Color Logic
The leaf’s **brightness** and **saturation** are adjusted according to the Growth Index.

| Growth Index | Appearance | Meaning |
|---------------|-------------|----------|
| 80–100 | 🌿 Bright vivid green | Ideal environment |
| 40–79 | 🍃 Medium green | Moderate condition |
| 0–39 | 🌲 Dark green | Poor condition |

The app does **not** switch to red or brown.  
Instead, it keeps the same green hue and varies only the **vividness and brightness**, resulting in a natural and realistic color transition.  
Internally, this is achieved using Pillow’s `ImageEnhance.Color` and `ImageEnhance.Brightness` functions.

---

## 🌿 Growth Index Calculation

| Parameter | Description |
|------------|-------------|
| Temperature | Ideal: 25 °C (scored within 15–35 °C range) |
| Light | Ideal: 200 or higher (normalized to 1.0) |
| Growth Index | Average of temperature and light scores × 100 |

**Formula:**
```python
temp_score = max(0, 1 - abs(temp - 25) / 10)
light_score = min(light / 200, 1.0)
growth_index = (temp_score * 0.5 + light_score * 0.5) * 100
