# -----------------------------------------------------------
# Класс предназначен для расчета исперения СУГ
#
# Рекомендации по обеспечению пожарной безопасности объектов хранения и
# переработки сжиженных углеводородных газов (СУГ)
#
# (C) 2023 Kuznetsov Konstantin, Kazan , Russian Federation
# email kuznetsovkm@yandex.ru
# -----------------------------------------------------------
import math

TEMP_TO_KELVIN = 273


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
        self.lpg_temperature = lpg_temperature + TEMP_TO_KELVIN
        self.surface_temperature = surface_temperature + TEMP_TO_KELVIN

    def evaporation_in_moment(self, time) -> float:
        """
        Функция расчета испарения в конкретный момент времени
        :@param time: время, с
        :@return: result: mass: масса испарившегося СУГ, кг
        """

        first_add = self.strait_area * ((self.molar_mass / 1000) / 13440) * (
                    self.surface_temperature - self.lpg_temperature)
        second_add = 2 * 1.5 * math.pow((time / (3.14 * 8.4 * math.pow(10, -8))), 1 / 2)
        third_add = 5.1 * math.sqrt(
            (self.strait_area / (1.64 * math.pow(10, -5)) * 2.74 * math.pow(10, -2) * time)) / math.sqrt(self.strait_area)
        mass = first_add * (second_add + third_add)

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
    ev_class = LPG_evaporation(molar_mass=28, strait_area=5128, wind_velosity=5,
                               lpg_temperature=-104, surface_temperature=36)

    print(ev_class.evaporation_in_moment(3600))
