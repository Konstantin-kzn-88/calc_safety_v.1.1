# -----------------------------------------------------------
# Класс предназначен для исчтечения газа из трубопровода на разрыв
#
# Fires, explosions, and toxic gas dispersions :
# effects calculation and risk analysis /
# Marc J. Assael, Konstantinos E. Kakosimos.

# (C) 2022 Kuznetsov Konstantin, Kazan , Russian Federation
# email kuznetsovkm@yandex.ru
# -----------------------------------------------------------
import math

DISCHARGE = 1  # коэф.истечения, допускается брать 0.95-1 при разрыве на сечение (p.37)
TEMP_TO_KELVIN = 273
KMOL_TO_MOL = 0.001
PRESSURE_ATM = 0.101325  # атмосферное давление, МПа
R = 8.413  # газовая постоянная
MPA_TO_PA = math.pow(10, 6)  # МПа в Па
KM_TO_M = math.pow(10, 3)  # км в м
VISCOSITY = 82  # Па*с (вязкость по пропану)
MM_TO_M = 0.001


class Outflow:
    def __init__(self, pipe_diameter: float, pipe_length: float, pressure: float, temperature: int,
                 mol_weight: float, poisson_ratio: float):
        '''
        Класс предназначен для расчета истечения газа
        :param рipe_diameter: - диаметр трубы, м
        :param pipe_length: - длина трубы, м
        :param pressure: - давление, МПа
        :param temperature: - температура, град.С
        :param mol_weight: - молекулярная масса, кг/кмоль
        :param poisson_ratio: - адиабата газа, -
        '''
        self.pipe_diameter = pipe_diameter
        self.pipe_length = pipe_length
        self.pressure = pressure
        self.temperature = temperature + TEMP_TO_KELVIN
        self.mol_weight = mol_weight * KMOL_TO_MOL
        self.poisson_ratio = poisson_ratio


    def coefficient_K(self) -> float:
        '''
        Вычисление коэф.истечения
        :return: коэф.истечения K (p.36)
        '''
        a = self.pressure / PRESSURE_ATM
        b = math.pow((self.poisson_ratio + 1) / 2, self.poisson_ratio / (self.poisson_ratio - 1))
        # дозвуковое истечение
        if a < b:
            i = 2 * math.pow(self.poisson_ratio, 2) / (self.poisson_ratio - 1)
            j = math.pow(PRESSURE_ATM / self.pressure, 2 / self.poisson_ratio)
            k = math.pow(PRESSURE_ATM / self.pressure, (self.poisson_ratio - 1) / self.poisson_ratio)
            return math.pow(i * j * (1 - k), 1 / 2)
        # сверхзвуковое истечение
        else:
            i = 2 / (self.poisson_ratio + 1)
            j = (self.poisson_ratio + 1) / (2 * (self.poisson_ratio - 1))
            return self.poisson_ratio * math.pow(i, j)

    def flow_rate_init(self):
        '''
        Функция расчета начального значения расхода
        :param hole_diameter: - диаметр отверстия, мм
        :param pressure: - давление, МПа
        :param temperature: - температура, град. K
        :return: расход, кг/с
        '''
        square = (1 / 4) * math.pi * math.pow(self.pipe_diameter, 2)
        k = self.coefficient_K()
        a = DISCHARGE * square * self.pressure * MPA_TO_PA * k
        b = math.pow(math.fabs(self.mol_weight / (self.poisson_ratio * R * self.temperature)), 1 / 2)
        return float(a * b)

    def u_sound(self) -> float:
        'Скорость звука, м/с'
        return math.pow(self.poisson_ratio * R * self.temperature / self.mol_weight, 1 / 2)

    def reinolds(self) -> float:
        'Число Рейнольдса для истечения газа'
        square = (1 / 4) * math.pi * math.pow(self.pipe_diameter, 2)
        po = self.pressure * MPA_TO_PA * self.mol_weight / (R * self.temperature)
        m = self.flow_rate_init()
        u = m / (po * square)

        return (po * u * self.pipe_diameter / VISCOSITY) * math.pow(10, 6)

    def fanning_factor(self) -> float:
        'Параметр Фаннинга'
        re = self.reinolds()
        if re < 2000:
            return 16 / re
        return 0.0791 * math.pow(re, -0.25)

    def time_base(self) -> float:
        'Определение времени истечения, с'
        us = self.u_sound()
        f = self.fanning_factor()
        a = (4 / 3) * (self.pipe_length / us)
        b = math.pow(self.poisson_ratio * f * self.pipe_length / self.pipe_diameter, 1 / 2)
        tb = a * b
        return tb

    def cross_sectional_area(self) -> float:
        'Площадь отверстия истечения, м2'
        return (1 / 4) * math.pi * math.pow(self.pipe_diameter, 2)

    def mass_flow_rate_init(self) -> float:
        'Определение мгновенного массового расхода при t = 0 сек'
        s = self.cross_sectional_area()
        k = self.coefficient_K()
        m = DISCHARGE * s * self.pressure * MPA_TO_PA * k * math.pow(
            self.mol_weight / (self.poisson_ratio * R * self.temperature), 1 / 2)
        return m

    def result(self):
        'Определение расхода по времени от t = 0 сек до t = time_valid'
        m = round(self.mass_flow_rate_init(),2)
        tb =self.time_base()
        s = self.cross_sectional_area()
        po = self.pressure * MPA_TO_PA * self.mol_weight / (R * self.temperature)
        mass_gas = po*self.pipe_length*s
        S = mass_gas/(m*tb)
        u_s = self.u_sound()
        time_valid = int(self.pipe_length / u_s)

        mass_flow_rate = [m]
        time = [0]
        for t in range(0,time_valid,1):
            a = m/(1+S)
            b = S* math.exp(-t/tb)
            c = math.exp(-t/(tb*math.pow(S,2)))
            mass_flow_rate.append(round(a*(b+c)))
            time.append(t)
        return(time, mass_flow_rate)

if __name__ == '__main__':
    cls = Outflow(pipe_diameter=1, pipe_length=10000, pressure=0.5, temperature=15,
                 mol_weight=44, poisson_ratio=1.19)
    print(cls.result())
