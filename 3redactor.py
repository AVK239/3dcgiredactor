import tkinter as tk
from tkinter import simpledialog
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.pyplot as plt


def rotate_x(obj, angle):
    """ Поворот объекта вокруг оси X. """
    rad = np.radians(angle)
    rotation_matrix = np.array([
        [1, 0, 0],
        [0, np.cos(rad), -np.sin(rad)],
        [0, np.sin(rad), np.cos(rad)]
    ])
    return np.dot(obj, rotation_matrix.T)


def rotate_y(obj, angle):
    """ Поворот объекта вокруг оси Y. """
    rad = np.radians(angle)
    rotation_matrix = np.array([
        [np.cos(rad), 0, np.sin(rad)],
        [0, 1, 0],
        [-np.sin(rad), 0, np.cos(rad)]
    ])
    return np.dot(obj, rotation_matrix.T)

def rotate_z(obj, angle):
    """ Поворот объекта вокруг оси Z. """
    rad = np.radians(angle)
    rotation_matrix = np.array([
        [np.cos(rad), -np.sin(rad), 0],
        [np.sin(rad), np.cos(rad), 0],
        [0, 0, 1]
    ])
    return np.dot(obj, rotation_matrix.T)

def translate(obj, shift):
    """ Перемещение объекта. """
    return obj + shift

# Кнопка масштабирования

def scale(obj, factor):
    """ Масштабирование объекта. """
    scaling_matrix = np.array([
        [factor, 0, 0],
        [0, factor, 0],
        [0, 0, factor]
    ])
    return obj @ scaling_matrix


def create_pyramid(base_size=2, height=3):
    half_base = base_size / 2
    points = np.array([
        [-half_base, -half_base, 0],
        [half_base, -half_base, 0],
        [half_base, half_base, 0],
        [-half_base, half_base, 0],
        [0, 0, height]
    ])
    return points

def create_cube(edge_length=2):
    half = edge_length / 2
    points = np.array([
        [-half, -half, -half],
        [half, -half, -half],
        [half, half, -half],
        [-half, half, -half],
        [-half, -half, half],
        [half, -half, half],
        [half, half, half],
        [-half, half, half]
    ])
    return points

def draw_cube(ax, points, edge_length=2):
    half = edge_length / 2

    edges = [
        [points[0], points[1], points[2], points[3]],
        [points[4], points[5], points[6], points[7]],
        [points[0], points[1], points[5], points[4]],
        [points[2], points[3], points[7], points[6]],
        [points[1], points[2], points[6], points[5]],
        [points[4], points[7], points[3], points[0]]
    ]

    ax.add_collection3d(Poly3DCollection(edges, facecolors='cyan', linewidths=1, edgecolors='r', alpha=.25))
    ax.set_xlim([-half-1, half+1])
    ax.set_ylim([-half-1, half+1])
    ax.set_zlim([-half-1, half+1])

def draw_pyramid(ax, points, base_size=2, height=3):
    edges = [
        [points[0], points[1], points[2], points[3], points[0]],
        [points[0], points[4]],
        [points[1], points[4]],
        [points[2], points[4]],
        [points[3], points[4]]
    ]
    for edge in edges:
        ax.plot(*zip(*edge), color='b')
    ax.set_xlim([-base_size, base_size])
    ax.set_ylim([-base_size, base_size])
    ax.set_zlim([0, height + 1])

# Выбор объекта




# Кнопка перемещения
def apply_translation():
    global object_points
    shift_x = simpledialog.askfloat("Input", "Смещение по X:", parent=root)
    shift_y = simpledialog.askfloat("Input", "Смещение по Y:", parent=root)
    shift_z = simpledialog.askfloat("Input", "Смещение по Z:", parent=root)
    object_points = translate(object_points, np.array([shift_x, shift_y, shift_z]))
    draw_object()



def apply_scaling():
    global object_points
    factor = simpledialog.askfloat("Input", "Масштабирующий коэффициент:", parent=root)
    object_points = scale(object_points, factor)
    draw_object()



def apply_rotation():
    global object_points, ax, canvas

    # Запрашиваем у пользователя углы вращения для каждой оси
    angle_x = simpledialog.askfloat("Вращение", "Угол вращения вокруг оси X:", parent=root)
    angle_y = simpledialog.askfloat("Вращение", "Угол вращения вокруг оси Y:", parent=root)
    angle_z = simpledialog.askfloat("Вращение", "Угол вращения вокруг оси Z:", parent=root)

    # Проверяем, что пользователь ввел значения
    if angle_x is not None and angle_y is not None and angle_z is not None:
        # Применяем вращение
        object_points = rotate_x(object_points, angle_x)
        object_points = rotate_y(object_points, angle_y)
        object_points = rotate_z(object_points, angle_z)

        # Перерисовываем объект
        draw_object()

def select_shape(shape):
    global object_points
    if shape == 'cube':
        object_points = create_cube()
    elif shape == 'pyramid':
        object_points = create_pyramid()
    draw_object()

def draw_object():
    global object_points, ax, canvas
    ax.clear()

    shape = shape_var.get()
    if shape == 'cube':
        draw_cube(ax, object_points, 2)
    elif shape == 'pyramid':
        draw_pyramid(ax, object_points)

    canvas.draw()



# Инициализация object_points
object_points = create_cube()  # Начальное значение

root = tk.Tk()
root.title("3D Графический Редактор")
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

canvas = FigureCanvasTkAgg(fig, master=root)
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

shape_var = tk.StringVar(root)
shape_var.set("cube")
shape_menu = tk.OptionMenu(root, shape_var, "cube", "pyramid", command=select_shape)
shape_menu.pack(side=tk.TOP)

rotate_button = tk.Button(root, text="Применить вращение", command=apply_rotation)
rotate_button.pack(side=tk.BOTTOM)

scale_button = tk.Button(root, text="Масштабирование", command=apply_scaling)
scale_button.pack(side=tk.BOTTOM)

translate_button = tk.Button(root, text="Перемещение", command=apply_translation)
translate_button.pack(side=tk.BOTTOM)

draw_object()
root.mainloop()