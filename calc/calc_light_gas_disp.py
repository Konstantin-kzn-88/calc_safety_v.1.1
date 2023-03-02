# -----------------------------------------------------------
# Класс предназначен для расчета выброса легкого газа
#
# Fires, explosions, and toxic gas dispersions :
# effects calculation and risk analysis /
# Marc J. Assael, Konstantinos E. Kakosimos.

# (C) 2022 Kuznetsov Konstantin, Kazan , Russian Federation
# email kuznetsovkm@yandex.ru
# -----------------------------------------------------------

import math

TEMP_TO_KELVIN = 273
WIND_HEIGHT = 10  # высота определения характеристик ветра
GRAVITY = 9.81  # ускорение свободного падения м/с2
MKG_TO_MG = 0.001  # мкг в мг
M3_TO_LITER = 1000  # м3 в литры


class Instantaneous_source:

    def __init__(self, ambient_temperature: int, cloud: int,
                 wind_speed: int, density_air: float,
                 is_night: bool, is_urban_area: bool):
        """
        ambient_temperature - температура окружающего воздуха, град. С
        cloud - облачность от 0 до 8, -
        wind_speed - скорость ветра, м/с
        density_air - плотность воздуха, кг/м3
        is_night - ночное время суток, -
        is_urban_area - городская застройка, -
        """
        self.ambient_temperature = ambient_temperature + TEMP_TO_KELVIN
        self.cloud = cloud if cloud in [i for i in range(0, 9)] else 0
        self.wind_speed = wind_speed
        self.density_air = density_air
        self.is_night = is_night
        self.is_urban_area = is_urban_area

    def pasquill_atmospheric_stability_classes(self) -> str:
        """
        Классы стабильности атмосферы по Паскуиллу
        Table C5.2. Pasquill Atmospheric Stability Classes. p.222
        :return: : pasquill_class: str: класс атмосферы
        """

        table_data = (
            ('A', 'B', 'B', 'F', 'F'),
            ('B', 'B', 'C', 'E', 'F'),
            ('B', 'B', 'C', 'D', 'E'),
            ('C', 'D', 'D', 'D', 'D'),
            ('C', 'D', 'D', 'D', 'D')
        )

        if self.wind_speed < 2:
            wind_ind = 0
        elif self.wind_speed >= 2 and self.wind_speed < 3:
            wind_ind = 1
        elif self.wind_speed >= 3 and self.wind_speed < 5:
            wind_ind = 2
        elif self.wind_speed >= 5 and self.wind_speed < 6:
            wind_ind = 3
        else:
            wind_ind = 4

        if self.cloud <= 2 and not self.is_night:
            cloud_ind = 0
        elif self.cloud <= 5 and self.cloud > 2 and not self.is_night:
            cloud_ind = 1
        elif self.cloud <= 8 and self.cloud > 5 and not self.is_night:
            cloud_ind = 2
        elif self.cloud <= 3 and self.is_night:
            cloud_ind = 3
        else:
            cloud_ind = 4

        pasquill_class = table_data[wind_ind][cloud_ind]
        return pasquill_class

    def wind_profile(self):
        """
        Экспонента профиля ветра
         Table C5.3. Wind Profile Exponent p, Eq. (C5.1).
         :return: : p: float: экспонента профиля ветра
        """
        pasquill = ('A', 'B', 'C', 'D', 'E', 'F').index(self.pasquill_atmospheric_stability_classes())
        table_data = (
            (0.07, 0.07, 0.10, 0.15, 0.35, 0.55),
            (0.15, 0.15, 0.20, 0.25, 0.30, 0.30),
        )
        p = table_data[int(self.is_urban_area)][pasquill]
        return p

    def wind_power_law(self, ejection_height: int) -> float:
        """
        Зависимость закона силы ветра от высоты выброса
        (C5.1) p.223
        :param ejection_height - высота выброса, м
        :return: : us: float: закон силы ветра от высоты выброса
        """
        p = self.wind_profile()
        us = self.wind_speed * math.pow(ejection_height / WIND_HEIGHT, p)
        return us

    def source_buoyancy_flux_parameter(self, gas_temperature: int, gas_weight: int) -> float:
        """
        Параметр плавучести
        (C5.33) p.243
        :param gas_temperature - температура газа, град.С
        :param gas_weight - масса газа, кг
        :return: : Fbi: float: параметр плавучести газа, м4/с2
        """
        a = (GRAVITY * gas_weight) / (math.pi * self.density_air)
        b = (gas_temperature + TEMP_TO_KELVIN - self.ambient_temperature) / self.ambient_temperature
        Fbi = a * b
        return Fbi

    def maximum_distance_x(self, pasquill: str, us: float, Fbi: float) -> float:
        '''
        Функция расчета максимальной дистанции
        :param pasquill - класс атмосферы по Паскуиллу
        :param us - сила ветра от высоты выброса (см. def wind_power_law)
        :param Fbi - параметр плавучести (см. def source_buoyancy_flux_parameter)
        :return: x_max: float: расстояние, м
        '''
        if pasquill in ('A', 'B', 'C', 'D'):
            if Fbi <= 300 * math.pow(us, 2 / 3):
                x_max = 12 * math.pow(Fbi, 1 / 2) * math.pow(us, 1 / 3)
            else:
                x_max = 50 * math.pow(Fbi, 1 / 4) * math.pow(us, 1 / 2)
        else:
            # 0.02  и 0.035 эмпирические коэф. p.245
            k = 0.02 if pasquill == 'E' else 0.035
            s = (GRAVITY / self.ambient_temperature) * k
            x_max = math.pi * us / math.sqrt(s)
        return x_max

    def gradual_puff_rise(self, ejection_height: int, pasquill: str, us: float,
                          Fbi: float, gas_weight: int, po_gas: float, x_dist) -> float:
        '''
        Функция постепенного подъема выброса (he - параметр),
        до величины максимальной дистанции x_max (def maximum_distance_x)

        :param ejection_height - высота выброса, м
        :param pasquill - класс атмосферы по Паскуиллу
        :param us - сила ветра от высоты выброса (см. def wind_power_law)
        :param Fbi - параметр плавучести (см. def source_buoyancy_flux_parameter)
        :param gas_weight - масса газа, кг
        :param po_gas - плотность газа, кг/м3
        :param x_dist - дистанция м
        :return: he: float: подъем, м
        '''
        x_max = self.maximum_distance_x(pasquill, us, Fbi)
        x_dist = x_dist if x_dist < x_max else x_max
        C_CONST = 0.64  # эмпирический коэф. p.245 (коэф. поглощения)
        # 0.02  и 0.035 эмпирические коэф. p.245
        k = 0.02 if pasquill == 'E' else 0.035
        s = (GRAVITY / self.ambient_temperature) * k

        if pasquill in ('A', 'B', 'C', 'D'):
            a = 2 * Fbi * math.pow(x_dist, 2)
            b = math.pow(C_CONST, 3) * math.pow(us, 2)
            he = ejection_height + math.pow(a / b, 1 / 4)
        else:
            r_cloud = math.pow(3 * gas_weight / (4 * math.pi * po_gas), 1 / 3)
            a = (4 * Fbi) / (math.pow(C_CONST, 3) * s)
            b = 1 - math.cos(x_dist * math.sqrt(s) / us)
            c = a * b
            d = math.pow(r_cloud / C_CONST, 4)
            he = ejection_height + math.pow(c + d, 1 / 4) - (r_cloud / C_CONST)
        return he

    def final_puff_rise(self, ejection_height: int, pasquill: str, us: float,
                        Fbi: float, gas_weight: int, po_gas: float, x_dist: int) -> float:
        '''
        Функция финальной высоты выброса (he - параметр),
        после величины максимальной дистанции x_max (def maximum_distance_x)

        :param ejection_height - высота выброса, м
        :param pasquill - класс атмосферы по Паскуиллу
        :param us - сила ветра от высоты выброса (см. def wind_power_law)
        :param Fbi - параметр плавучести (см. def source_buoyancy_flux_parameter)
        :param gas_weight - масса газа, кг
        :param po_gas - плотность газа, кг/м3
        :param x_dist - дистанция м
        :return: he: float: подъем, м
        '''
        x_max = self.maximum_distance_x(pasquill, us, Fbi)
        x_dist = x_dist if x_dist < x_max else x_max
        C_CONST = 0.64  # эмпирический коэф. p.245 (коэф. поглощения)
        # 0.02  и 0.035 эмпирические коэф. p.245
        k = 0.02 if pasquill == 'E' else 0.035
        s = (GRAVITY / self.ambient_temperature) * k
        if pasquill in ('A', 'B', 'C', 'D'):
            a = 2 * Fbi * math.pow(x_dist, 2)
            b = math.pow(C_CONST, 3) * math.pow(us, 2)
            he = ejection_height + math.pow(a / b, 1 / 4)
        else:
            r_cloud = math.pow(3 * gas_weight / (4 * math.pi * po_gas), 1 / 3)
            a = (8 * Fbi) / (math.pow(C_CONST, 3) * s)
            d = math.pow(r_cloud / C_CONST, 4)
            he = ejection_height + math.pow(a + d, 1 / 4) - (r_cloud / C_CONST)
        return he

    def atmospheric_stability_param(self, pasquill: str) -> tuple:
        '''
        Параметры атмосферной стабильности
        Table C5.11. Parameters of Eq. (C5.44) as a
        Function of Atmospheric Stability. p247

        :param pasquill - класс атмосферы по Паскуиллу
        :return: : tuple: кортеж параметров (a,b,c,d)
        '''

        # Table C5.11. Parameters of Eq. (C5.44) as a
        # Function of Atmospheric Stability. p247
        data = {
            "A": (0.18, 0.92, 0.72, 0.76),
            "B": (0.14, 0.92, 0.53, 0.73),
            "C": (0.10, 0.92, 0.34, 0.72),
            "D": (0.06, 0.92, 0.15, 0.70),
            "E": (0.045, 0.91, 0.12, 0.67),
            "F": (0.03, 0.90, 0.08, 0.64),
        }

        return data[pasquill] if pasquill in data.keys() else data['F']

    def dispersion_param(self, pasquill: str, x_dist: int):
        '''
        Функция параметров дисперсии
        :param pasquill - класс атмосферы по Паскуиллу
        :param x_dist - дистанция м
        :return: sigma: tuple: кортеж параметров (sigma_x, sigma_y, sigma_z)
        '''
        a, b, c, d = self.atmospheric_stability_param(pasquill)
        sigma_x = a * math.pow(x_dist / 1, b)
        sigma_y = sigma_x
        sigma_z = c * math.pow(x_dist / 1, d)
        return (sigma_x, sigma_y, sigma_z)

    def mean_wind_speed(self, height_rise: float, height_rise_max: float, sigma_z: float) -> tuple:
        '''
        Функция средней скорости ветра
        :param height_rise - высота выброса, м (см. def gradual_puff_rise и final_puff_rise)
        :param height_rise_max - высота выброса при расстоянии для
                                   максимального подъема, м (см. def gradual_puff_rise)
        :param sigma_z - коэф. дисперсии (см. def dispersion_param)

        :return: (z_b,z_t,u_with_streak): tuple: - эмп. коэфциенты расслоения, средняя скорость ветра, м/с

        '''
        p = self.wind_profile()

        if height_rise - 2.15 * sigma_z > 2:
            z_b = height_rise - 2.15 * sigma_z
        else:
            z_b = 2

        if height_rise + 2.15 * sigma_z < height_rise_max:
            z_t = height_rise + 2.15 * sigma_z
        else:
            z_t = height_rise_max

        a = (z_t - z_b) * math.pow(WIND_HEIGHT, p) * (1 + p)
        b = self.wind_speed / a
        c = math.pow(z_t, 1 + p) - math.pow(z_b, 1 + p)
        u_with_streak = b * c

        return (z_b, z_t, u_with_streak)

    def time_in_out_peak(self, sigma_x: float, u_with_streak: float, x_dist: int) -> tuple:
        '''
        :param sigma_x - коэф. дисперсии (см. def dispersion_param)
        :param u_with_streak - средняя скорость ветра (см. def mean_wind_speed)
        :param x_dist - дистанция м

        :return: (t_in,t_out,t_peak): tuple: - время приходо, ухода, максимального присутвия в точке, с

        '''
        t_in = (x_dist - 2.45 * sigma_x) / u_with_streak
        t_out = (x_dist + 2.45 * sigma_x) / u_with_streak
        t_peak = x_dist / u_with_streak
        return (t_in, t_out, t_peak)

    def concentration(self, gas_weight: int, mean_wind_speed: float,
                      height_rise: float, time: float, x_dist: int, y: int, z: int) -> float:
        '''
        :param gas_weight - масса газа, кг
        :param u_with_streak - средняя скорость ветра (см. def mean_wind_speed)
        :param height_rise - высота выброса, м (см. def gradual_puff_rise и final_puff_rise)
        :param time - время с момента выброса, с (для максимального значения принять t_peak)
        :param x_dist, y, z - пространственные координаты, м

        :return: (concentration): float: - концентрация, мг/м3

        '''
        pasquill = self.pasquill_atmospheric_stability_classes()
        sigma_x, sigma_y, sigma_z = self.dispersion_param(pasquill, x_dist)

        first_add = 2 * gas_weight * math.pow(10, 9)
        second_add = math.pow(2 * math.pi, 3 / 2) * sigma_x * sigma_y * sigma_z
        third_add = math.exp(-(math.pow(x_dist - mean_wind_speed * time, 2)) / (2 * math.pow(sigma_x, 2)))
        fourth_add = math.exp(-(math.pow(y, 2)) / (2 * math.pow(sigma_y, 2)))
        fifth_add = math.exp(-(math.pow(height_rise - z, 2)) / (2 * math.pow(sigma_z, 2)))
        six_add = math.exp(-(math.pow(height_rise + z, 2)) / (2 * math.pow(sigma_z, 2)))

        concentration = (first_add / second_add) * third_add * fourth_add * (fifth_add + six_add)
        return concentration * MKG_TO_MG

    def toxic_dose(self, concentration: float, time: int, n=3):
        '''
        :param concentration - концентрация, мг/м3
        :param time - время экспозиции, мин
        :param n - эмпирический коэф., допускается принимать равным 3 (стр.266 Fires, explosions, and toxic gas...)

        :return: (dose): float: - токсодоза, мг*мин/л
        '''
        dose = math.pow(concentration/M3_TO_LITER, n) * time
        return dose


class Continuous_source:
    def __init__(self, ambient_temperature: int, cloud: int,
                 wind_speed: int, density_air: float,
                 is_night: bool, is_urban_area: bool):
        """
        ambient_temperature - температура окружающего воздуха, град. С
        cloud - облачность от 0 до 8, -
        wind_speed - скорость ветра, м/с
        density_air - плотность воздуха, кг/м3
        is_night - ночное время суток, -
        is_urban_area - городская застройка, -
        """
        self.ambient_temperature = ambient_temperature + TEMP_TO_KELVIN
        self.cloud = cloud if cloud in [i for i in range(0, 9)] else 0
        self.wind_speed = wind_speed
        self.density_air = density_air
        self.is_night = is_night
        self.is_urban_area = is_urban_area

    def pasquill_atmospheric_stability_classes(self) -> str:
        """
        Классы стабильности атмосферы по Паскуиллу
        Table C5.2. Pasquill Atmospheric Stability Classes. p.222
        :return: : pasquill_class: str: класс атмосферы
        """

        table_data = (
            ('A', 'B', 'B', 'F', 'F'),
            ('B', 'B', 'C', 'E', 'F'),
            ('B', 'B', 'C', 'D', 'E'),
            ('C', 'D', 'D', 'D', 'D'),
            ('C', 'D', 'D', 'D', 'D')
        )

        if self.wind_speed < 2:
            wind_ind = 0
        elif self.wind_speed >= 2 and self.wind_speed < 3:
            wind_ind = 1
        elif self.wind_speed >= 3 and self.wind_speed < 5:
            wind_ind = 2
        elif self.wind_speed >= 5 and self.wind_speed < 6:
            wind_ind = 3
        else:
            wind_ind = 4

        if self.cloud <= 2 and not self.is_night:
            cloud_ind = 0
        elif self.cloud <= 5 and self.cloud > 2 and not self.is_night:
            cloud_ind = 1
        elif self.cloud <= 8 and self.cloud > 5 and not self.is_night:
            cloud_ind = 2
        elif self.cloud <= 3 and self.is_night:
            cloud_ind = 3
        else:
            cloud_ind = 4

        pasquill_class = table_data[wind_ind][cloud_ind]
        return pasquill_class

    def wind_profile(self):
        """
        Экспонента профиля ветра
         Table C5.3. Wind Profile Exponent p, Eq. (C5.1).
         :return: : p: float: экспонента профиля ветра
        """
        pasquill = ('A', 'B', 'C', 'D', 'E', 'F').index(self.pasquill_atmospheric_stability_classes())
        table_data = (
            (0.07, 0.07, 0.10, 0.15, 0.35, 0.55),
            (0.15, 0.15, 0.20, 0.25, 0.30, 0.30),
        )
        p = table_data[int(self.is_urban_area)][pasquill]
        return p

    def wind_power_law(self, ejection_height: int) -> float:
        """
        Зависимость закона силы ветра от высоты выброса
        (C5.1) p.223
        :param ejection_height - высота выброса, м
        :return: : us: float: закон силы ветра от высоты выброса
        """
        p = self.wind_profile()
        us = self.wind_speed * math.pow(ejection_height / WIND_HEIGHT, p)
        return us

    def height_source_correction(self, us: float, gas_exit_speed: float,
                                 ejection_diametr: int, ejection_height: int):
        '''
        Функция корректироваки высоты выброса

        :param us - сила ветра, м/с (см. def wind_power_law)
        :param gas_exit_speed - скорость выброса газа, м/с
        :param ejection_diametr - диаметр выброса, м
        :param hs_with_steak - корректированная высота выброса, м

        :return: : us: float: закон силы ветра от высоты выброса
        '''
        if gas_exit_speed / us < 1.5:
            hs_with_steak = ejection_height + 2 * ejection_diametr * (gas_exit_speed / us - 1.5)
        else:
            hs_with_steak = ejection_height
        return hs_with_steak

    def selecting_plume_rise(self, pasquill: str, gas_exit_speed: float,
                             gas_temperature: int, ejection_diametr: int) -> float:
        '''
        Функция для опредления, что больше воздействует импульс или плавучесть
        Table C5.4. Equations for Selecting Plume Rise Because of Buoyancy or Momentum
        :param pasquill - класс атмосферы по Паскуиллу
        :param gas_exit_speed - скорость выброса газа, м/с
        :param gas_temperature - температура выброса газа, град.С
        :param ejection_diametr - диаметр выброса, м
        :return: delta_T_c: float: температура, К (для опредления, что больше воздействует импульс или плавучесть)
        '''
        gas_temperature = gas_temperature + TEMP_TO_KELVIN
        Fb = GRAVITY * gas_exit_speed * math.pow(ejection_diametr, 2) * (
                (gas_temperature - self.ambient_temperature) / (4 * gas_temperature))
        if pasquill in ('A', 'B', 'C', 'D'):
            if Fb < 55:
                delta_T_c = 0.0297 * gas_temperature * math.pow(gas_exit_speed / math.pow(ejection_diametr, 2), 1 / 3)
            else:
                delta_T_c = 0.00575 * gas_temperature * math.pow(gas_exit_speed / math.pow(ejection_diametr, 2), 1 / 3)
        else:
            # 0.02  и 0.035 эмпирические коэф. p.245
            k = 0.02 if pasquill == 'E' else 0.035
            s = (GRAVITY / self.ambient_temperature) * k
            delta_T_c = 0.019582 * gas_temperature * gas_exit_speed * math.sqrt(s)
        return delta_T_c

    def maximum_distance_x(self, pasquill: str, gas_exit_speed: float,
                           gas_temperature: int, ejection_diametr: int, delta_T_c: float, us: float) -> float:
        '''
        Функция расчета максимальной дистанции
        Table C5.5. Equations for Calculating Distance, xf, of Maximum Plume Rise
        :param pasquill - класс атмосферы по Паскуиллу
        :param gas_exit_speed - скорость выброса газа, м/с
        :param gas_temperature - температура выброса газа, град.С
        :param ejection_diametr - диаметр выброса, м
        :@delta_T_c: nt - диаметр выброса, м
        :param us - сила ветра от высоты выброса (см. def wind_power_law)
        :return: x_max: float: расстояние, м
        '''
        gas_temperature = gas_temperature + TEMP_TO_KELVIN
        Fb = GRAVITY * gas_exit_speed * math.pow(ejection_diametr, 2) * (
                (gas_temperature - self.ambient_temperature) / (4 * gas_temperature))

        if pasquill in ('A', 'B', 'C', 'D'):
            if Fb < 55:
                x_max = 49 * math.pow(Fb, 5 / 8)
            else:
                x_max = 119 * math.pow(Fb, 2 / 5)
            if (gas_temperature - self.ambient_temperature) < delta_T_c and Fb == 0:
                x_max = 4 * ejection_diametr * math.pow(gas_exit_speed + 3 * us, 2) / (gas_exit_speed * us)
        else:
            # 0.02  и 0.035 эмпирические коэф. p.245
            k = 0.02 if pasquill == 'E' else 0.035
            s = (GRAVITY / self.ambient_temperature) * k
            if (gas_temperature - self.ambient_temperature) < delta_T_c:
                x_max = math.pi * 0.50 * us / math.sqrt(s)
            else:
                x_max = 2.0715 * us / math.sqrt(s)
        return x_max

    def gradual_puff_rise(self, pasquill: str, gas_exit_speed: float,
                          gas_temperature: int, ejection_diametr: int,
                          delta_T_c: float, us: float, hs_with_steak: float, x_dist: float) -> float:
        '''
        Функция постепенного подъема выброса (he - параметр),
        до величины максимальной дистанции x_max (def maximum_distance_x)

        :param pasquill - класс атмосферы по Паскуиллу
        :param gas_exit_speed - скорость выброса газа, м/с
        :param gas_temperature - температура выброса газа, град.С
        :param ejection_diametr - диаметр выброса, м
        :@delta_T_c: nt - диаметр выброса, м
        :param us - сила ветра от высоты выброса (см. def wind_power_law)
        :param hs_with_steak - откорректированная высота выброса, м (см. def height_source_correction)
        :param x_dist - дистанция м
        :return: he: float: подъем, м
        '''
        gas_temperature = gas_temperature + TEMP_TO_KELVIN

        Fb = GRAVITY * gas_exit_speed * math.pow(ejection_diametr, 2) * (
                (gas_temperature - self.ambient_temperature) / (4 * gas_temperature))

        x_max = self.maximum_distance_x(pasquill, gas_exit_speed, gas_temperature, ejection_diametr, delta_T_c, us)
        x_dist = x_dist if x_dist < x_max else x_max

        # 0.02  и 0.035 эмпирические коэф. p.245
        k = 0.02 if pasquill == 'E' else 0.035
        s = (GRAVITY / self.ambient_temperature) * k

        Fm = math.pow(gas_exit_speed, 2) * math.pow(ejection_diametr, 2) * (
                self.ambient_temperature / (4 * gas_temperature))

        betta_j = (1 / 3) + us / gas_exit_speed

        if pasquill in ('A', 'B', 'C', 'D', 'E', 'F') and (gas_temperature - self.ambient_temperature) >= delta_T_c:
            a = 1.60 * math.pow(Fb * math.pow(x_dist, 2), 1 / 3) / us
            he = hs_with_steak + a
        else:
            if pasquill in ('A', 'B', 'C', 'D'):
                a = math.pow(betta_j, 2) * math.pow(us, 2)
                b = 1.60 * math.pow(3 * Fm * x_dist / a, 1 / 3)
                he = hs_with_steak + b
            else:
                a = 3 * Fm
                b = math.sin(x_dist * math.sqrt(s) / us)
                c = math.pow(betta_j, 2) * us * math.sqrt(s)

                he = hs_with_steak + math.pow(a * (b / c), 1 / 3)

        return he

    def final_puff_rise(self, pasquill: str, gas_exit_speed: float,
                        gas_temperature: int, ejection_diametr: int,
                        delta_T_c: float, us: float, hs_with_steak: float) -> float:
        '''
        Функция финальной высоты выброса (he - параметр),
        после величины максимальной дистанции x_max (def maximum_distance_x)

        :param pasquill - класс атмосферы по Паскуиллу
        :param gas_exit_speed - скорость выброса газа, м/с
        :param gas_temperature - температура выброса газа, град.С
        :param ejection_diametr - диаметр выброса, м
        :@delta_T_c: nt - диаметр выброса, м
        :param us - сила ветра от высоты выброса (см. def wind_power_law)
        :param hs_with_steak - откорректированная высота выброса, м (см. def height_source_correction)
        :return: he: float: подъем, м
        '''
        gas_temperature = gas_temperature + TEMP_TO_KELVIN

        Fb = GRAVITY * gas_exit_speed * math.pow(ejection_diametr, 2) * (
                (gas_temperature - self.ambient_temperature) / (4 * gas_temperature))

        # 0.02  и 0.035 эмпирические коэф. p.245
        k = 0.02 if pasquill == 'E' else 0.035
        s = (GRAVITY / self.ambient_temperature) * k

        Fm = math.pow(gas_exit_speed, 2) * math.pow(ejection_diametr, 2) * (
                self.ambient_temperature / (4 * gas_temperature))

        if pasquill in ('A', 'B', 'C', 'D') and (gas_temperature - self.ambient_temperature) >= delta_T_c:
            if Fb < 55:
                a = 21.425 * math.pow(Fb, 3 / 4) / us
                he = hs_with_steak + a
            else:
                a = 38.710 * math.pow(Fb, 3 / 5) / us
                he = hs_with_steak + a
        elif pasquill in ('E', 'F') and (gas_temperature - self.ambient_temperature) >= delta_T_c:
            a = 2.60 * math.pow(Fb / (us * s), 1 / 3)
            he = hs_with_steak + a
        else:
            if pasquill in ('A', 'B', 'C', 'D'):
                a = 3 * ejection_diametr * (gas_exit_speed / us)
                he = hs_with_steak + a
            else:
                a = 3 * ejection_diametr * (gas_exit_speed / us)
                b = 1.5 * math.pow(Fm / (us * math.sqrt(s)), 1 / 3)
                he = hs_with_steak + min(a, b)

        return he

    def a_b_param(self, pasquill: str, x_dist: int):
        '''
        Функция подбора параметров a,b
        Table C5.8. Parameters of Eqs. (C5.26)-(C5.27) as a Function of Atmospheric Stability. p.238
        :param pasquill: 
        :param x_dist: 
        :return: tuple (a,b)
        '''
        data = {
            'A': {
                '100': (122.800, 0.94470),
                '150': (158.080, 1.05420),
                '200': (170.220, 1.09320),
                '250': (179.520, 1.12620),
                '300': (217.410, 1.26440),
                '400': (258.890, 1.40940),
                '500': (346.750, 1.72830),
                '3110': (453.850, 2.11660),
                '60001': (0, 0),
            },
            'B': {
                '210': (90.673, 0.93196),
                '400': (98.483, 0.98332),
                '60001': (109.300, 1.09710),  # для любых х>400
            },
            'C': {
                '60001': (61.141, 0.91465),  # для любых х
            },
            'D': {
                '310': (34.459, 0.86974),
                '1000': (32.093, 0.81066),
                '3000': (32.093, 0.64403),
                '30000': (36.650, 1.09710),
                '60001': (44.053, 0.51179),
            },
            'E': {
                '100': (24.260, 0.83660),
                '300': (23.331, 0.81956),
                '1000': (21.628, 0.75660),
                '2000': (21.628, 0.63077),
                '4000': (22.540, 0.57154),
                '10000': (24.703, 0.50527),
                '20000': (26.970, 0.46713),
                '40000': (34.420, 0.37615),
                '60001': (47.618, 0.29592),
            },
            'F': {
                '200': (15.209, 0.81558),
                '700': (14.457, 0.78407),
                '1000': (13.953, 0.68465),
                '2000': (13.953, 0.63227),
                '3000': (14.823, 0.54503),
                '7000': (16.187, 0.46490),
                '15000': (17.836, 0.41507),
                '30000': (22.651, 0.32681),
                '60001': (27.074, 0.27436),
            },
        }
        pasquill = pasquill if pasquill in ('A', 'B', 'C', 'D', 'E', 'F') else 'F'
        x_dist = x_dist if x_dist < 60000 else 60000
        for item in data.keys():
            if item == pasquill:
                for i in data[pasquill].keys():
                    if x_dist < int(i):
                        a, b = data[pasquill][i]
                        return (a, b)

    def c_h_param(self, pasquill: str):
        '''
        Функция подбора параметров c-h
        Table C5.8. Parameters of Eqs. (C5.26)-(C5.27) as a Function of Atmospheric Stability. p.238
        :param pasquill:
        :return: tuple (c,d,e,f,g,h)
        '''
        pasquill = pasquill if pasquill in ('A', 'B', 'C', 'D', 'E', 'F') else 'F'
        data = {
            'A': (24.1670, 2.5334, 0.32, 0.24, 0.001, 0.5),
            'B': (18.3330, 1.8096, 0.32, 0.24, 0.001, 0.5),
            'C': (12.5000, 1.0857, 0.22, 0.20, 0, 0),
            'D': (8.3330, 0.7238, 0.16, 0.14, 0.0003, -0.5),
            'E': (6.2500, 0.5428, 0.11, 0.08, 0.0015, -0.05),
            'F': (4.1667, 0.3619, 0.11, 0.08, 0.0015, -0.05),
        }

        return data[pasquill]

    def dispersion_param(self, pasquill: str, x_dist: int):
        '''
        Функция параметров дисперсии
        :param pasquill - класс атмосферы по Паскуиллу
        :param x_dist - дистанция м
        :return: sigma: tuple: кортеж параметров (sigma_x, sigma_y, sigma_z)
        '''
        C1 = 0.0004
        C2 = 0.4651
        C3 = 0.001
        C4 = 0.01745
        c, d, e, f, g, h = self.c_h_param(pasquill)
        a, b = self.a_b_param(pasquill, x_dist)
        if self.is_urban_area:
            sigma_y = e * x_dist * math.pow(1 + C1 * x_dist, -1 / 2)
            sigma_z = f * x_dist * math.pow(1 + g * x_dist, h)
        else:
            TH = C4 * (c - d * math.log(C3 * x_dist))
            sigma_y = C2 * x_dist * math.tan(TH)
            sigma_z = a * math.pow(C3 * x_dist, b)

        return (sigma_y, sigma_z)

    def concentration(self, gas_emission: float, us: float,
                      height_rise: float, x_dist: int, y: int, z: int) -> float:
        '''
        :param gas_emission - выброс газа, кг/с
        :param us закон силы ветра от высоты выброса
        :param height_rise - высота выброса, м (см. def gradual_puff_rise и final_puff_rise)
        :param x_dist, y, z - пространственные координаты, м

        :return: (concentration): float: - концентрация, мг/м3

        '''

        pasquill = self.pasquill_atmospheric_stability_classes()
        sigma_y, sigma_z = self.dispersion_param(pasquill, x_dist)

        first_add = (gas_emission / us) * (math.pow(10, 9) / (2 * math.pi * sigma_y))
        second_add = math.exp(-(y ** 2) / (2 * (sigma_y ** 2)))
        third_add = 1 / sigma_z
        fourth_add = math.exp(-((height_rise - z) ** 2) / (2 * sigma_z * sigma_z))
        fifth_add = math.exp(-((height_rise + z) ** 2) / (2 * sigma_z * sigma_z))

        concentration = first_add * second_add * third_add * (fourth_add + fifth_add)
        return concentration * MKG_TO_MG

    def toxic_dose(self, concentration: float, time: int, n=3):
        '''
        :param concentration - концентрация, мг/м3
        :param time - время экспозиции, мин
        :param n - эмпирический коэф., допускается принимать равным 3 (стр.266 Fires, explosions, and toxic gas...)

        :return: (dose): float: - токсодоза, мг*мин/л
        '''
        dose = math.pow(concentration/M3_TO_LITER, n) * time
        return dose


if __name__ == '__main__':
    # #instantaneous_source
    # cls = Instantaneous_source(ambient_temperature=25, cloud=0,
    #                            wind_speed=4, density_air=1.21,
    #                            is_night=False, is_urban_area=False)
    # pasquill = (cls.pasquill_atmospheric_stability_classes())
    # p = (cls.wind_profile())
    # us = (cls.wind_power_law(ejection_height=2))
    # Fbi = (cls.source_buoyancy_flux_parameter(147, 500))
    # x_max = cls.maximum_distance_x(pasquill, us, Fbi)
    # he_max = cls.gradual_puff_rise(ejection_height=2, pasquill=pasquill, us=us,
    #                                Fbi=Fbi, gas_weight=500, po_gas=3.15, x_dist=x_max)
    #
    # x = 1000
    # he_r = cls.gradual_puff_rise(ejection_height=2, pasquill=pasquill, us=us, Fbi=Fbi, gas_weight=500, po_gas=3.15,
    #                              x_dist=x) if x <= he_max else cls.final_puff_rise(ejection_height=2, pasquill=pasquill,
    #                                                                                us=us, Fbi=Fbi, gas_weight=500,
    #                                                                                po_gas=3.15, x_dist=x)
    #
    # sigma_x, sigma_y, sigma_z = cls.dispersion_param(pasquill=pasquill, x_dist=x)
    #
    # u_mean = cls.mean_wind_speed(he_r, he_max, sigma_z)[2]
    #
    # t_in, t_out, t_peak = cls.time_in_out_peak(sigma_x, u_mean, x)
    #
    # print(cls.concentration(500, u_mean, he_r, t_peak, x, 0, 2))

    # Continuous
    cls = Continuous_source(ambient_temperature=7, cloud=5,
                            wind_speed=2, density_air=1.21,
                            is_night=True, is_urban_area=False)

    pasquill = (cls.pasquill_atmospheric_stability_classes())
    us = (cls.wind_power_law(25))
    hs_with_steak = cls.height_source_correction(us, 4, 1, 25)
    dt = cls.selecting_plume_rise(pasquill, 4, 127, 1)
    x_max = cls.maximum_distance_x(pasquill, 4, 127, 1, dt, us)
    he_1 = (cls.gradual_puff_rise(pasquill, 4, 127, 1, dt, us, hs_with_steak, 50))
    he_2 = (cls.final_puff_rise(pasquill, 4, 127, 1, dt, us, hs_with_steak))

    print(cls.concentration(0.02, us, he_2, 60000, 0, 2))
