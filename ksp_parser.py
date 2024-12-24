import krpc
import time
import json
import math

turn_start_altitude = 250
turn_end_altitude = 45000
target_altitude = 160000
srbs_drop_altitude = 26000

conn = krpc.connect(name='Запуск на орбиту')
vessel = conn.space_center.active_vessel

# Настройка потоков для телеметрии
ut = conn.add_stream(getattr, conn.space_center, 'ut')
altitude = conn.add_stream(getattr, vessel.flight(), 'mean_altitude')
apoapsis = conn.add_stream(getattr, vessel.orbit, 'apoapsis_altitude')

# Список для записи телеметрии
flight_data = []

my_start_time = ut()

# Функция записи телеметрии
def record_telemetry():
    fuel_mass = vessel.resources.amount("LiquidFuel")
    oxidizer_mass = vessel.resources.amount("Oxidizer")
    data = {
        "time": ut() - my_start_time,
        "altitude": altitude(),
        "speed": vessel.flight(vessel.orbit.body.reference_frame).speed,
        "mass": vessel.mass,
        "fuel_mass": fuel_mass,
        "oxidizer_mass": oxidizer_mass
        }
    flight_data.append(data)
    time.sleep(0.1)

# Предстартовая настройка
vessel.control.sas = False
vessel.control.rcs = False
vessel.control.throttle = 1.0


# Активация первой ступени
vessel.control.activate_next_stage()
vessel.auto_pilot.engage()
vessel.auto_pilot.target_pitch_and_heading(90, 90)

# Основной цикл подъема
stage = 1
turn_angle = 0
srbs_separated = False
stage_1_separated = False
while True:

    if turn_start_altitude < altitude() < turn_end_altitude:
        frac = (altitude() - turn_start_altitude) / (turn_end_altitude - turn_start_altitude)
        new_turn_angle = frac * 90
        if abs(new_turn_angle - turn_angle) > 0.5:
            turn_angle = new_turn_angle
            vessel.auto_pilot.target_pitch_and_heading(90 - turn_angle, 90)

    # Отделение ускорителей при их израсходовании
    if not srbs_separated and altitude() > srbs_drop_altitude:
        print("Ускорители отделены")
        vessel.control.throttle = 0.0
        vessel.control.activate_next_stage()  # Отделение ускорителей
        time.sleep(0.5)
        vessel.control.throttle = 1.0
        srbs_separated = True

    # Снижение тяги при приближении к целевому апоцентру
    if apoapsis() > target_altitude * 0.9:
        print('Приближение к целевому апоцентру')
        break

    # Запись телеметрии
    record_telemetry()

# Отключение двигателей при достижении целевого апоцентра
vessel.control.throttle = 0.25
while apoapsis() < target_altitude:
    record_telemetry()
print('Целевой апоцентр достигнут')
vessel.control.throttle = 0.0


# Ожидание выхода из атмосферы
print('Движение в космос')
while altitude() < 70500:
    record_telemetry()

# Планирование маневра стабилизации орбиты (уравнение Вис-Вива)
print('Планирование маневра стабилизации орбиты')
mu = vessel.orbit.body.gravitational_parameter
r = vessel.orbit.apoapsis
a1 = vessel.orbit.semi_major_axis
a2 = r
v1 = math.sqrt(mu*((2./r)-(1./a1)))
v2 = math.sqrt(mu*((2./r)-(1./a2)))
delta_v = v2 - v1
node = vessel.control.add_node(
    ut() + vessel.orbit.time_to_apoapsis, prograde=delta_v)

# Расчет времени работы двигателя (уравнение Циолковского)
F = vessel.available_thrust
Isp = vessel.specific_impulse * 9.82
m0 = vessel.mass
m1 = m0 / math.exp(delta_v/Isp)
flow_rate = F / Isp
burn_time = (m0 - m1) / flow_rate

# Наведение корабля
print('Наведение корабля для стабилизации орбиты')
vessel.auto_pilot.reference_frame = node.reference_frame
vessel.auto_pilot.target_direction = (0, 1, 0)
vessel.auto_pilot.wait()

# Ожидание перед маневром
print('Ожидание начала стабилизации орбиты')
burn_ut = ut() + vessel.orbit.time_to_apoapsis - (burn_time/2.)
lead_time = 5
conn.space_center.warp_to(burn_ut - lead_time)

# Выполнение маневра
time_to_apoapsis = conn.add_stream(getattr, vessel.orbit, 'time_to_apoapsis')
while time_to_apoapsis() - (burn_time / 2.0) > 0:
    record_telemetry()

vessel.control.throttle = 1.0
time.sleep(burn_time - 0.1)

vessel.control.throttle = 0.05
remaining_burn = conn.add_stream(node.remaining_burn_vector, node.reference_frame)

#Добавляем защитный таймер, чтобы цикл не застрял
start_time = time.time()
timeout = 5  # Максимальное время ожидания в секундах

while remaining_burn()[1] > 0.1:  # Устанавливаем небольшой порог вместо проверки на 0
    record_telemetry()
    if time.time() - start_time > timeout:
        break

vessel.control.throttle = 0.0
node.remove()

time_after = ut()

while ut() - time_after < 100:
    record_telemetry()

# Запись данных телеметрии в JSON
output_file = "flight_data.json"
with open(output_file, "w") as f:
    json.dump(flight_data, f, indent=4)

print(f"Данные полета сохранены в файл: {output_file}")