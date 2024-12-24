import json
import matplotlib.pyplot as plt

# Функция для построения графиков
def load_flight_data(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def transform_flight_data(flight_data):
    time = [entry["time"] for entry in flight_data]
    altitude = [entry["altitude"] for entry in flight_data]
    speed = [entry["speed"] for entry in flight_data]
    mass = [entry["mass"] for entry in flight_data]
    fuel_mass = [entry.get("fuel_mass", 0) for entry in flight_data]
    oxidizer_mass = [entry.get("oxidizer_mass", 0) for entry in flight_data]
    return time, altitude, speed, mass, fuel_mass, oxidizer_mass

# Функция для построения графиков
def plot_flight_data(time, altitude, speed, mass, fuel_mass, oxidizer_mass):
    plt.figure(figsize=(12, 10))

    # График высоты
    plt.subplot(3, 2, 1)
    plt.plot(time, altitude, label="Высота", color="blue")
    plt.title("Изменение высоты")
    plt.xlabel("Время (с)")
    plt.ylabel("Высота (м)")
    plt.grid(True)
    plt.legend()

    # График скорости
    plt.subplot(3, 2, 2)
    plt.plot(time, speed, label="Скорость", color="red")
    plt.title("Изменение скорости")
    plt.xlabel("Время (с)")
    plt.ylabel("Скорость (м/с)")
    plt.grid(True)
    plt.legend()

    # График массы ракеты
    plt.subplot(3, 2, 3)
    plt.plot(time, mass, label="Масса ракеты", color="purple")
    plt.title("Изменение массы ракеты")
    plt.xlabel("Время (с)")
    plt.ylabel("Масса (кг)")
    plt.grid(True)
    plt.legend()

    # График массы топлива
    plt.subplot(3, 2, 4)
    plt.plot(time, fuel_mass, label="Масса топлива", color="green")
    plt.title("Изменение массы топлива")
    plt.xlabel("Время (с)")
    plt.ylabel("Масса топлива (кг)")
    plt.grid(True)
    plt.legend()

    # График массы окислителя
    plt.subplot(3, 2, 5)
    plt.plot(time, oxidizer_mass, label="Масса окислителя", color="orange")
    plt.title("Изменение массы окислителя")
    plt.xlabel("Время (с)")
    plt.ylabel("Масса окислителя (кг)")
    plt.grid(True)
    plt.legend()

    # Расстановка графиков
    plt.tight_layout()
    plt.show()

# Укажите путь к вашему JSON файлу
file_path = "flight_data.json"

# Загрузка данных
try:
    flight_data = load_flight_data(file_path)
    time, altitude, speed, mass, fuel_mass, oxidizer_mass = transform_flight_data(flight_data)
    # Построение графиков
    plot_flight_data(time, altitude, speed, mass, fuel_mass, oxidizer_mass)
except FileNotFoundError:
    print(f"Файл {file_path} не найден.")
except json.JSONDecodeError:
    print("Ошибка при чтении JSON файла. Проверьте его синтаксис.")
