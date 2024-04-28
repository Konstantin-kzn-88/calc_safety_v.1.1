# ------------------------------------------------------------------------------------
# Класс GUI для расчетов по промышленной безопасности
#
# (C) 2023 Kuznetsov Konstantin, Kazan , Russian Federation
# email kuznetsovkm@yandex.ru
# ------------------------------------------------------------------------------------

import sys
import os
from pathlib import Path
import time
import webbrowser

from PySide6 import QtWidgets, QtGui, QtCore
import pyqtgraph as pg
import pyqtgraph.exporters as pg_exp

from calc import calc_strait_fire
from calc import calc_lower_concentration
from calc import calc_fireball
from calc import calc_sp_explosion
from calc import calc_tvs_explosion
from calc import calc_light_gas_disp
from calc import calc_heavy_gas_disp
from calc import calc_gas_outflow_small_hole  # истечение газ-емкость
from calc import calc_gas_outflow_big_hole  # истечение газ-труба на разрыв
from calc import calc_liguid_outflow_tank
from calc import calc_liguid_outflow_pipe
from calc import calc_liguid_evaporation
from calc import calc_evaporation_LPG
from calc import calc_liquid_overflow
from calc import calc_damage

METODS_AND_PARAMETRS = {
    'Пожар пролива': ('Площадь, м2', 'm, кг/(с*м2) ', 'Mmol, кг/кмоль', 'Ткип, град.С', 'Ветер, м/с'),
    'Пожар-вспышка': ('Масса, кг', 'Mmol, кг/кмоль', 'Ткип, град.С', 'НКПР, об.%'),
    'Огненный шар': ('Масса, кг', 'Ef, кВт/м2'),
    'Взрыв (СП 12.13130-2009)': ('Масса, кг', 'Qсг, кДж/кг ', 'z, -'),
    'Взрыв (Методика ТВС)': ('Класс в-ва', 'Класс прост-ва', 'Масса, кг', 'Qсг, кДж/кг', 'sigma, -', 'Энергозапас, -'),
    'Легкий газ': (
        'Тем-ра воздуха, град. С', 'Облачность (0-8)', 'Cкорость ветра, м/с', 'Ночь (0/1)',
        'Городская застройка (0/1)', 'Высота выброса, м', 'Тем-ра газа, град. С', 'Масса газа, кг',
        'Расход газа, кг/с', 'Время отсечения, с', 'Молекулярная масса, кг/кмоль'),
    'Тяжелый газ (перв.облако)': (
        'Скорость ветра, м/с', 'Плотность воздуха, кг/м3', 'Плотность газа, кг/м3', 'Объем газа, м3'),
    'Тяжелый газ (втор.облако)': (
        'Скорость ветра, м/с', 'Плотность воздуха, кг/м3', 'Плотность газа, кг/м3', 'Расход газа, кг/с',
        'Радиус выброса, м'),
    'Истечение газа (емк.)': (
        'Объем емк., м3', 'Давление, МПа', 'Тем-ра газа, град. С', 'Молекулярная масса, кг/кмоль', 'Коэф. адиабаты, -',
        'Диаметр отверстия, мм'),
    'Истечение газа (труб.)': (
        'Диаметр трубопровода, м', 'Длина трубопровода, м', 'Давление, МПа', 'Тем-ра газа, град. С',
        'Молекулярная масса, кг/кмоль', 'Коэф. адиабаты, -'),
    'Истечение жидкости (емк.)': (
        'Объем емк., м3', 'Высота взлива, м', 'Давление, МПа',
        'Степень заполнения,-', ' Диаметр отверстия, мм', 'Плотность жидкости, кг/м3'),
    'Истечение жидкости (труб.)': (
        'Давление, МПа', 'Высот.отм. z1, м', 'Высот.отм. z2, м', ' Диаметр трубы, мм', 'Плотность жидкости, кг/м3',
        'Длина трубопровода, м', ' Диаметр отверстия, мм', ' Время отключения давления, с',
        ' Время закрытия арматуры, с'),
    'Испарение жидкости': ('Давление пара, кПа', 'Молярная масса, кг/кмоль', 'Площадь пролива, м2'),
    'Испарение СУГ': ('Молярная масса, кг/кмоль', 'Площадь пролива, м2', 'Скорость ветра, м/с', 'Тем-ра газа, град. С',
                      'Тем-ра поверхности, град. С'),
    'Гидродинамический перелив': ('Высота столба жидкости, м', 'Объем жидкости, м3',
                                  'Расстояние до обвалования, м', 'Высота отбортовки, м'),
    'Эконом.ущерб': ('Кол-во погибщих, чел', 'Кол-во пострадавших, чел', 'Аварийный объем, м3', 'Диаметр тр-да, мм',
                      'Длина тр-да, м', 'Степень уничтожения (0...1)','Исп. масса, т', 'Масса пролива, т','Площадь пролива, м2',)
}

class Calc_gui(QtWidgets.QMainWindow):
    def __init__(self, parent=None) -> None:
        super().__init__()

        self.main_ico = QtGui.QIcon(str(Path(os.getcwd()).parents[0]) + '/calc_safety_v.1.1/ico/calc.png')
        save_ico = QtGui.QIcon(str(Path(os.getcwd()).parents[0]) + '/calc_safety_v.1.1/ico/save.png')
        calc_ico = QtGui.QIcon(str(Path(os.getcwd()).parents[0]) + '/calc_safety_v.1.1/ico/comp.png')
        book_ico = QtGui.QIcon(str(Path(os.getcwd()).parents[0]) + '/calc_safety_v.1.1/ico/book.png')
        question_ico = QtGui.QIcon(str(Path(os.getcwd()).parents[0]) + '/calc_safety_v.1.1/ico/question.png')
        select_ico = QtGui.QIcon(str(Path(os.getcwd()).parents[0]) + '/calc_safety_v.1.1/ico/select.png')

        # Главное окно
        self.resize(1300, 1200)
        self.setWindowTitle('Safety calc (v.1.1)')
        self.setWindowIcon(self.main_ico)

        central_widget = QtWidgets.QWidget()
        grid = QtWidgets.QGridLayout(self)
        grid.setColumnStretch(0, 2)
        grid.setColumnStretch(1, 6)

        # 1.Окно ввода данных
        self.table_data = QtWidgets.QTableWidget(0, 2)
        self.table_data_view()  # фукция отрисовки заголовков таблицы
        # 2. Окно текстового результата и выбранная методика
        self.result_text = QtWidgets.QPlainTextEdit()
        self.selected_method = QtWidgets.QLabel()
        self.selected_method.setText('Пожар пролива')
        self.set_param_names_in_table()
        # Упакуем 1 и 2 в vbox
        layout_data = QtWidgets.QFormLayout(self)
        GB_data = QtWidgets.QGroupBox('Ввод данных и результат')
        GB_data.setStyleSheet("QGroupBox { font-weight : bold; }")
        vbox_data = QtWidgets.QVBoxLayout()
        vbox_data.addWidget(self.table_data)
        vbox_data.addWidget(self.result_text)
        vbox_data.addWidget(self.selected_method)
        layout_data.addRow("", vbox_data)
        GB_data.setLayout(layout_data)
        # 3.График
        self.chart_layout = pg.GraphicsLayoutWidget()
        self.chart_layout.setBackground('w')

        layout_chart = QtWidgets.QFormLayout(self)
        GB_chart = QtWidgets.QGroupBox('Расчетные зависимости')
        GB_chart.setStyleSheet("QGroupBox { font-weight : bold; }")
        layout_chart.addRow("", self.chart_layout)
        GB_chart.setLayout(layout_chart)

        grid.addWidget(GB_data, 0, 0, 1, 1)
        grid.addWidget(GB_chart, 0, 1, 0, 1)
        central_widget.setLayout(grid)
        self.setCentralWidget(central_widget)

        # Меню приложения (верхняя плашка)
        menubar = self.menuBar()
        file_menu = menubar.addMenu('Файл')
        file_menu.addAction(calc_ico, 'Расчет', self.calculation)
        file_menu.addAction(save_ico, 'Сохранить график', self.save_chart)
        # 1. Методики
        method_menu = menubar.addMenu('Методики')
        # 1.1. Горение
        fire_menu = method_menu.addMenu(select_ico, 'Горение')
        fire_menu.addAction(book_ico, 'Пожар пролива', self.change_method)
        fire_menu.addAction(book_ico, 'Пожар-вспышка', self.change_method)
        fire_menu.addAction(book_ico, 'Огненный шар', self.change_method)
        # 2. Взрыв
        expl_menu = method_menu.addMenu(select_ico, 'Взрыв')
        expl_menu.addAction(book_ico, 'Взрыв (СП 12.13130-2009)', self.change_method)
        expl_menu.addAction(book_ico, 'Взрыв (Методика ТВС)', self.change_method)
        # 3. Токсическое поражение
        toxic_menu = method_menu.addMenu(select_ico, 'Токсическое поражение')
        toxic_menu.addAction(book_ico, 'Легкий газ', self.change_method)
        toxic_menu.addAction(book_ico, 'Тяжелый газ (перв.облако)', self.change_method)
        toxic_menu.addAction(book_ico, 'Тяжелый газ (втор.облако)', self.change_method)
        # 4. Количество опасного вещества
        mass_menu = method_menu.addMenu(select_ico, 'Оценка количества опасного вещества')
        mass_menu.addAction(book_ico, 'Истечение газа (емк.)', self.change_method)
        mass_menu.addAction(book_ico, 'Истечение газа (труб.)', self.change_method)
        mass_menu.addAction(book_ico, 'Истечение жидкости (емк.)', self.change_method)
        mass_menu.addAction(book_ico, 'Истечение жидкости (труб.)', self.change_method)
        mass_menu.addAction(book_ico, 'Испарение жидкости', self.change_method)
        mass_menu.addAction(book_ico, 'Испарение СУГ', self.change_method)
        mass_menu.addAction(book_ico, 'Гидродинамический перелив', self.change_method)
        # 5. Ущерб
        damage_menu = method_menu.addMenu(select_ico, 'Эконом.ущерб')
        damage_menu.addAction(book_ico, 'Эконом.ущерб', self.change_method)
        # 6. Справка
        help_menu = menubar.addMenu('Справка')
        help_menu.addAction(question_ico, "Cправка", self.about_prog)

        if not parent:
            self.show()

    def about_prog(self):
        """
        Функция диалоговое окно о программе
        """
        msg = QtWidgets.QMessageBox(self)
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setWindowTitle("Информация")
        msg.setText(f"Разработчик: ООО ИНТЕЛПРОЕКТ (email: inteldocs@yandex.ru)")
        msg.exec()
        webbrowser.open_new(str(Path(os.getcwd()).parents[0]) + '/calc_safety_v.1.1/help/help.pdf')
        return

    def change_method(self):
        """
        Функция для меню при смене методики расчета
        :return:
        """
        # 1. Текст отправителя
        text = self.sender().text()
        # 2. Очистка графика
        self.chart_layout.clear()
        # 3. Очистка результатов расчета
        self.result_text.setPlainText('')
        # 4. Установка для Label selected_method наименование методики
        self.selected_method.setText(text)
        # 5. Установка наименования параметров
        self.set_param_names_in_table()

    def table_data_view(self):
        """
        Функция заголовков таблицы ввода данных (self.table_data)
        """
        item = QtWidgets.QTableWidgetItem('Параметр')
        item.setBackground(QtGui.QColor(150, 225, 225))
        self.table_data.setHorizontalHeaderItem(0, item)

        item = QtWidgets.QTableWidgetItem('Значение')
        item.setBackground(QtGui.QColor(150, 225, 225))
        self.table_data.setHorizontalHeaderItem(1, item)

    def set_param_names_in_table(self):
        """
        Функция отрисовки таблицы для получения
        исходных данных для расчета
        """
        self.table_data.setRowCount(0)
        text = self.selected_method.text()
        name = METODS_AND_PARAMETRS[text]
        rows = len(METODS_AND_PARAMETRS[text])

        for row in range(rows):
            self.table_data.insertRow(row)
            COLUMN = 0  # наименование параметров только в первой колонке
            item = QtWidgets.QTableWidgetItem(name[row])
            item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
            self.table_data.setItem(row, COLUMN, item)
            self.table_data.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)

    def get_data_in_table(self) -> list:
        """
        Функция получения параметров из таблицы, а так же их проверка на число
        :return: data_list - список значений параметров для расчета
        """
        self.table_data.setFocusPolicy(QtCore.Qt.NoFocus)
        data_list = []
        try:
            for row in range(self.table_data.rowCount()):
                data_list.append(float(self.table_data.item(row, 1).text().replace(',', '.')))
        except:
            msg = QtWidgets.QMessageBox(self)
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.setWindowTitle("Информация")
            msg.setText(f"Не все поля заполненны или введены не числовые значения")
            msg.exec()
            return []
        return data_list

    def calculation(self):
        """
        Функция расчета и отрисовки графиков с зависимостями поражающих факторов
        """
        data = self.get_data_in_table()
        if data == []: return

        text = self.selected_method.text()

        if text == 'Пожар пролива':
            radius = calc_strait_fire.Strait_fire().termal_class_zone(*data)
            self.result_text.setPlainText(self.report(text, radius))
            result_tuple = calc_strait_fire.Strait_fire().termal_radiation_array(*data)
            self.create_chart(text, result_tuple)

        elif text == 'Пожар-вспышка':
            radius = calc_lower_concentration.LCLP().lower_concentration_limit(*data)
            self.result_text.setPlainText(self.report(text, radius))

        elif text == 'Огненный шар':
            radius = calc_fireball.Fireball().termal_class_zone(*data)
            self.result_text.setPlainText(self.report(text, radius))
            result_tuple = calc_fireball.Fireball().fireball_array(*data)
            self.create_chart(text, result_tuple)

        elif text == 'Взрыв (СП 12.13130-2009)':
            radius = calc_sp_explosion.Explosion().explosion_class_zone(*data)
            self.result_text.setPlainText(self.report(text, radius))
            result_tuple = calc_sp_explosion.Explosion().explosion_array(*data)
            self.create_chart(text, result_tuple)

        elif text == 'Взрыв (Методика ТВС)':
            radius = calc_tvs_explosion.Explosion().explosion_class_zone(*data)
            self.result_text.setPlainText(self.report(text, radius))
            result_tuple = calc_tvs_explosion.Explosion().explosion_array(*data)
            self.create_chart(text, result_tuple)

        elif text == 'Легкий газ':
            data = calc_light_gas_disp.Source(*data).result()
            self.result_text.setPlainText(self.report(text, []))
            self.create_chart(text, data)

        elif text == 'Тяжелый газ (перв.облако)':
            data = calc_heavy_gas_disp.Instantaneous_source(*data).result()
            self.result_text.setPlainText(self.report(text, []))
            self.create_chart(text, data)

        elif text == 'Тяжелый газ (втор.облако)':
            data = calc_heavy_gas_disp.Continuous_source(*data).result()
            self.result_text.setPlainText(self.report(text, []))
            self.create_chart(text, data)

        elif text == 'Истечение газа (емк.)':
            data = calc_gas_outflow_small_hole.Outflow(*data).result()
            self.result_text.setPlainText(self.report(text, []))
            self.create_chart(text, data)

        elif text == 'Истечение газа (труб.)':
            data = calc_gas_outflow_big_hole.Outflow(*data).result()
            self.result_text.setPlainText(self.report(text, []))
            self.create_chart(text, data)

        elif text == 'Истечение жидкости (емк.)':
            data = calc_liguid_outflow_tank.Outflow(*data).result()
            self.result_text.setPlainText(self.report(text, []))
            self.create_chart(text, data)

        elif text == 'Истечение жидкости (труб.)':
            data = calc_liguid_outflow_pipe.Outflow_in_one_section_pipe(*data).result()
            self.result_text.setPlainText(self.report(text, data[2]))
            self.create_chart(text, data)

        elif text == 'Испарение жидкости':
            data = calc_liguid_evaporation.Liquid_evaporation().evaporation_array(*data)
            self.result_text.setPlainText(self.report(text, data[1]))
            self.create_chart(text, data)

        elif text == 'Испарение СУГ':
            data = calc_evaporation_LPG.LPG_evaporation(*data).evaporation_array()
            self.result_text.setPlainText(self.report(text, []))
            self.create_chart(text, data)

        elif text == 'Гидродинамический перелив':
            data = calc_liquid_overflow.LIGUID_OVERFLOW(*data).overflow_in_moment()
            self.result_text.setPlainText(self.report(text, data[5]))
            self.create_chart(text, data)

        elif text == 'Эконом.ущерб':
            data = calc_damage.Damage(*data).sum_damage()
            self.result_text.setPlainText(self.report(text, data))
            self.create_chart(text, data)

    def report(self, text: str, data: list):
        """
        Функция оформления отчета по зонам действия поражающих факторов
        :param text: - параметр наименования методики
        :param data: - параметр данных (список со значениями радиусов)
        """
        if text == 'Пожар пролива':
            return (f'Зона 10.5 кВт/м2 = {data[0]} м \n'
                    f'Зона 7.0 кВт/м2 = {data[1]} м \n'
                    f'Зона 4.2 кВт/м2 = {data[2]} м \n'
                    f'Зона 1.4 кВт/м2 = {data[3]} м \n')
        elif text == 'Пожар-вспышка':
            return (f'Зона НКПР = {data[0]} м \n'
                    f'Зона Вспышки = {data[1]} м \n')

        elif text == 'Огненный шар':
            return (f'Зона 600 кДж/м2 = {data[0]} м \n'
                    f'Зона 320 кДж/м2 = {data[1]} м \n'
                    f'Зона 220 кДж/м2 = {data[2]} м \n'
                    f'Зона 120 кДж/м2 = {data[3]} м \n')

        elif text == 'Взрыв (СП 12.13130-2009)' or text == 'Взрыв (Методика ТВС)':
            return (f'Зона 100 кПа = {data[0]} м \n'
                    f'Зона 53 кПа = {data[1]} м \n'
                    f'Зона 28 кПа = {data[2]} м \n'
                    f'Зона 12 кПа = {data[3]} м \n'
                    f'Зона 5 кПа = {data[4]} м \n'
                    f'Зона 3 кПа = {data[5]} м \n')

        elif text == 'Легкий газ':
            return (f'Расчет по модели "легкого газа" \n'
                    f'Методика "ТОКСИ-2 (ред.2)"')

        elif text == 'Тяжелый газ (перв.облако)' or text == 'Тяжелый газ (втор.облако)':
            return (f'Расчет по модели "тяжелого газа" \n'
                    f'Авторы Britter and McQuaid')

        elif text == 'Истечение газа (емк.)':
            return (f'Расчет истечения газа из емкости (трубопровода). \n'
                    f'Размер отвестия намного меньше размера оборудования')

        elif text == 'Истечение газа (труб.)':
            return (f'Расчет истечения газа из трубопровода на разрыв. \n'
                    f'Размер отвестия достаточно большой \n'
                    f'для ударной волны, которая движется со скоростью звука \n')

        elif text == 'Истечение жидкости (емк.)':
            return (f'Расчет истечения жидкости из емкости. \n'
                    f'Размер отвестия намного меньше размера оборудования \n')

        elif text == 'Истечение жидкости (труб.)':
            return (f'Расчет истечения жидкости из трубопровода. \n'
                    f'Масса жидкости в проливе{round(sum(data), 1)} кг. \n')

        elif text == 'Испарение жидкости':
            return (f'Расчет испарения ненагретой жидкости. \n'
                    f'Масса испарившейся жидкости {round((data[-1]), 1)} кг. \n')

        elif text == 'Истечение СУГ':
            return (f'Расчет испарения СУГ. \n')

        elif text == 'Гидродинамический перелив':
            return (f'Гидродинамический перелив составляет: {max(data)} % \n')

        elif text == 'Эконом.ущерб':
            return (f'Эконом.ущерб составляет: {round(sum(data),3)} млн.руб \n'
                    f'а) cоц.-эконом. ущерб: {round(data[0],3)} млн.руб \n'
                    f'б) прямой ущерб: {round(data[1],3)} млн.руб \n'
                    f'в) затраты на ЛЛА: {round(data[2],3)} млн.руб \n'
                    f'г) эколог. ущерб: {round(data[3],3)} млн.руб \n')


    def create_chart(self, text: str, data: tuple):
        """
        Функция отрисовки графических зависимостей
        :param text: - параметр наименования методики
        :param data: - параметр данных (список со значениями радиус - воздействие)
        """

        self.chart_layout.clear()
        # Определим ручки для рисования графиков (примем, что максимально показываем 4 зависимости)
        pen1 = pg.mkPen(color=(255, 0, 0), width=3, style=QtCore.Qt.SolidLine)
        pen2 = pg.mkPen(color=(0, 0, 255), width=3, style=QtCore.Qt.SolidLine)
        pen3 = pg.mkPen(color=(0, 255, 0), width=3, style=QtCore.Qt.SolidLine)
        pen4 = pg.mkPen(color=(0, 255, 255), width=3, style=QtCore.Qt.SolidLine)
        styles = {'color': 'b', 'font-size': '15px'}

        if text == 'Пожар пролива':
            radius, q, pr, vp = data
            # Зависимость интенсивности от расстояния
            qraph1 = self.chart_layout.addPlot(x=radius, y=q, pen=pen1, row=0, col=0)
            qraph1.setLabel('left', 'Интенсивность, кВт/м2', **styles)
            qraph1.setLabel('bottom', 'Расстояние от центра пролива, м2', **styles)
            qraph1.showGrid(x=True, y=True)
            # Зависимость пробита от расстояния
            qraph2 = self.chart_layout.addPlot(x=radius, y=pr, pen=pen2, row=1, col=0)
            qraph2.setLabel('left', 'Пробит-функция, -', **styles)
            qraph2.setLabel('bottom', 'Расстояние от центра пролива, м2', **styles)
            qraph2.showGrid(x=True, y=True)
            # Зависимость вероятности поражения от расстояния
            qraph3 = self.chart_layout.addPlot(x=radius, y=vp, pen=pen3, row=2, col=0)
            qraph3.setLabel('left', 'Вероятность поражения, -', **styles)
            qraph3.setLabel('bottom', 'Расстояние от центра пролива, м2', **styles)
            qraph3.showGrid(x=True, y=True)

        elif text == 'Огненный шар':
            radius, q, dose, pr, vp = data

            qraph1 = self.chart_layout.addPlot(x=radius, y=q, pen=pen1, row=0, col=0)
            qraph1.setLabel('left', 'Интенсивность, кВт/м2', **styles)
            qraph1.setLabel('bottom', 'Расстояние, м2', **styles)
            qraph1.showGrid(x=True, y=True)

            qraph2 = self.chart_layout.addPlot(x=radius, y=dose, pen=pen2, row=1, col=0)
            qraph2.setLabel('left', 'Доза, кДж/м2', **styles)
            qraph2.setLabel('bottom', 'Расстояние, м2', **styles)
            qraph2.showGrid(x=True, y=True)

            qraph3 = self.chart_layout.addPlot(x=radius, y=pr, pen=pen3, row=2, col=0)
            qraph3.setLabel('left', 'Пробит-функция, -', **styles)
            qraph3.setLabel('bottom', 'Расстояние, м2', **styles)
            qraph3.showGrid(x=True, y=True)

            qraph4 = self.chart_layout.addPlot(x=radius, y=vp, pen=pen4, row=3, col=0)
            qraph4.setLabel('left', 'Вероятность поражения, -', **styles)
            qraph4.setLabel('bottom', 'Расстояние, м2', **styles)
            qraph4.showGrid(x=True, y=True)

        elif text == 'Взрыв (СП 12.13130-2009)' or text == 'Взрыв (Методика ТВС)':
            radius, pressure, impuls, pr, vp = data

            qraph1 = self.chart_layout.addPlot(x=radius, y=pressure, pen=pen1, row=0, col=0)
            qraph1.setLabel('left', 'Давление, кПа', **styles)
            qraph1.setLabel('bottom', 'Расстояние, м2', **styles)
            qraph1.showGrid(x=True, y=True)

            qraph2 = self.chart_layout.addPlot(x=radius, y=impuls, pen=pen2, row=1, col=0)
            qraph2.setLabel('left', 'Импульс, Па*с', **styles)
            qraph2.setLabel('bottom', 'Расстояние, м2', **styles)
            qraph2.showGrid(x=True, y=True)

            qraph3 = self.chart_layout.addPlot(x=radius, y=pr, pen=pen3, row=2, col=0)
            qraph3.setLabel('left', 'Пробит-функция, -', **styles)
            qraph3.setLabel('bottom', 'Расстояние, м2', **styles)
            qraph3.showGrid(x=True, y=True)

            qraph4 = self.chart_layout.addPlot(x=radius, y=vp, pen=pen4, row=3, col=0)
            qraph4.setLabel('left', 'Вероятность поражения, -', **styles)
            qraph4.setLabel('bottom', 'Расстояние, м2', **styles)
            qraph4.showGrid(x=True, y=True)

        elif text == 'Легкий газ':
            dist, conc, toxic_dose = data

            qraph1 = self.chart_layout.addPlot(x=dist, y=conc, pen=pen1, row=0, col=0)
            qraph1.setLabel('left', 'Концентрация, кг/м3', **styles)
            qraph1.setLabel('bottom', 'Расстояние, м2', **styles)
            qraph1.showGrid(x=True, y=True)

            qraph2 = self.chart_layout.addPlot(x=dist, y=toxic_dose, pen=pen2, row=1, col=0)
            qraph2.setLabel('left', 'Токсодоза, мг*мин/литр', **styles)
            qraph2.setLabel('bottom', 'Расстояние, м2', **styles)
            qraph2.showGrid(x=True, y=True)

        elif text == 'Тяжелый газ (перв.облако)':
            dose, conc, radius, width, _ = data

            qraph1 = self.chart_layout.addPlot(x=radius, y=conc, pen=pen1, row=0, col=0)
            qraph1.setLabel('left', 'Концентрация, кг/м3', **styles)
            qraph1.setLabel('bottom', 'Расстояние, м2', **styles)
            qraph1.showGrid(x=True, y=True)

            qraph2 = self.chart_layout.addPlot(x=radius, y=dose, pen=pen2, row=1, col=0)
            qraph2.setLabel('left', 'Токсодоза, мг*мин/л', **styles)
            qraph2.setLabel('bottom', 'Расстояние, м2', **styles)
            qraph2.showGrid(x=True, y=True)

            qraph3 = self.chart_layout.addPlot(x=radius, y=width, pen=pen3, row=2, col=0)
            qraph3.setLabel('left', 'Ширина облака, м', **styles)
            qraph3.setLabel('bottom', 'Расстояние, м2', **styles)
            qraph3.showGrid(x=True, y=True)

        elif text == 'Тяжелый газ (втор.облако)':
            dose, conc, radius, width = data

            qraph1 = self.chart_layout.addPlot(x=radius, y=conc, pen=pen1, row=0, col=0)
            qraph1.setLabel('left', 'Концентрация, кг/м3', **styles)
            qraph1.setLabel('bottom', 'Расстояние, м2', **styles)
            qraph1.showGrid(x=True, y=True)

            qraph2 = self.chart_layout.addPlot(x=radius, y=dose, pen=pen2, row=1, col=0)
            qraph2.setLabel('left', 'Токсодоза, мг*мин/л', **styles)
            qraph2.setLabel('bottom', 'Расстояние, м2', **styles)
            qraph2.showGrid(x=True, y=True)

            qraph3 = self.chart_layout.addPlot(x=radius, y=width, pen=pen3, row=2, col=0)
            qraph3.setLabel('left', 'Ширина облака, м', **styles)
            qraph3.setLabel('bottom', 'Расстояние, м2', **styles)
            qraph3.showGrid(x=True, y=True)

        elif text == 'Истечение газа (емк.)':
            weight, time, temperature, _, pressure, mass_flow_rate, _, _ = data

            qraph1 = self.chart_layout.addPlot(x=time, y=weight, pen=pen1, row=0, col=0)
            qraph1.setLabel('left', 'Масса газа в емк., кг', **styles)
            qraph1.setLabel('bottom', 'Время, с', **styles)
            qraph1.showGrid(x=True, y=True)

            qraph2 = self.chart_layout.addPlot(x=time, y=temperature, pen=pen2, row=1, col=0)
            qraph2.setLabel('left', 'Температура газа в емк., град.С', **styles)
            qraph2.setLabel('bottom', 'Время, с', **styles)
            qraph2.showGrid(x=True, y=True)

            qraph3 = self.chart_layout.addPlot(x=time, y=pressure, pen=pen3, row=2, col=0)
            qraph3.setLabel('left', 'Давление, МПа', **styles)
            qraph3.setLabel('bottom', 'Время, с', **styles)
            qraph3.showGrid(x=True, y=True)

            qraph4 = self.chart_layout.addPlot(x=time, y=mass_flow_rate, pen=pen4, row=3, col=0)
            qraph4.setLabel('left', 'Расход газа, кг/с', **styles)
            qraph4.setLabel('bottom', 'Время, с', **styles)
            qraph4.showGrid(x=True, y=True)

        elif text == 'Истечение газа (труб.)':
            time, mass_flow_rate = data

            qraph1 = self.chart_layout.addPlot(x=time, y=mass_flow_rate, pen=pen1, row=0, col=0)
            qraph1.setLabel('left', 'Расход, кг/с', **styles)
            qraph1.setLabel('bottom', 'Время, с', **styles)
            qraph1.showGrid(x=True, y=True)

        elif text == 'Истечение жидкости (емк.)':
            _, time, _, height, _, flow_rate, _, mass_leaking = data

            qraph1 = self.chart_layout.addPlot(x=time, y=height, pen=pen1, row=0, col=0)
            qraph1.setLabel('left', 'Высота взлива, м', **styles)
            qraph1.setLabel('bottom', 'Время, с', **styles)
            qraph1.showGrid(x=True, y=True)

            qraph2 = self.chart_layout.addPlot(x=time, y=mass_leaking, pen=pen2, row=1, col=0)
            qraph2.setLabel('left', 'Масса жидкости в проливе, кг', **styles)
            qraph2.setLabel('bottom', 'Время, с', **styles)
            qraph2.showGrid(x=True, y=True)

            qraph3 = self.chart_layout.addPlot(x=time, y=flow_rate, pen=pen3, row=2, col=0)
            qraph3.setLabel('left', 'Расход жидкости, кг/с', **styles)
            qraph3.setLabel('bottom', 'Время, с', **styles)
            qraph3.showGrid(x=True, y=True)

        elif text == 'Истечение жидкости (труб.)':
            mass_liquid, time, flow_rate = data

            qraph1 = self.chart_layout.addPlot(x=time, y=flow_rate, pen=pen1, row=0, col=0)
            qraph1.setLabel('left', 'Расход жидкости, кг/с', **styles)
            qraph1.setLabel('bottom', 'Время, с', **styles)
            qraph1.showGrid(x=True, y=True)

            qraph2 = self.chart_layout.addPlot(x=time, y=mass_liquid, pen=pen2, row=1, col=0)
            qraph2.setLabel('left', 'Масса жидкости в трубопроводе, кг', **styles)
            qraph2.setLabel('bottom', 'Время, с', **styles)
            qraph2.showGrid(x=True, y=True)

        elif text == 'Испарение жидкости':
            time_arr, evaporatiom_arr = data

            qraph1 = self.chart_layout.addPlot(x=time_arr, y=evaporatiom_arr, pen=pen1, row=0, col=0)
            qraph1.setLabel('left', 'Масса испарившейся жидкости, кг', **styles)
            qraph1.setLabel('bottom', 'Время, с', **styles)
            qraph1.showGrid(x=True, y=True)

        elif text == 'Испарение СУГ':
            time_arr, evaporatiom_arr = data

            qraph1 = self.chart_layout.addPlot(x=time_arr, y=evaporatiom_arr, pen=pen1, row=0, col=0)
            qraph1.setLabel('left', 'Масса испарившейся жидкости, кг', **styles)
            qraph1.setLabel('bottom', 'Время, с', **styles)
            qraph1.showGrid(x=True, y=True)

        elif text == 'Гидродинамический перелив':
            t, s, hn, un, x, Q = data

            qraph1 = self.chart_layout.addPlot(x=t, y=hn, pen=pen1, row=0, col=0)
            qraph1.setLabel('left', 'Высота столба жидкости, м', **styles)
            qraph1.setLabel('bottom', 'Время, с', **styles)
            qraph1.showGrid(x=True, y=True)

            qraph2 = self.chart_layout.addPlot(x=t, y=x, pen=pen2, row=1, col=0)
            qraph2.setLabel('left', 'Положение переднего края волны, м', **styles)
            qraph2.setLabel('bottom', 'Время, с', **styles)
            qraph2.showGrid(x=True, y=True)

        elif text == 'Эконом.ущерб':

            y = data
            xlab = ['а', 'б', 'в', 'г']
            xval = list(range(1, len(xlab) + 1))

            ticks = []
            for i, item in enumerate(xlab):
                ticks.append((xval[i], item))
            ticks = [ticks]

            qraph1 = self.chart_layout.addPlot()
            qraph1.setLabel(axis='left', text='Ущерб по видам, млн.руб')
            qraph1.setLabel(axis='bottom', text='Виды ущерба')

            bargraph = pg.BarGraphItem(x=xval, height=y, width=0.5)
            qraph1.addItem(bargraph)
            ax = qraph1.getAxis('bottom')
            ax.setTicks(ticks)

    def save_chart(self):
        exporter = pg_exp.ImageExporter(self.chart_layout.scene())
        desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
        exporter.params.param('width').setValue(1000, blockSignal=exporter.widthChanged)
        exporter.params.param('height').setValue(1000, blockSignal=exporter.heightChanged)
        # save to file
        exporter.export(f'{desktop}/{time.time()}.png')


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    main = Calc_gui()
    app.exec()
