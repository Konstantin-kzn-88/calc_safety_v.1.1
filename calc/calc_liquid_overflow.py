import math
import numpy as np

GRAVITY = 9.81 #м/с2
TIME_STEP = 0.01


class LIGUID_OVERFLOW:
    """
    Класс предназначени для расчета перелива ЛВЖ
    """

    def __init__(self, height_liguid_init: float, volume_init: float, dist:float, flanging_height: float):
        '''

        :@param height_liguid_init: начальная высота столба жидкости, м
        :@param volume_init: объем жидкости, м3
        :@param dist: расстояние от края резервуара до обвалования, м
        :@param flanging_height: высота отбортовки, м
        '''
        self.height_liguid_init = height_liguid_init
        self.volume_init = volume_init
        self.dist = dist
        self.flanging_height = flanging_height


    def overflow_in_moment(self):
        t = []  # время, с
        x = []  # край пролива, м
        un = []  # скорость падения столба жидкость, м/с
        hn = []  # высота столба жидкость, м/с
        s = []  # площадь цилиндра, м2
        Q = []  # доля перелившейся жидкости, %

        for time in np.arange(0, 1, TIME_STEP):
            if time == 0:
                t.append(0)
                s.append(self.volume_init/self.height_liguid_init)
                hn.append(self.height_liguid_init)
                un.append(math.sqrt(2*GRAVITY*hn[-1]))
                x.append(math.sqrt(s[-1]/math.pi))

            else:
                t.append(time)
                hn.append(hn[-1]-TIME_STEP*un[-1])
                s.append(self.volume_init / hn[-1])
                un.append(math.sqrt(2*GRAVITY*hn[-1]))
                x.append(math.sqrt(s[-1] / math.pi))

            if x[-1] < self.dist:
                Q.append(0)
            else:
                print(un[-1],hn[-1], self.flanging_height, hn[0], x[0])
                Q.append(int(un[-1] * (hn[-1] - self.flanging_height) / (hn[0] * x[0]) * 100))
                return (t, s, hn, un, x, Q)
        raise ValueError

if __name__ == '__main__':
    ov_class = LIGUID_OVERFLOW(height_liguid_init=12, volume_init=5000,dist=15, flanging_height=2)
    for i in ov_class.overflow_in_moment():
        print(i)
