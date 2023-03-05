# -----------------------------------------------------------
# Класс предназначен для расчета исперения ненагретых жидкостей
#
# CП 12.13130-2009
# (C) 2022 Kuznetsov Konstantin, Kazan , Russian Federation
# email kuznetsovkm@yandex.ru
# -----------------------------------------------------------


class Liquid_evaporation:
    """
    Класс предназначени для расчета испарения ненагретых жидкостей
    """

    def evaporation_in_moment(self, time: float, steam_pressure: float, molar_mass: float, strait_area: float) -> tuple:

        """
        Функция расчета испарения в конкретный момент времени

        :@param time: время, с
        :@param steam_pressure: давление пара, кПа
        :@param molar_mass: молярная масса, кг/кмоль
        :@param strait_area: площадь пролива, м2

        :@return: result: mass: масса испарившейся жидкости, кг
        """
        # Проверки
        if 0 in (time, steam_pressure, molar_mass, strait_area):
            raise ValueError(f'Фукнция не может принимать нулевые параметры')
        intensity = pow(10, -6) * steam_pressure * pow(molar_mass, 1 / 2)  # кг/(с*м2)
        mass = intensity * strait_area * time  # кг
        return (mass, )

    def evaporation_array(self, steam_pressure: float, molar_mass: float, strait_area: float) -> tuple:

        """
        :@param steam_pressure: давление пара, кПа
        :@param molar_mass: молярная масса, кг/кмоль
        :@param strait_area: площадь пролива, м2

        :@return: : list: [radius, delta_p_arr, impulse_arr, probit, probability]: список списков параметров
        """

        time_arr = [t for t in range(1, 3601)]
        evaporatiom_arr = [self.evaporation_in_moment(t, steam_pressure, molar_mass, strait_area)[0] for t in
                           range(1, 3601)]

        result = (time_arr, evaporatiom_arr)

        return result


if __name__ == '__main__':
    ev_class = Liquid_evaporation()
    time = 3600
    steam_pressure = 35
    molar_mass = 100
    strait_area = 200

    print(ev_class.evaporation_in_moment(time, steam_pressure, molar_mass, strait_area))
    print(ev_class.evaporation_array(steam_pressure, molar_mass, strait_area))
