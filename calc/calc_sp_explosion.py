# -----------------------------------------------------------
# Класс предназначен для расчета взрыва ТВС
#
# CП 12.13130-2009
# (C) 2022 Kuznetsov Konstantin, Kazan , Russian Federation
# email kuznetsovkm@yandex.ru
# -----------------------------------------------------------

from calc.calc_probit import Probit
from calc._found_nearest_value import get_nearest_value


class Explosion:
    """
    Класс для расчета зон действия взрыва в зависимости от расстояния (СП 12.13130-2009).
    Уравнение Садовского.
    """

    def explosion_point(self, mass: float, heat_of_combustion: float, z: float, radius: float) -> tuple:

        """
        Функция расчета избыточного давления и импульса от рассстояния

        :@param mass: масса испарившегося вещества, кг
        :@param heat_of_combustion: теплота сгорания, кДж/кг (например heat_of_combustion = 46000)
        :@param z: коэф. участия во взрыве (например z = 0.1)
        :@param radius: расстояние от геометрического центра взрыва, м (например radius = 20)

        :@return: result: tuple: delta_p: избыточное давление ВУВ, кПа
                         impulse: импульс, Па*с
        """
        # Проверки
        if 0 in (mass, heat_of_combustion, z, radius):
            raise ValueError(f'Фукнция не может принимать нулевые параметры')

        M_pr = (heat_of_combustion / 4520) * mass * z
        # поиск максимального значения давления и импульса
        delta_p_max = 0
        impulse_max = 0
        for r in range(1, 2000):
            delta_p_max = 101.3 * ((0.8 * (M_pr ** 0.33) / r) + (3 * (M_pr ** 0.66)) /
                                   (r ** 2) + (5 * M_pr) / (r ** 3))
            impulse_max = 123 * (M_pr ** 0.66) / r
            if delta_p_max < 200:
                break
        # расчет в зависимости от радиуса
        delta_p = 101.3 * ((0.8 * (M_pr ** 0.33) / radius) + (3 * (M_pr ** 0.66)) /
                           (radius ** 2) + (5 * M_pr) / (radius ** 3))
        impulse = 123 * (M_pr ** 0.66) / radius

        if delta_p > 150:
            delta_p = delta_p_max
            impulse = impulse_max

        delta_p = round(delta_p, 2)
        impulse = round(impulse, 2)

        result = (delta_p, impulse)

        return result

    def explosion_array(self, mass: float, heat_of_combustion: float, z: float) -> tuple:

        """
        :@param mass: масса испарившегося вещества, кг
        :@param heat_of_combustion: теплота сгорания, кДж/кг (например heat_of_combustion = 46000)
        :@param z: коэф. участия во взрыве (например z = 0.1)

        :@return: : list: [radius, delta_p_arr, impulse_arr, probit, probability]: список списков параметров
        """

        radius_arr = []
        delta_p_arr = []
        impulse_arr = []
        probit_arr = []
        probability_arr = []

        # максимальная взрывная волна
        radius = 0.1
        delta_p = self.explosion_point(mass, heat_of_combustion, z, radius)[0]

        # просчитаем значения пока взрыв больше 2.9 кПа
        while delta_p > 2.9:
            res = self.explosion_point(mass, heat_of_combustion, z, radius)
            delta_p = res[0]
            impulse = res[1]
            probit = Probit().probit_explosion(delta_p, impulse)
            probability = Probit().probability(probit)
            # append
            radius_arr.append(round(radius, 2))
            delta_p_arr.append(delta_p)
            impulse_arr.append(impulse)
            probit_arr.append(probit)
            probability_arr.append(probability)
            radius += 0.1

        result = (radius_arr, delta_p_arr, impulse_arr, probit_arr, probability_arr)

        return result

    def explosion_class_zone(self, mass: float, heat_of_combustion: float, z: float) -> list:
        """
        :@param mass: масса испарившегося вещества, кг
        :@param heat_of_combustion: теплота сгорания, кДж/кг (например heat_of_combustion = 46000)
        :@param z: коэф. участия во взрыве (например z = 0.1)

        :@return: : list: [radius_CZA]: список отсортированных зон
        """

        res_list = self.explosion_array(mass, heat_of_combustion, z)

        # Calculate classified_zone_array
        classified_zone_array = [100, 53, 28, 12, 5, 3]  # CZA
        radius_CZA = []
        delta_p_array = res_list[1]
        radius_array = res_list[0]

        for CZA in classified_zone_array:
            ind = delta_p_array.index(get_nearest_value(delta_p_array, CZA))
            radius_CZA.append(radius_array[ind])
        return radius_CZA


if __name__ == '__main__':


    ev_class = Explosion()
    mass = 10
    heat_of_combustion = 46000
    z = 0.1

    print(ev_class.explosion_class_zone(mass, heat_of_combustion, z))

