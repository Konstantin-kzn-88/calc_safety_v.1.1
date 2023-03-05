# -----------------------------------------------------------
# Класс предназначен для исчтечения жидкости из небольшого отверстия
# трубопровод с профилем
#
# (C) 2023 Kuznetsov Konstantin, Kazan , Russian Federation
# email kuznetsovkm@yandex.ru
# -----------------------------------------------------------

import math

GRAVITY = 9.81  # ускорение свободного падения м/с2
DISCHARGE = 0.6  # коэф.истечения, допускается брать 0.6 (p.31 РБ оценка риска на нефтедобыче)
PRESSURE_ATM = 101325  # атмосферное давление, Па
MPA_TO_PA = math.pow(10, 6)  # МПа в Па
MM_TO_M = math.pow(10, -3)  # мм в м


class Outflow_in_one_section_pipe:
    def __init__(self, common_pressure: float, z1: float, z2: float, diametr: float, density: float, lenght: float,
                 hole: float, time_shutdown: float, time_closing: float):
        '''
        Класс предназначен для оценки количества опасного вещества
        истекающего из трубопровода в напорном и безнапорном режиме
        :param common_pressure: начальное давление, МПа
        :param z1: высотная отметка, м
        :param z2: высотная отметка, м
        :param diametr: диаметр, мм
        :param density: плотность, кг/м3
        :param lenght: длина участка трубопровода, м
        :param hole: отверстие истечения, мм
        :param time_shutdown: время отключения давления, с
        :param time_closing: время арматуры, с
        '''
        self.common_pressure = common_pressure * MPA_TO_PA
        self.z1 = z1
        self.z2 = z2
        self.diametr = diametr*MM_TO_M
        self.density = density
        self.lenght = lenght
        self.hole = hole*MM_TO_M
        self.time_shutdown = time_shutdown
        self.time_closing = time_closing

    def velocity(self):
        'Скорость потока при расходе, м/с'
        return math.sqrt(2 * (self.common_pressure / self.density))

    def pressure_flow_rate(self):
        '''
        https://sciencing.com/convert-psi-gpm-water-8174602.html
        https://calculator.academy/pressure-to-velocity-calculator/
        :return: напорный расход, кг/с
        '''
        velocity = self.velocity()
        Ah = (math.pi) * math.pow(self.hole / 2, 2)
        return Ah * velocity * self.density

    def hydrostatic_pressure(self, z1, z2):
        'Гидростатическое давление, Па'
        return self.density * GRAVITY * (z1 - z2)

    def non_pressure_flow_rate(self, z1, z2):
        'Расход в безнапорном режиме, кг/с'
        Ah = (math.pi / 4) * math.pow(self.hole, 2)
        p1 = self.hydrostatic_pressure(z1, z2)
        return DISCHARGE * Ah * self.density * math.sqrt(2 * (p1 - PRESSURE_ATM) / self.density)

    def result(self):
        mass_liquid = []  # масса жидкости в емкости, кг
        time = []  # время истечения, с
        flow_rate = []  # расход, кг/с

        time_init = 0

        mass_in_pipe = (math.pi * math.pow(self.diametr/2, 2)*self.lenght) * self.density  # кг

        while True:
            # Напорный режим
            if time_init <= self.time_shutdown:
                mass_liquid.append(mass_in_pipe)
                time.append(time_init)
                flow_rate.append(self.pressure_flow_rate())
            # Безнапорный режим с подпором других учатков
            elif time_init > self.time_shutdown  and time_init <= self.time_shutdown+self.time_closing:
                mass_liquid.append(mass_in_pipe)
                time.append(time_init)
                flow_rate.append(self.non_pressure_flow_rate(self.z1, self.z2))
            # Безнапорный режим после закрытия арматуры
            elif time_init > self.time_shutdown+self.time_closing:
                volume = mass_liquid[-1]/self.density
                lenght = volume/(math.pi*math.pow(self.diametr/2,2))

                z1  = (self.z1 - self.z2) * (lenght/self.lenght) + self.z2
                mass_in_pipe =mass_liquid[-1] - self.non_pressure_flow_rate(z1, self.z2)
                mass_liquid.append(mass_in_pipe)
                time.append(time_init)
                flow_rate.append(self.non_pressure_flow_rate(z1, self.z2))
                if flow_rate[-1] < 10: break

            time_init += 1

        return (mass_liquid, time, flow_rate)


if __name__ == '__main__':
    cls = Outflow_in_one_section_pipe(common_pressure=2, z1=250, z2=120, diametr=100, density=900,
                                      lenght=1000,
                                      hole=90, time_shutdown=3, time_closing=3)
    print(cls.result())
