__author__ = 'alexandra'


class Crossword:
    def __init__(self):
        self.geometry_strs = []
        self.geometry_columns = []
        self.horizontal_coordinates = []
        self.vertical_coordinates = []
        self.horizontal_words_length = []
        self.vertical_words_length = []
        self.dict_words = []
        self.dict_words_length = []
        self.adding_horizontal_letters = {}
        self.adding_vertical_letters = {}
        self.fail_ways = []
        self.current_way = []
        self.viewed_horizontal_coordinates = [0]
        self.viewed_vertical_coordinates = [0]
        self.finded_position = [-1]
        self.crossword = ''

    def set_geometry(self, file_name):
        """
        Считывание геометрии из файла. Добавление построчно в список.
        :param file_name: имя файла с геометрией.
        """
        file_reader = open(file_name)
        for i in file_reader:
            self.geometry_strs.append(i)
        file_reader.close()

    @staticmethod
    def get_coordinates_and_lengths(geometry):
        """
        Анализация строк геометрии. Составление координат для каждой буквы.
        :param geometry: строки геометрии.
        :return: список координат + список длин для каждого слова.
        """
        strs_count = 0
        coordinates = []
        words_lengths = []
        for i in geometry:
            i += "\n"
            count_letter = 0
            for j in range(len(i)):
                if i[j] != '*' and count_letter > 1:
                    coordinates +=\
                        ([(strs_count, j - p - 1) for p in reversed(range(count_letter))])
                    words_lengths.append(count_letter)
                if i[j] == '*':
                    count_letter += 1
                if i[j] != '*':
                    count_letter = 0
            strs_count += 1
        return [words_lengths] + [coordinates]

    def set_all_coordinates(self):
        """
        Добавление всех координат (по горизонтали и по вертикали), а также длин горизонтальных
        и вертикальных слов.
        Сначала вызываем метод добавления координатов и длинн для горизонтальных слов, а затем
        строки геометрии транспонируются и вызывается метод добавления координатов и
        длинн для вертикальных слов.
        """
        horizontal_coordinates_and_lengths = self.get_coordinates_and_lengths(self.geometry_strs)
        self.horizontal_coordinates = horizontal_coordinates_and_lengths[1]
        self.horizontal_words_length = horizontal_coordinates_and_lengths[0]
        max_length = max(len(i) for i in self.geometry_strs)
        for i in range(max_length):
            transposed_str = ''
            for j in range(len(self.geometry_strs)):
                if i < len(self.geometry_strs[j]):
                    transposed_str += self.geometry_strs[j][i]
                else:
                    transposed_str += '0'
            self.geometry_columns.append(transposed_str)
        vertical_coordinates_and_lengths = self.get_coordinates_and_lengths(self.geometry_columns)
        self.vertical_coordinates = vertical_coordinates_and_lengths[1]
        self.vertical_words_length = vertical_coordinates_and_lengths[0]

    def set_words_and_lengths(self, dict_file):
        """
        Получение слов из словаря и длину для каждого из них.
        :param dict_file: файл со словарем.
        """
        file_reader = open(dict_file)
        for i in file_reader:
            self.dict_words.append(i[:-1])
            self.dict_words_length.append(len(i) - 1)
        file_reader.close()

    def add_word(self, words_lengths, coordinates, index, opposite_coordinates, adding_letters,
                 viewed_coordinates_number, opposite_adding_letters):
        """
        Вызывается из метода "write_in_words". В зависимости от того, как вызван данный метод,
        пытаемся подставить либо вертикальное, либо горизонтальное слово. Сначала ищем слово
        необходимой длины среди словарных слов. Если оно есть, то проверяем, будет ли текущий путь
        найденных слов входить в список неудачных путей. В таком случаем заполняем кроссворд заново,
        избегая неудачный путь.
        Если не входит в список неудачных путей, то пытаемся подставить каждую букву. При этои
        текущие заполненные буквы должны быть равны соответствующим буквам из слова. Также для
        каждой координаты проверяем, содержится ли точно такая же координата(только с
        переставленными значениями) в противоположно заполняемом словаре (при гориз. заполнении
        противоложно заполняемый словарь - вертикальный, при вертик. - гориз.). Сверяем и эти буквы.
        Если оказалось, что слово не подходит, то ведем поиск со следующей позиции.
        :param words_lengths: длины слов(в зависимости от того, как вызван метод, либо вертик.,
        либо горизонтальные)
        :param coordinates: координата каждой буквы(в зависимости от того, как вызван метод,
         либо вертик., либо горизонтальные)
        :param index: тещая позиция просмотра списка длин словарных слов.
        :param opposite_coordinates: противоположные координаты.
        :param adding_letters: заполненные горизонтальные или вертикальные буквы(в зависимости от
         того, как вызван метод).
        :param viewed_coordinates_number: число просмотренных координат(вертикальных или
         горизонтальных).
        :param opposite_adding_letters: противоположные заполненные буквы.
        :return: сигнал о том, как прошло заполнение.
        """
        try:
            self.dict_words_length.index(words_lengths[index], self.finded_position[0] + 1)
        except ValueError:
            if len(adding_letters) != 0:
                self.fail_ways.append(self.current_way)
                return 'заполнение заново'
            else:
                return 'невозможно заполнить'
        word_position = self.dict_words_length.index(words_lengths[index], self.finded_position[0]
                                                     + 1)
        self.finded_position[0] = word_position
        check_in_fail_ways = self.current_way[:]
        check_in_fail_ways.append(word_position)
        if check_in_fail_ways in self.fail_ways:
            return "подставляем другое слово"
        word = self.dict_words[word_position]
        flag = False
        for j in range(len(word)):
            if coordinates[viewed_coordinates_number[0] + j] in adding_letters\
                    and adding_letters[coordinates[viewed_coordinates_number[0] + j]] != word[j]:
                flag = True
        if not flag:
            self.current_way.append(word_position)
            for j in range(len(word)):
                adding_letters[coordinates[viewed_coordinates_number[0] + j]] = word[j]
                revers_coordinate = list(coordinates[viewed_coordinates_number[0] + j])
                revers_coordinate.reverse()
                revers_coordinate = tuple(revers_coordinate)
                if revers_coordinate in opposite_coordinates:
                    opposite_adding_letters[revers_coordinate] = word[j]
            viewed_coordinates_number[0] += len(word)
            self.finded_position[0] = -1
            return "удачное заполнение"
        return 'подставляем другое слово'

    def write_in_words(self):
        """
        В данном методе находится цикл вызовов метода add_word. Заполнение проиходит поочередно до
        тех пор, пока это возможно. Т.е. если поставлены все вертикальные слова, то дальше будут
        поставляться только горизонтальные. Если получили сигнал из функции add_word о том,
        что кроссворд необходимо заполнять заново, присваиваем всем необходимым переменным начальное
        значение(а также обнуляем счетчик цикла). Если получили сигнал, о том, что необходмо
        поставить другое слово, не изменяем счетчик цикла. Если заполнение удачное, увеличиваем
        счетчик. Если невозможно заполнить кроссворд - выход из функции.
        :return: возможно заполнить кроссворд - True. невозможно - False
        """
        i = 0
        flag = True
        max_words_number = max(len(self.horizontal_words_length), len(self.vertical_words_length))
        while i < max_words_number:
            if i < len(self.horizontal_words_length) and flag:
                result = self.add_word(self.horizontal_words_length, self.horizontal_coordinates, i,
                                       self.vertical_coordinates, self.adding_horizontal_letters,
                                       self.viewed_horizontal_coordinates,
                                       self.adding_vertical_letters)
                if result == 'заполнение заново':
                    i = 0
                    self.adding_horizontal_letters = {}
                    self.adding_vertical_letters = {}
                    self.viewed_horizontal_coordinates = [0]
                    self.viewed_vertical_coordinates = [0]
                    self.finded_position = [-1]
                    self.current_way = []
                    continue
                if result == 'подставляем другое слово':
                    continue
                if result == 'удачное заполнение':
                    self.finded_position = [-1]
                if result == 'невозможно заполнить':
                    return False
            if i < len(self.vertical_words_length):
                flag = 1
                result = self.add_word(self.vertical_words_length, self.vertical_coordinates, i,
                                       self.horizontal_coordinates, self.adding_vertical_letters,
                                       self.viewed_vertical_coordinates,
                                       self.adding_horizontal_letters)
                if result == 'заполнение заново':
                    i = 0
                    self.adding_horizontal_letters = {}
                    self.adding_vertical_letters = {}
                    self.viewed_horizontal_coordinates = [0]
                    self.viewed_vertical_coordinates = [0]
                    self.finded_position = [-1]
                    self.current_way = []
                    continue
                if result == 'подставляем другое слово':
                    flag = False
                    continue
                if result == 'удачное заполнение':
                    self.finded_position = [-1]
                if result == 'невозможно заполнить':
                    return False
            i += 1
        self.crossword = self.output_crossword()
        return True

    def set_default_values(self):
        self.geometry_strs = []
        self.geometry_columns = []
        self.horizontal_coordinates = []
        self.vertical_coordinates = []
        self.horizontal_words_length = []
        self.vertical_words_length = []
        self.dict_words = []
        self.dict_words_length = []
        self.adding_horizontal_letters = {}
        self.adding_vertical_letters = {}
        self.fail_ways = []
        self.current_way = []
        self.viewed_horizontal_coordinates = [0]
        self.viewed_vertical_coordinates = [0]
        self.finded_position = [-1]

    def output_crossword(self):
        result = ""
        out_str = ''
        for i in range(len(self.geometry_strs)):
            for j in range(len(self.geometry_strs[i])):
                if (j,i) in self.adding_horizontal_letters:
                    out_str += self.adding_horizontal_letters[(j,i)]
                    continue
                if (i,j) in self.adding_vertical_letters:
                    out_str += self.adding_vertical_letters[(i,j)]
                    continue
                out_str += ' '
            result += out_str + "\n"
            out_str = ''
        return result