# -----------------------------------------------------------
# Класс предназначен для расчета исперения СУГ
#
# CП 12.13130-2009
# (C) 2023 Kuznetsov Konstantin, Kazan , Russian Federation
# email kuznetsovkm@yandex.ru
# -----------------------------------------------------------
import math


class LPG_evaporation:
    """
    Класс предназначени для расчета испарения СУГ
    """
    def __init__(self, molar_mass: float, strait_area: float, wind_velosity: float,
                              lpg_temperature: float, surface_temperature: float):
        '''

        :@param molar_mass: молярная масса, кг/кмоль
        :@param strait_area: площадь пролива, м2
        :@param wind_velosity: скорость ветра, м/с
        :@param lpg_temperature: температура газа, град С
        :@param surface_temperature: температура поверхности, град С
        '''
        self.molar_mass = molar_mass
        self.strait_area = strait_area
        self.wind_velosity = wind_velosity
        self.lpg_temperature = lpg_temperature
        self.surface_temperature = surface_temperature


    def evaporation_in_moment(self, time) -> float:
        """
        Функция расчета испарения в конкретный момент времени
        :@param time: время, с
        :@return: result: mass: масса испарившегося СУГ, кг
        """
        diametr_spill = math.sqrt((4 * self.strait_area) / math.pi)
        reinolds = (self.wind_velosity * diametr_spill) / (1.64 * math.pow(10, -5))

        first_add = ((self.molar_mass / 1000) / 13509) * (self.surface_temperature - self.lpg_temperature)
        second_add = 2 * 1.3 * math.pow((time / (3.14 * 7.74* math.pow(10, -7))), 1 / 2)
        third_add = 5.1 * math.sqrt(reinolds) * time * 0.00155 / diametr_spill
        intensity = first_add * (second_add + third_add)
        mass = intensity * time

        return mass

    def evaporation_array(self) -> tuple:
        """
        :@return: : список списков параметров
        """

        time_arr = [t for t in range(1, 3601)]
        evaporatiom_arr = [self.evaporation_in_moment(t) for t in time_arr]

        result = (time_arr, evaporatiom_arr)

        return result


if __name__ == '__main__':
    ev_class = LPG_evaporation(molar_mass =55, strait_area=300, wind_velosity=1,
                              lpg_temperature=10, surface_temperature=30)


    print(ev_class.evaporation_array())
