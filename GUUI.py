__author__ = 'alexandra'
from gi.repository import Gtk, Gdk
from Crossword import Crossword


class CrosswordWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Кроссворд")
        self.crossword = Crossword()
        okay_button = Gtk.Button("ОК")
        okay_button.connect("clicked", self.on_ok_clicked)
        reset_button = Gtk.Button("Сброс")
        reset_button.connect("clicked", self.on_reset_clicked)
        self.frame = Gtk.Frame()
        table = Gtk.Table()
        self.frame.add(table)
        self.frame.set_size_request(650, 650)
        self.dict_file = ''
        self.matrix_geometry = []
        self.cells = []
        self.cells_areas = []
        self.flag_successful_filling = False
        self.pressed_cells = []
        geometry_str = ''
        for i in range(25):
            for j in range(25):
                geometry_str += '0'
            geometry_str += '\n'
            self.matrix_geometry.append(geometry_str)
            geometry_str = ''
        fixed = Gtk.Fixed()
        fixed.add(self.add_menu_bar())
        fixed.put(self.frame, 0, 0)
        self.add(fixed)
        okay_button.set_size_request(80, 30)
        reset_button.set_size_request(80, 30)
        fixed.put(okay_button, 200, 680)
        fixed.put(reset_button, 320, 680)
        fixed.show_all()
        for i in range(25):
            self.areas_list = []
            self.cells_list = []
            for j in range(25):
                button_and_area = self.new_button_and_color_area()
                button = button_and_area[0]
                button.show()
                area = button_and_area[1]
                self.areas_list.append(area)
                self.cells_list.append(button)
                button.set_size_request(20, 20)
                button.connect("clicked", self.on_cell_clicked, i, j, area)
                button.connect_object("event", self.button_press, "press")
                table.attach(button, i, i + 1, j, j + 1)
            self.cells.append(self.cells_list)
            self.cells_areas.append(self.areas_list)

    def button_press(self, widget, event):
        if event.type == Gtk.Gdk.BUTTON_PRESS and event.button == 3:
            print("fg")

    def add_menu_bar(self):
        """
        Создает меню.
        :return: меню.
        """
        menu_bar = Gtk.MenuBar()
        file_menu = Gtk.Menu()
        help_menu = Gtk.Menu()
        file_item = Gtk.MenuItem("Файл")
        help_item = Gtk.MenuItem("Помощь")
        open_item = Gtk.MenuItem("Добавить словарь..")
        quit_item = Gtk.MenuItem("Выход")
        information_item = Gtk.MenuItem("О задаче")
        self.save_as_item = Gtk.MenuItem("Сохранить как..")
        self.save_as_item.set_sensitive(False)
        open_item.connect_object("activate", self.show_select, "file.open")
        self.save_as_item.connect_object("activate", self.show_file_save_as, "file.save")
        quit_item.connect_object("activate", self.destroy, "file.quit")
   #     information_item.connect_object("activate", self.show_help, "file.help")
        file_menu.append(open_item)
        file_menu.append(self.save_as_item)
        file_menu.append(quit_item)
        help_menu.append(information_item)
        file_item.set_submenu(file_menu)
        help_item.set_submenu(help_menu)
        menu_bar.append(file_item)
        menu_bar.append(help_item)
        return menu_bar

    @staticmethod
    def destroy(widget):
        """
        Уничтожает диалоговые окна.
        :param widget: ссылка на виджет, к которому был применен сигнал.
        """
        Gtk.main_quit()

    @staticmethod
    def new_button_and_color_area():
        """
        Создает новую кнопку (которая будет использоваться как клетка для задания геометрии)
        и цветную прямоугольную область для неё (изначально невидимую).
        :return: кнопку и область.
        """
        color = Gdk.color_parse("coral")
        rgba = Gdk.RGBA.from_color(color)
        button = Gtk.Button()
        area = Gtk.DrawingArea()
        area.set_size_request(6, 6)
        area.set_no_show_all(True)
        area.override_background_color(0, rgba)
        button.add(area)
        return [button, area]

    def on_cell_clicked(self, widget, i, j, area):
        """
        Вызывается после нажатия на клетку. Изменяет геометрию кроссворда в зависимсоти от того,
        какая клетка была нажата.
        :param widget: ссылка на виджет, к которому был применен сигнал.
        :param i: первая координата клетки.
        :param j: вторая координата клетки.
        :param area: прямоугольная область из клетки.
        """
        if area.get_no_show_all():
            area.show()
            area.set_no_show_all(False)
            self.matrix_geometry[i] = self.matrix_geometry[i][:j] + '*' +\
                self.matrix_geometry[i][j+1:]
            self.pressed_cells.append(area)
        else:
            area.hide()
            area.set_no_show_all(True)
            self.matrix_geometry[i] = self.matrix_geometry[i][:j] + '0' +\
                self.matrix_geometry[i][j+1:]
            self.pressed_cells.remove(area)

    def on_ok_clicked(self, widget):
        """
        Вызывается после нажатия на кнопку "ОК". Вызывает метод заполнения кроссворда.
        В соостветствии с заполненной геометрией удаляет цветную область из клетки
        и добавляет туда нужную букву. Вызов метода показа ошибки и выход из функции в случае,
         если не был загружен словарь.
        :param widget: ссылка на виджет, к которому был применен сигнал.
        :return: None.
        """
        self.crossword.geometry_strs = self.matrix_geometry
        self.crossword.set_all_coordinates()
        if self.dict_file == '':
            self.show_error("Не был добавлен словарь.")
            return
        self.crossword.set_words_and_lengths(self.dict_file)
        self.flag_successful_filling = self.crossword.write_in_words()
        if self.flag_successful_filling:
            self.save_as_item.set_sensitive(True)
        else:
            self.show_error("Невозможно заполнить кроссворд.")
        self.adding_vertic_letters = self.crossword.adding_vertical_letters
        self.adding_horiz_letters = self.crossword.adding_horizontal_letters
        for i in range(len(self.crossword.geometry_strs)):
            for j in range(len(self.crossword.geometry_strs[i])):
                if (i, j) in self.crossword.adding_horizontal_letters:
                    self.cells_areas[i][j].hide()
                    self.cells_areas[i][j].set_no_show_all(True)
                    child_widget = self.cells[i][j].get_children()
                    self.cells[i][j].remove(child_widget[0])
                    box = Gtk.Box()
                    cell_title = '<span foreground="red" size="small">' +\
                                 self.crossword.adding_horizontal_letters[(i, j)] + '</span>'
                    label = Gtk.Label(cell_title)
                    label.set_use_markup(True)
                    box.add(label)
                    box.show_all()
                    self.cells[i][j].add(box)
                    continue
                if (j, i) in self.crossword.adding_vertical_letters:
                    self.cells_areas[i][j].hide()
                    self.cells_areas[i][j].set_no_show_all(True)
                    child_widget = self.cells[i][j].get_children()
                    self.cells[i][j].remove(child_widget[0])
                    box = Gtk.Box()
                    cell_title = '<span foreground="red" size="small">' +\
                                 self.crossword.adding_vertical_letters[(j, i)] + '</span>'
                    label = Gtk.Label(cell_title)
                    label.set_use_markup(True)
                    box.add(label)
                    box.show_all()
                    self.cells[i][j].add(box)
                    continue
        self.crossword.set_default_values()

    def on_reset_clicked(self, widget):
        """
        Проходит по клеткам. Если там сейчас буква, то она удаляется и добавляется
        невидимая прямоугольная область. Если там в данный момент видимая прямоугольная область, то
        она также становится невидимой. Также "обнуляется" геометрия кроссворда.
        :param widget: ссылка на виджет, к которому был применен сигнал.
        :return: None.
        """
        self.save_as_item.set_sensitive(False)
        if self.flag_successful_filling:
            for i in self.adding_horiz_letters:
                x = i[0]
                y = i[1]
                self.cells[x][y].remove(self.cells[x][y].get_children()[0])
                self.cells[x][y].add(self.cells_areas[x][y])
                self.matrix_geometry[x] = self.matrix_geometry[x][:y] + '0' +\
                    self.matrix_geometry[x][y+1:]
            for i in self.adding_vertic_letters:
                y = i[0]
                x = i[1]
                self.cells[x][y].remove(self.cells[x][y].get_children()[0])
                self.cells[x][y].add(self.cells_areas[x][y])
                self.matrix_geometry[x] = self.matrix_geometry[x][:y] + '0' \
                    + self.matrix_geometry[x][y+1:]
            self.crossword.set_default_values()
            self.flag_successful_filling = False
            return
        for i in range(len(self.cells_areas)):
            for j in range(len(self.cells_areas[i])):
                self.cells_areas[i][j].hide()
                self.cells_areas[i][j].set_no_show_all(True)
                child = self.cells[i][j].get_children()[0]
                self.cells[i][j].remove(child)
                self.cells[i][j].add(self.cells_areas[i][j])
        for i in range(len(self.matrix_geometry)):
            self.matrix_geometry[i] = self.matrix_geometry[i].replace('*', "0")
        self.crossword.set_default_values()

    def show_select(self, _):
        """
        Создает окно добавления файла со словарем.
        :param _: ссылка на виджет, к которому был применен сигнал.
        """
        dialog = Gtk.Dialog("Выберите словарь", self, 0,
                            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                             Gtk.STOCK_OK, Gtk.ResponseType.OK))
        dialog.set_default_size(250, 100)
        fixed = Gtk.Fixed()
        open_button = Gtk.Button("Открыть")
        self.select_file_entry = Gtk.Entry()
        self.select_file_entry.set_size_request(300, 30)
        self.select_file_entry.set_editable(False)
        self.select_file_entry.set_text(self.dict_file)
        open_button.connect("clicked", self.show_file_open, "null")
        fixed.put(self.select_file_entry, 0, 0)
        fixed.put(open_button, 305, 0)
        box = dialog.get_content_area()
        box.add(fixed)
        dialog.show_all()
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.dict_file = self.select_file_entry.get_text()
            dialog.destroy()
        dialog.destroy()

    def show_file_open(self, _, __):
        """
        Вызывается после на "Открыть" в окне добавления файла со словарем.
        :param widget: ссылка на виджет, к которому был применен сигнал.
        """
        dialog = Gtk.FileChooserDialog("Выберите файл", self, Gtk.FileChooserAction.OPEN,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN,
                                        Gtk.ResponseType.OK))
        text_filter = Gtk.FileFilter()
        text_filter.set_name("Текстовые файлы")
        text_filter.add_mime_type("text/plain")
        dialog.add_filter(text_filter)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.select_file_entry.set_text(dialog.get_filename())
        dialog.destroy()

    def show_error(self, text):
        """
        Вызывается в случае, если не был добавлен файл со словарем.
        """
        secondary_text = ""
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR,
                                   Gtk.ButtonsType.OK, text)
        dialog.format_secondary_text(secondary_text)
        dialog.run()
        dialog.destroy()

    def show_file_save_as(self, widget):
        """
        Вызывается через меню после нажатия на "File" --> "Сохранить как".
        :param widget: ссылка на виджет, к которому был применен сигнал.
        """
        dialog = Gtk.FileChooserDialog("Выберите файл", self, Gtk.FileChooserAction.SAVE,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_SAVE, Gtk.ResponseType.OK))
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            result = ''
            out_str = ''
            for i in range(len(self.matrix_geometry)):
                for j in range(len(self.matrix_geometry[i])):
                    if (i, j) in self.adding_horiz_letters:
                        out_str += self.adding_horiz_letters[(i, j)]
                        continue
                    if (j, i) in self.adding_vertic_letters:
                        out_str += self.adding_vertic_letters[(j, i)]
                        continue
                    out_str += ' '
                result += out_str + "\n"
            with open(dialog.get_filename(), "w") as output_file:
                output_file.write(result)
        dialog.destroy()



win = CrosswordWindow()
win.connect("delete-event", Gtk.main_quit)
win.show()
Gtk.main()