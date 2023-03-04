# -----------------------------------------------------------
# Класс предназначен для исчтечения жидкости из небольшого отверстия
# вертикальный цилиндрический резервуар
#
# Fires, explosions, and toxic gas dispersions :
# effects calculation and risk analysis /
# Marc J. Assael, Konstantinos E. Kakosimos.

# (C) 2023 Kuznetsov Konstantin, Kazan , Russian Federation
# email kuznetsovkm@yandex.ru
# -----------------------------------------------------------
import math

DISCHARGE = 0.62  # коэф.истечения, допускается брать 0.62 (p.53)
TEMP_TO_KELVIN = 273
MPA_TO_PA = math.pow(10, 6)  # МПа в Па
MM_TO_M = math.pow(10, -3)  # мм в м
PRESSURE_ATM = 101325  # атмосферное давление, Па
GRAVITY = 9.81  # ускорение свободного падения м/с2
PERSENT_BREAK = 0.99  # процент при котором остановить расчет


class Outflow:
    def __init__(self, volume: float, height: float, pressure: float,
                 fill_factor: float, hole_diametr: float, density: float):
        '''
        Класс предназначен для расчета истечения газа
        :param volume: - объем, м3
        :param height: - высота, м
        :param pressure: - избыточное давление давление, МПа
        :param fill_factor: - степень заполнения, м3/м3
        :param hole_diametr: - диаметр отверстия, мм
        :param density: - плотность вещества, кг/м3
        :param time_step: - временной шаг истечения, с
        '''
        self.volume = volume
        self.height = height
        self.pressure = pressure * MPA_TO_PA + PRESSURE_ATM  # перевод в абсолютное
        self.fill_factor = fill_factor
        self.hole_diametr = hole_diametr * MM_TO_M
        self.density = density
        self.time_step = 1000

    def result(self):
        mass_liquid = []  # масса жидкости в емкости, кг
        time = []  # время истечения, с
        fill_tank = []  # степень заполнения емкости при истачении, -
        height = []  # высота взлива, м
        pressure = []  # давление жидкости, Па
        flow_rate = []  # расход, кг/с
        delta_mass = []  # масса истечения за шаг времени, кг
        mass_leaking = []  # масса жидкости в проливе, кг

        time_init = 0

        while True:
            Ah = (math.pi / 4) * math.pow(self.hole_diametr, 2)
            if time_init == 0:
                mass_liquid.append(round(self.fill_factor * self.volume * self.density, 2))
                time.append(time_init)
                fill_tank.append(self.fill_factor)
                height.append(round(self.fill_factor * self.height, 2))
                pressure.append(round(self.density * GRAVITY * height[-1] + self.pressure, 2))
                flow_rate.append(round(DISCHARGE * Ah * math.sqrt(2 * (pressure[-1] - PRESSURE_ATM) * self.density), 2))
                delta_mass.append(round(flow_rate[-1] * self.time_step, 2))
                mass_leaking.append(0)

                time_init += self.time_step

            else:
                height.append(round(height[-1] * (mass_liquid[-1] - delta_mass[-1]) / mass_liquid[-1], 2))
                mass_liquid.append(round(mass_liquid[-1] - delta_mass[-1], 2))
                time.append(time_init)
                fill_tank.append(round(height[-1] / self.height, 2))
                pressure.append(round(self.density * GRAVITY * height[-1] + self.pressure, 2))
                flow_rate.append(round(DISCHARGE * Ah * math.sqrt(2 * (pressure[-1] - PRESSURE_ATM) * self.density), 2))
                delta_mass.append(round(flow_rate[-1] * self.time_step, 2))
                mass_leaking.append(sum(delta_mass))

                time_init += self.time_step

            if mass_leaking[-1] >= PERSENT_BREAK * mass_liquid[0]:
                break



        return (mass_liquid,
                time,
                fill_tank,
                height,
                pressure,
                flow_rate,
                delta_mass,
                mass_leaking)


if __name__ == '__main__':
    cls = Outflow(6000, 15, 0, 0.75, 100, 773)
    print(cls.result())
