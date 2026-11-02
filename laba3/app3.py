import streamlit as st
import plotly.graph_objects as go
import time

st.set_page_config(page_title="Лабораторная 3: Растеризация", layout="wide")
st.title("Лабораторная работа 3. Базовые растровые алгоритмы")
st.write("Построение отрезков и окружностей на дискретной сетке (пикселях).")

# ==========================================
# 1. АЛГОРИТМЫ (Вся математика здесь)
# ==========================================

def step_by_step(x1, y1, x2, y2):
    """Пошаговый алгоритм (школьное уравнение y = kx + b)"""
    points = []
    if x1 == x2 and y1 == y2: return [(x1, y1)]
    
    dx = x2 - x1
    dy = y2 - y1
    
    if abs(dx) >= abs(dy): # Линия больше горизонтальная
        if x1 > x2: x1, x2, y1, y2 = x2, x1, y2, y1 # Всегда рисуем слева направо
        k = dy / dx if dx != 0 else 0
        b = y1 - k * x1
        for x in range(x1, x2 + 1):
            points.append((x, round(k * x + b)))
    else: # Линия больше вертикальная
        if y1 > y2: x1, x2, y1, y2 = x2, x1, y2, y1 # Всегда рисуем снизу вверх
        k = dx / dy if dy != 0 else 0
        b = x1 - k * y1
        for y in range(y1, y2 + 1):
            points.append((round(k * y + b), y))
    return points

def dda(x1, y1, x2, y2):
    """Алгоритм ЦДА (Цифровой дифференциальный анализатор)"""
    points = []
    dx = x2 - x1
    dy = y2 - y1
    L = max(abs(dx), abs(dy)) # Количество шагов
    if L == 0: return [(x1, y1)]
    
    x_inc = dx / L
    y_inc = dy / L
    
    x, y = x1, y1
    for _ in range(L + 1):
        points.append((round(x), round(y)))
        x += x_inc
        y += y_inc
    return points

def bresenham_line(x1, y1, x2, y2):
    """Алгоритм Брезенхема (Только целые числа, самый быстрый!)"""
    points = []
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy

    while True:
        points.append((x1, y1))
        if x1 == x2 and y1 == y2:
            break
        e2 = err * 2
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy
    return points

def bresenham_circle(xc, yc, r):
    """Алгоритм Брезенхема для окружности"""
    points = set() # set используем, чтобы избежать дубликатов точек
    x, y = 0, r
    d = 3 - 2 * r # Стартовый параметр принятия решения
    
    while x <= y:
        # Круг симметричен, рисуем сразу 8 точек во всех октантах
        points.update([
            (xc+x, yc+y), (xc-x, yc+y), (xc+x, yc-y), (xc-x, yc-y),
            (xc+y, yc+x), (xc-y, yc+x), (xc+y, yc-x), (xc-y, yc-x)
        ])
        if d < 0:
            d = d + 4 * x + 6
        else:
            d = d + 4 * (x - y) + 10
            y -= 1
        x += 1
    return list(points)

# ==========================================
# 2. ИНТЕРФЕЙС (Боковая панель)
# ==========================================

st.sidebar.header("Параметры фигуры")
figure_type = st.sidebar.radio("Что рисуем?", ["Отрезок", "Окружность"])

if figure_type == "Отрезок":
    algo = st.sidebar.selectbox("Выберите алгоритм:", ["Пошаговый", "ЦДА", "Брезенхем (линия)"])
    st.sidebar.subheader("Координаты начала (X1, Y1)")
    col1, col2 = st.sidebar.columns(2)
    x1 = col1.number_input("X1", value=2, step=1)
    y1 = col2.number_input("Y1", value=2, step=1)
    
    st.sidebar.subheader("Координаты конца (X2, Y2)")
    col3, col4 = st.sidebar.columns(2)
    x2 = col3.number_input("X2", value=15, step=1)
    y2 = col4.number_input("Y2", value=9, step=1)
else:
    algo = "Брезенхем (окружность)"
    st.sidebar.subheader("Центр окружности (Xc, Yc)")
    col1, col2 = st.sidebar.columns(2)
    xc = col1.number_input("Xc", value=10, step=1)
    yc = col2.number_input("Yc", value=10, step=1)
    r = st.sidebar.number_input("Радиус (R)", value=7, min_value=1, step=1)

# ==========================================
# 3. ВЫПОЛНЕНИЕ И ЗАМЕР ВРЕМЕНИ
# ==========================================

# Чтобы замерить время точно, мы прогоним алгоритм 1000 раз
iterations = 1000
start_time = time.perf_counter_ns()

for _ in range(iterations):
    if figure_type == "Отрезок":
        if algo == "Пошаговый":
            pixels = step_by_step(x1, y1, x2, y2)
        elif algo == "ЦДА":
            pixels = dda(x1, y1, x2, y2)
        else:
            pixels = bresenham_line(x1, y1, x2, y2)
    else:
        pixels = bresenham_circle(xc, yc, r)

end_time = time.perf_counter_ns()

# Время одного выполнения в микросекундах (1 мкс = 0.000001 сек)
time_taken_us = (end_time - start_time) / iterations / 1000

# Разделяем координаты x и y для графика
x_coords = [p[0] for p in pixels]
y_coords = [p[1] for p in pixels]

# ==========================================
# 4. ОТРИСОВКА КРАСИВОГО ГРАФИКА
# ==========================================

st.subheader(f"Результат работы: {algo}")

# Создаем интерактивный график
fig = go.Figure()

# Добавляем наши пиксели (рисуем их как синие квадратики)
fig.add_trace(go.Scatter(
    x=x_coords, y=y_coords,
    mode='markers',
    marker=dict(symbol='square', size=20, color='royalblue', line=dict(width=1, color='darkblue')),
    name="Пиксели"
))

# Добавляем идеальную линию (красную), чтобы сравнить пиксели с идеалом
if figure_type == "Отрезок":
    fig.add_trace(go.Scatter(x=[x1, x2], y=[y1, y2], mode='lines', line=dict(color='red', width=2), name="Идеальная линия"))

# Настраиваем сетку (тетрадь в клеточку)
max_val = max(max(x_coords, default=0), max(y_coords, default=0)) + 5
min_val = min(min(x_coords, default=0), min(y_coords, default=0)) - 5

fig.update_layout(
    xaxis=dict(title="Ось X", dtick=1, showgrid=True, gridcolor='lightgray', zeroline=True, zerolinecolor='black', range=[min_val, max_val]),
    yaxis=dict(title="Ось Y", dtick=1, showgrid=True, gridcolor='lightgray', zeroline=True, zerolinecolor='black', range=[min_val, max_val], scaleanchor="x", scaleratio=1),
    plot_bgcolor='white',
    width=800,
    height=800,
    title="Дискретная сетка (Масштабируется колесиком мыши)"
)

st.plotly_chart(fig, use_container_width=True)

# Вывод времени и информации
st.success(f"⏱ **Среднее время выполнения:** {time_taken_us:.3f} микросекунд")
st.info("💡 **Как целочисленные координаты привязаны к сетке?**\n\nМатематическая точка (X, Y) является центром квадрата (пикселя). На графике пересечения линий сетки — это целочисленные координаты пикселей. Мы закрашиваем квадратик ровно вокруг этого пересечения.")