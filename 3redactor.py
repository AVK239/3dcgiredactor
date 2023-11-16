import tkinter as tk
from tkinter import simpledialog
from typing import Any

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.pyplot as plt
from numpy import ndarray, dtype


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


def draw_cube(ax, points, edge_length=2, invisible_faces=[]):
    half = edge_length / 2
    edges = [
        [points[0], points[1], points[2], points[3]],
        [points[4], points[5], points[6], points[7]],
        [points[0], points[1], points[5], points[4]],
        [points[2], points[3], points[7], points[6]],
        [points[1], points[2], points[6], points[5]],
        [points[4], points[7], points[3], points[0]]
    ]

    # Список цветов для каждой грани
    face_colors = ['cyan' if i not in invisible_faces else (0, 0, 0, 0) for i in range(len(edges))]

    cube = Poly3DCollection(edges, facecolors=face_colors, linewidths=1, edgecolors='r', alpha=.25)
    ax.add_collection3d(cube)


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



def calculate_normals(points):
    # Рассчитываем нормали для каждой грани
    normals = []
    for i in range(len(points)):
        if i < len(points) - 1:
            edge1 = points[i + 1] - points[i]
        else:
            edge1 = points[0] - points[i]
        if i < len(points) - 2:
            edge2 = points[i + 2] - points[i]
        elif i == len(points) - 2:
            edge2 = points[0] - points[i]
        else:
            edge2 = points[1] - points[i]
        normal = np.cross(edge1, edge2)
        normals.append(normal / np.linalg.norm(normal))
    return normals


def find_visible_faces(points, normals, viewer_position):
    visible_faces = []
    for i, normal in enumerate(normals):
        face_center = np.mean(points[i], axis=0)
        view_vector = viewer_position - face_center
        if np.dot(normal, view_vector) >= 0:
            visible_faces.append(i)
    return visible_faces


def perspective_projection(obj, distance):
    perspective_matrix = np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, -1 / distance],
        [0, 0, 0, 1]
    ])
    obj_homogeneous = np.hstack((obj, np.ones((obj.shape[0], 1))))
    projected = np.dot(obj_homogeneous, perspective_matrix.T)
    projected = projected[:, :-1] / projected[:, -1:]
    return projected


def apply_perspective_distance():
    try:
        new_distance = float(distance_entry.get())
        global perspective_distance
        perspective_distance = new_distance
        draw_object()

    except ValueError:
        print("Пожалуйста, введите корректное числовое значение.")




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


# Функция для применения удаления невидимых граней
def apply_backface_culling():
    global object_normals, viewer_position
    invisible_faces = []

    for i, normal in enumerate(object_normals):
        # Если нормаль направлена к наблюдателю, то грань видима, иначе - невидима
        if np.dot(normal, viewer_position) > 0:
            invisible_faces.append(i)

    # Перерисовка куба с невидимыми гранями
    draw_cube(ax, object_points, 2, invisible_faces=invisible_faces)
    canvas.draw()


# Функция для отмены удаления невидимых граней
def cancel_backface_culling():
    global object_points, object_normals
    object_points = create_cube()  # Восстанавливаем исходные координаты объекта
    object_normals = calculate_normals(object_points)  # Пересчитываем нормали
    draw_object()


# Функция для применения одноточечного перспективного преобразования
def apply_perspective_projection():
    global object_points, perspective_distance
    original_object = create_cube()  # Используем исходные координаты объекта
    object_points = perspective_projection(original_object, perspective_distance)
    draw_object()


# Функция для отмены одноточечного перспективного преобразования
def cancel_perspective_projection():
    global object_points
    object_points = create_cube()  # Восстанавливаем исходные координаты объекта
    draw_object()


def select_shape(shape):
    global object_points
    if shape == 'cube':
        object_points = create_cube()
    elif shape == 'pyramid':
        object_points = create_pyramid()
    draw_object()

def adjust_scale(ax, scale):
    # Добавляем невидимые точки для регулирования масштаба
    invisible_points = np.array([
        [-scale, -scale, -scale],
        [scale, scale, scale]
    ])
    ax.scatter(*invisible_points.T, alpha=0)  # Alpha=0 делает точки невидимыми
    print('points added')

def draw_object():
    global object_points, ax, canvas, shape_var, perspective_distance
    print("Drawing object with perspective distance:", perspective_distance)
    ax.clear()
    shape = shape_var.get()

    # Непосредственно устанавливаем пределы осей
    max_range = perspective_distance * 2
    ax.set_xlim([-max_range, max_range])
    ax.set_ylim([-max_range, max_range])
    ax.set_zlim([-max_range, max_range])

    if shape == 'cube':
        if backface_culling_enabled.get():
            visible_faces = find_visible_faces(object_points, object_normals, viewer_position)
            object_to_draw = object_points[visible_faces]
        else:
            object_to_draw = object_points

        if perspective_projection_enabled.get():
            object_to_draw = perspective_projection(object_to_draw, perspective_distance)

        draw_cube(ax, object_to_draw, 2)
    elif shape == 'pyramid':
        if backface_culling_enabled.get():
            visible_faces = find_visible_faces(object_points, object_normals, viewer_position)
            object_to_draw = object_points[visible_faces]
        else:
            object_to_draw = object_points

        if perspective_projection_enabled.get():
            object_to_draw = perspective_projection(object_to_draw, perspective_distance)

        draw_pyramid(ax, object_to_draw)

    canvas.draw()
    plt.draw()

    canvas.draw_idle()
    fig.canvas.flush_events()

root = tk.Tk()
root.title("3D Графический Редактор")
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Глобальные переменные
object_points: ndarray[Any, dtype[Any]] = create_cube()  # Начальное значение
object_normals = calculate_normals(object_points)  # Начальные нормали
viewer_position = np.array([0, 0, 10])  # Позиция наблюдателя
perspective_distance = 5  # Начальное значение
backface_culling_enabled = tk.BooleanVar()
perspective_projection_enabled = tk.BooleanVar()
backface_culling_enabled.set(False)  # Исходно отключено
perspective_projection_enabled.set(False)  # Исходно отключено

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

# Кнопка применения удаления невидимых граней
apply_backface_culling_button = tk.Button(root, text="Применить удаление невидимых граней",
                                          command=apply_backface_culling)
apply_backface_culling_button.pack(side=tk.BOTTOM)

# Кнопка отмены удаления невидимых граней
cancel_backface_culling_button = tk.Button(root, text="Отменить удаление невидимых граней",
                                           command=cancel_backface_culling)
cancel_backface_culling_button.pack(side=tk.BOTTOM)

# Кнопка применения одноточечного перспективного преобразования
apply_perspective_projection_button = tk.Button(root, text="Применить перспективное преобразование",
                                                command=apply_perspective_projection)
apply_perspective_projection_button.pack(side=tk.BOTTOM)

# Кнопка отмены одноточечного перспективного преобразования
cancel_perspective_projection_button = tk.Button(root, text="Отменить перспективное преобразование",
                                                 command=cancel_perspective_projection)
cancel_perspective_projection_button.pack(side=tk.BOTTOM)

# Создание текстового поля для ввода
distance_entry = tk.Entry(root)
distance_entry.pack(side=tk.TOP)

# Создание кнопки для применения нового расстояния перспективы
apply_button = tk.Button(root, text="Применить расстояние перспективы", command=apply_perspective_distance)
apply_button.pack(side=tk.TOP)

def on_slider_change(val):
    global perspective_distance
    perspective_distance = float(val)
    draw_object()

# Добавление ползунка
perspective_slider = tk.Scale(root, from_=1, to=20, orient=tk.HORIZONTAL,
                              label="Расстояние перспективы", command=on_slider_change)
perspective_slider.set(perspective_distance)  # Установка начального значения ползунка
perspective_slider.pack(side=tk.BOTTOM)



root.mainloop()
