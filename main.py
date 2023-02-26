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

from PySide6 import QtWidgets, QtGui, QtCore
import pyqtgraph as pg
import pyqtgraph.exporters as pg_exp


METHODS = ('Пожар пролива', 'Взрыв (СП 12.13130-2009)', 'Взрыв (Методика ТВС)', 'Огненный шар', 'Пожар-вспышка',
           'Испарение ненагретой жидкости')


class Calc_gui(QtWidgets.QMainWindow):
    def __init__(self, parent=None) -> None:
        super().__init__()

        self.main_ico = QtGui.QIcon(str(Path(os.getcwd()).parents[0]) + '/calc_safety_v.1.1/ico/calc.png')
        save_ico = QtGui.QIcon(str(Path(os.getcwd()).parents[0]) + '/calc_safety_v.1.1/ico/save.png')
        calc_ico = QtGui.QIcon(str(Path(os.getcwd()).parents[0]) + '/calc_safety_v.1.1/ico/comp.png')
        book_ico = QtGui.QIcon(str(Path(os.getcwd()).parents[0]) + '/calc_safety_v.1.1/ico/book.png')
        question_ico = QtGui.QIcon(str(Path(os.getcwd()).parents[0]) + '/calc_safety_v.1.1/ico/question.png')

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
        GB_chart = QtWidgets.QGroupBox('Графическое отображение')
        GB_chart.setStyleSheet("QGroupBox { font-weight : bold; }")
        layout_chart.addRow("", self.chart_layout)
        GB_chart.setLayout(layout_chart)

        grid.addWidget(GB_data, 0, 0, 1, 1)
        grid.addWidget(GB_chart, 0, 1, 0, 1)
        central_widget.setLayout(grid)
        self.setCentralWidget(central_widget)

        # Меню приложения (верхняя плашка)
        # 1. file_menu
        # 1.1. Расчет
        calc_menu = QtGui.QAction(calc_ico, 'Расчет', self)
        calc_menu.setShortcut('Ctrl+D')
        calc_menu.setStatusTip('Провести расчет')
        # calc_menu.triggered.connect(self.calculate)
        # 1.2. График
        chart_menu = QtGui.QAction(save_ico, 'Сохранить график', self)
        chart_menu.setShortcut('Ctrl+A')
        chart_menu.setStatusTip('Сохранить график в JPG')
        # chart_menu.triggered.connect(self.save_chart)
        # 1.3. Выбор методики
        method_menu = QtWidgets.QMenu('Выбор методики расчета', self)
        method_menu.setIcon(book_ico)
        # 1.3.1. Пожар пролива
        strait_fire_calc = QtGui.QAction(book_ico, 'Пожар пролива', self)
        # strait_fire_calc.triggered.connect(self.change_method)
        method_menu.addAction(strait_fire_calc)
        # 1.3.2. Взрыв СП
        explosion_sp_calc = QtGui.QAction(book_ico, 'Взрыв (СП 12.13130-2009)', self)
        # explosion_sp_calc.triggered.connect(self.change_method)
        # method_menu.addAction(explosion_sp_calc)
        # 1.3.3. Взрыв ТВС
        explosion_tvs_calc = QtGui.QAction(book_ico, 'Взрыв (Методика ТВС)', self)
        # explosion_tvs_calc.triggered.connect(self.change_method)
        # method_menu.addAction(explosion_tvs_calc)
        # 1.3.4. Огненный шар
        fireball_calc = QtGui.QAction(book_ico, 'Огненный шар', self)
        # fireball_calc.triggered.connect(self.change_method)
        # 1.3.4. Вспышка-НКПР
        lclp_calc = QtGui.QAction(book_ico, 'Пожар-вспышка', self)
        # lclp_calc.triggered.connect(self.change_method)
        # 1.3.4. Вспышка-НКПР
        evaporation_calc = QtGui.QAction(book_ico, 'Испарение ненагретой жидкости', self)
        # evaporation_calc.triggered.connect(self.change_method)
        # 1.3._. Вспышка-НКПР
        about_prog = QtGui.QAction(question_ico, "Cправка", self)
        # about_prog.triggered.connect(self.about_prog)

        # Меню
        menubar = self.menuBar()
        file_menu = menubar.addMenu('Файл')
        file_menu.addAction(calc_menu)
        file_menu.addAction(chart_menu)
        method_menu = menubar.addMenu('Методики')
        method_menu.addAction(strait_fire_calc)
        method_menu.addAction(explosion_sp_calc)
        method_menu.addAction(explosion_tvs_calc)
        method_menu.addAction(fireball_calc)
        method_menu.addAction(lclp_calc)
        method_menu.addAction(evaporation_calc)
        help_menu = menubar.addMenu('Справка')
        help_menu.addAction(about_prog)

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
        return

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
        self.table_data.setRowCount(0)
        text = self.selected_method.text()
        names = [('Площадь, м2', 'm, кг/(с*м2) ', 'Mmol, кг/кмоль', 'Ткип, град.С', 'Ветер, м/с'),
                 ('Масса, кг', 'Qсг, кДж/кг ', 'z, -'),
                 ('Класс в-ва', 'Класс прост-ва', 'Масса, кг', 'Qсг, кДж/кг', 'sigma, -', 'Энергозапас, -'),
                 ('Масса, кг', 'Ef, кВт/м2'), ('Масса, кг', 'Mmol, кг/кмоль', 'Ткип, град.С', 'НКПР, об.%'),
                 ('Давление пара, кПа', 'Mmol, кг/кмоль', 'Площадь пролива, м2')]
        rows_tuple = (5, 3, 6, 2, 4, 3)

        ind = METHODS.index(text)
        name = names[ind]
        rows = rows_tuple[ind]

        for row in range(rows):
            self.table_data.insertRow(row)
            for col in range(2):
                if col == 0:
                    item = QtWidgets.QTableWidgetItem(name[row])
                    item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
                    self.table_data.setItem(row, col, item)
                    self.table_data.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)

    def change_method(self):
        text = self.sender().text()
        self.chart_layout.clear()
        self.result_text.setPlainText('')
        self.selected_method.setText(text)
        self.set_param_names_in_table()

    def get_data_in_table(self):
        if not self.chek_server():
            return
        self.table_data.setFocusPolicy(QtCore.Qt.NoFocus)
        data_list = []
        try:
            for row in range(self.table_data.rowCount()):
                data_list.append(self.table_data.item(row, 1).text().replace(',', '.'))
        except:
            msg = QtWidgets.QMessageBox(self)
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.setWindowTitle("Информация")
            msg.setText(f"Не все поля заполненны")
            msg.exec()
            return

        # Повека корректнос веденх значений
        text = self.selected_method.text()
        chek = [(float, float, float, float, float), (float, float, float), (int, int, float, float, float, float),
                (float, float), (int, float, float, float), (float, float, float)]
        ind = METHODS.index(text)

        for i in data_list:
            try:
                chek[ind][data_list.index(i)](i)
            except:
                msg = QtWidgets.QMessageBox(self)
                msg.setIcon(QtWidgets.QMessageBox.Warning)
                msg.setWindowTitle("Информация")
                msg.setText(f"Не верно указана характеристика: {i}")
                msg.exec()
                return
        return data_list

    def chek_server(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((IP, 8888))
            sock.close()
            return True
        except:
            msg = QtWidgets.QMessageBox(self)
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.setWindowTitle("Информация")
            msg.setText(f"Нет подключения к серверу!")
            msg.exec()
            return False

    def recvall(self, sock):
        BUFF_SIZE = 256  # 4 KiB
        data = b''
        while True:
            part = sock.recv(BUFF_SIZE)
            data += part
            if len(part) == 0:
                break
        return data

    def get_zone_in_server(self, data: list):
        text = self.selected_method.text()
        ind = METHODS.index(text)
        server_call = (2, 5, 8, 11, 12, 13)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((IP, 8888))
        str = f'({server_call[ind]}, {data})'
        sock.send(bytes(str, encoding='utf-8'))
        res = self.recvall(sock)
        sock.close()
        return res

    def get_data_for_chart_in_server(self, data: list):
        text = self.selected_method.text()
        ind = METHODS.index(text)
        if ind == 0:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((IP, 8888))
            str = f'(1, {data})'
            sock.send(bytes(str, encoding='utf-8'))
            res = self.recvall(sock)
            sock.close()
            return res
        elif ind == 1:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((IP, 8888))
            str = f'(4, {data})'
            sock.send(bytes(str, encoding='utf-8'))
            res = self.recvall(sock)
            sock.close()
            return res

        elif ind == 2:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((IP, 8888))
            str = f'(7, {data})'
            sock.send(bytes(str, encoding='utf-8'))
            res = self.recvall(sock)
            sock.close()
            return res

        elif ind == 3:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((IP, 8888))
            str = f'(10, {data})'
            sock.send(bytes(str, encoding='utf-8'))
            res = self.recvall(sock)
            sock.close()
            return res

        elif ind == 5:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((IP, 8888))
            str = f'(14, {data})'
            sock.send(bytes(str, encoding='utf-8'))
            res = self.recvall(sock)
            sock.close()
            return res

    def report(self, data: list):
        text = self.selected_method.text()
        ind = METHODS.index(text)

        if ind == 0:
            return (f'Зона 10.5 кВт/м2 = {data[0]} м \n'
                    f'Зона 7.0 кВт/м2 = {data[1]} м \n'
                    f'Зона 4.2 кВт/м2 = {data[2]} м \n'
                    f'Зона 1.4 кВт/м2 = {data[3]} м \n')

        elif ind == 1:
            return (f'Зона 100 кПа = {data[0]} м \n'
                    f'Зона 53 кПа = {data[1]} м \n'
                    f'Зона 28 кПа = {data[2]} м \n'
                    f'Зона 12 кПа = {data[3]} м \n'
                    f'Зона 5 кПа = {data[4]} м \n'
                    f'Зона 3 кПа = {data[5]} м \n')

        elif ind == 2:
            return (f'Зона 100 кПа = {data[0]} м \n'
                    f'Зона 53 кПа = {data[1]} м \n'
                    f'Зона 28 кПа = {data[2]} м \n'
                    f'Зона 12 кПа = {data[3]} м \n'
                    f'Зона 5 кПа = {data[4]} м \n'
                    f'Зона 3 кПа = {data[5]} м \n')

        elif ind == 3:
            return (f'Зона 600 кДж/м2 = {data[0]} м \n'
                    f'Зона 320 кДж/м2 = {data[1]} м \n'
                    f'Зона 220 кДж/м2 = {data[2]} м \n'
                    f'Зона 120 кДж/м2 = {data[3]} м \n')

        elif ind == 4:
            return (f'Зона НКПР = {data[0]} м \n'
                    f'Зона Вспышки = {data[1]} м \n')
        elif ind == 5:
            return (f'Испарение за 3600 секунд составит {round(data[0], 1)} кг')

    def calculate(self):
        data_list = self.get_data_in_table()
        if data_list == None:
            return

        zone = self.get_zone_in_server(data_list)
        for_chart = self.get_data_for_chart_in_server(data_list)
        self.result_text.setPlainText(self.report(eval(zone)))
        self.create_chart(for_chart)

    def create_chart(self, data: bytes):
        text = self.selected_method.text()
        ind = METHODS.index(text)

        self.chart_layout.clear()
        pen1 = pg.mkPen(color=(255, 0, 0), width=3, style=QtCore.Qt.SolidLine)
        pen2 = pg.mkPen(color=(0, 0, 255), width=3, style=QtCore.Qt.SolidLine)
        pen3 = pg.mkPen(color=(0, 255, 0), width=3, style=QtCore.Qt.SolidLine)
        pen4 = pg.mkPen(color=(0, 255, 255), width=3, style=QtCore.Qt.SolidLine)
        styles = {'color': 'b', 'font-size': '15px'}

        if not ind == 4:
            data = eval(data)
        else:
            return

        if ind == 0:
            radius = [float(i) for i in data[0]]
            q = [float(i) for i in data[1]]
            pr = [float(i) for i in data[2]]
            vp = [float(i) for i in data[3]]

            qraph1 = self.chart_layout.addPlot(x=radius, y=q, pen=pen1, row=0, col=0)
            qraph1.setLabel('left', 'Интенсивность, кВт/м2', **styles)
            qraph1.setLabel('bottom', 'Расстояние от центра пролива, м2', **styles)
            qraph1.showGrid(x=True, y=True)

            qraph2 = self.chart_layout.addPlot(x=radius, y=pr, pen=pen2, row=1, col=0)
            qraph2.setLabel('left', 'Пробит-функция, -', **styles)
            qraph2.setLabel('bottom', 'Расстояние от центра пролива, м2', **styles)
            qraph2.showGrid(x=True, y=True)

            qraph3 = self.chart_layout.addPlot(x=radius, y=vp, pen=pen3, row=2, col=0)
            qraph3.setLabel('left', 'Вероятность поражения, -', **styles)
            qraph3.setLabel('bottom', 'Расстояние от центра пролива, м2', **styles)
            qraph3.showGrid(x=True, y=True)

        if ind == 1:
            radius = [float(i) for i in data[0]]
            pressure = [float(i) for i in data[1]]
            impuls = [float(i) for i in data[2]]
            pr = [float(i) for i in data[3]]
            vp = [float(i) for i in data[4]]

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

        if ind == 2:
            radius = [float(i) for i in data[0]]
            pressure = [float(i) for i in data[1]]
            impuls = [float(i) for i in data[2]]
            pr = [float(i) for i in data[3]]
            vp = [float(i) for i in data[4]]

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

        if ind == 3:
            radius = [float(i) for i in data[0]]
            q = [float(i) for i in data[1]]
            dose = [float(i) for i in data[2]]
            pr = [float(i) for i in data[3]]
            vp = [float(i) for i in data[4]]

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

        if ind == 5:
            time = [float(i) for i in data[0]]
            mass = [float(i) for i in data[1]]

            qraph1 = self.chart_layout.addPlot(x=time, y=mass, pen=pen1, row=0, col=0)
            qraph1.setLabel('left', 'Масса, кг', **styles)
            qraph1.setLabel('bottom', 'Время, с', **styles)
            qraph1.showGrid(x=True, y=True)

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
