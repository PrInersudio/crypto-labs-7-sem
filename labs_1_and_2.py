from typing_extensions import Literal
from typing import List
from math import log2, ceil

def pad_with_symbol(plain_text, block_len, symbol):
    '''
        Осуществляет паддинг выбранным символом.
        Если длина текста кратна длине блока, то добавляет блок из символов.
    '''
    if isinstance(plain_text, bytes): pad = b''
    elif isinstance(plain_text, str): pad = ''
    else: raise TypeError("Соррян, хз чё за тип")
    pad = pad.join([symbol for _ in range(block_len - len(plain_text) % block_len)])
    return plain_text + pad

def evaluate_boolean_function(states: List[Literal[0,1]], func: str) -> Literal[0,1]:
    '''
        Принимает список состояний [x_0, x_1, x_2, ...] и булеву функцию (например 'x_0^x_3&x_10')
        Вычисляет значение булевой функции согласно состояниям.
    '''
    variables = {f'x_{i}': states[i] for i in range(len(states))}
    for variable, value in variables.items():
        func = func.replace(variable, str(value))
    return eval(func)

def hex_to_binary(hex_string: str) -> str:
    binary_string = bin(int(hex_string, 16))[2:]
    num_bits = len(binary_string)
    padding = (num_bits % 8)
    if padding != 0:
        binary_string = binary_string.zfill(num_bits + (8 - padding))
    return binary_string

class LFSR:
    '''
        Реализация РСОЛС.
        При инициализации принимает начальное заполнение регистра
        и многочлен, по которому генерируется новое.
        Также можно задать фильтрующую функцию.
    '''
    def __init__(self, init_state: List[Literal[0,1]], poly: List[int], filter_func: str = ''):
        self.__state = init_state
        self.__poly = poly
        self.__filter_func = filter_func

    def step(self, cascade_bit: Literal[0,1] = 0) -> Literal[0,1]:
        '''
            Делает шаг РСОЛС.
            !!! ВАЖНО: Обратите внимание, что в этой реализации регистры вращаются
            слева-направо!!! (А то на некоторых схемах в Notion,
            они вращаются справа-налево, что тоже допустимо)
            Возвращает выкинутый бит, если фильтрующая функция не задана,
            иначе возвращает значение фильтрующей функции.
            В качестве параметра может принять бит, который будет проксорин
            с новым битом, перед его добавлением в состояние
            (поможет в реализации каскадного генератора)
        '''
        new_bit = 0
        for monome in self.__poly: new_bit ^= self.__state[monome]
        new_bit ^= cascade_bit
        if self.__filter_func == '': throwed_bit = self.__state[-1]
        else: throwed_bit = evaluate_boolean_function(self.__state, self.__filter_func)
        print(self.__state, '=>', throwed_bit)
        self.__state = [new_bit] + self.__state[:-1]
        return throwed_bit


class lab1:

    def task2(key: List[int], plain_text: str) -> str:
        '''
            Реализация шифрования методом перестановок в колонках
        '''
        key = [num - 1 for num in key]
        padded_plain_text = pad_with_symbol(plain_text.upper(), len(key), '_')
        plain_table = [list(padded_plain_text[i : i + len(key)]) for i in range(0,len(padded_plain_text),len(key))]
        print(plain_table)
        cipher_table = []
        for plain_line in plain_table:
            cipher_line = [plain_line[i] for i in key]
            cipher_table.append(cipher_line)
        print(cipher_table)
        cipher_text = ''
        for line in cipher_table: cipher_text += ''.join(line)
        print(cipher_text)
        return cipher_text
    
    def __shrinking_generator(clock_lfsr: LFSR, gamma_lfsr: LFSR, gamma_size: int, clock_rule: Literal[0,1] = 1) -> List[Literal[0,1]]:
        '''
            Реализация сжимающего генератора.
            Принимает два РСОЛС:
                Первый используется как часы
                Второй непосредсвенно генерирует гамму
            Третий аргумент - количество бит гаммы, которое надо сгенерировать.
            Четвёртый - правило, по которому бит, сгенерированный вторым РСОЛС принимается.
            Если 1, то когда часы выдают 1, если 0, то когда часы выдают 0.
            Возвращает список битов гаммы длинной gamma_size
        '''
        gamma = []
        i = 1
        while len(gamma) != gamma_size:
            print(i)
            i+=1
            clock_bit = clock_lfsr.step()
            gamma_bit = gamma_lfsr.step()
            if clock_bit == clock_rule: gamma.append(gamma_bit)
        return gamma
    
    def __cascade_generator(lfsrs: List[LFSR], gamma_size: int) -> List[Literal[0,1]]:
        '''
            Реализация каскадного генератора.
            Примает список РЛОСЛов и количество бит гаммы, которое надо сгененировать.
            Возвращает список битов гаммы длинной gamma_size
        '''
        gamma = []
        for i in range(gamma_size):
            print(i+1)
            lfsr_output = 0
            for lfsr in lfsrs:
                lfsr_output = lfsr.step(lfsr_output)
            gamma.append(lfsr_output)
        return gamma
    
    def __combining_generator(lfsrs: List[LFSR], filter: str, gamma_size: int) -> List[Literal[0,1]]:
        '''
            Реализация комбинирующего генератора (Варианта с ним нет, но пусть будет на всякий).
            Примает список РЛОСЛов и количество бит гаммы, которое надо сгененировать.
            Возвращает список битов гаммы длинной gamma_size.
            Реализация огонь!!! Ничего не понятно, но очень интересно.
        '''
        return [evaluate_boolean_function([lfsr.step() for lfsr in lfsrs], filter) for _ in range(gamma_size)]
    
    def task3(lfsrs: List[LFSR], gamma_size: int, idle_num: int = 0, mode: Literal['shrinking', 'cascade', 'combining', ''] = '') -> List[Literal[0,1]]:
        '''
            Вращает регистры всякие по-всякому.
            В вариантах с фильтром просто задавайте фильтр при инициализации РСОЛС,
            а mode не задавайте.
            В вариантах с комбинированным генератором, я так понял, либо реализуется схема каскадного
            генератора, где выход фильтра кидается в следующий регистр, либо сжимающего, где выход
            фильтра это часы. (Комбинированный явно != комбинирующий, так как в комбинирующем
            размерность фильтра должна совпадать с количеством РСОЛС)
            !!! ВАЖНО: Обратите внимание, что в этой реализации регистры вращаются
            слева-направо!!! (А то на некоторых схемах в Notion,
            они вращаются справа-налево, что тоже допустимо)
        '''
        if (idle_num != 0): print('Холостые ходы:')
        for i in range(idle_num):
            print(i+1)
            for lfsr in lfsrs: lfsr.step()
        if mode == '':
            gamma = [lfsrs[0].step() for _ in range(gamma_size)]
        elif mode == 'shrinking':
            assert len(lfsrs) == 2
            gamma = lab1.__shrinking_generator(lfsrs[0], lfsrs[1], gamma_size)
        elif mode == 'cascade':
            gamma = lab1.__cascade_generator(lfsrs, gamma_size)
        elif mode == 'combining':
            gamma = lab1.__combining_generator(lfsrs, gamma_size)
        else:
            raise ValueError("А как вообще это сюда попало?")
        print(gamma)
        return gamma
    

class lab2:

    def task1(input_vector: str, p_box: List[int]) -> str:
        binary = hex_to_binary(input_vector)
        print(binary)
        permutated = [binary[i] for i in p_box]
        print(permutated)
        output_vector = hex(int(''.join(permutated), 2)).upper()
        print(output_vector)
        return output_vector
    
    def task2(input_vector: str, s_box: List[int]) -> str:
        input_binary = hex_to_binary(input_vector)
        print(input_binary)
        s_box_input_dim = int(log2(len(s_box)))
        print('Входная размерность s-box', s_box_input_dim)
        s_box_output_dim = ceil(log2(max(s_box)))
        print('Выходная размерность s-box', s_box_output_dim)
        padding = len(input_binary) % s_box_input_dim
        if padding != 0: input_binary = input_binary.zfill(len(input_binary) + (s_box_input_dim - padding))
        original_sequence = [input_binary[i:i+s_box_input_dim] for i in range(0, len(input_binary), s_box_input_dim)]
        print(original_sequence)
        original_sequence = [int(num, 2) for num in original_sequence]
        print(original_sequence)
        output_sequence = [s_box[num] for num in original_sequence]
        print(output_sequence)
        output_sequence = [bin(num)[2:].zfill(s_box_output_dim) for num in output_sequence]
        print(output_sequence)
        output_binary = ''.join(output_sequence)
        print(output_binary)
        output_vector = hex(int(output_binary, 2)).upper()
        print(output_vector)
        return output_vector


def do_all_tasks():
    lab1.task2([2,5,7,1,4,3,6], 'Криптография')
    print()
    lab1.task3([LFSR([0,1,0,0], [3,0]), LFSR([1,0,1,0,1,1], [5,2,0])], 4, mode='shrinking')
    print()
    lab1.task3([LFSR([0,0,1,0,1], [1,3,4], 'x_2&x_3^x_4')], 5)
    print()
    lab1.task3([LFSR([0,0,1,0,1], [1,3,4]), LFSR([0,0,1,0,1], [1,3,4])], 4, mode='cascade')
    print()
    lab2.task1('A79F15C4', [15,7,8,0,9,4,3,11,12,10,1,13,5,6,14,2])
    print()
    lab2.task2('F1542A33', [0,2,7,1,3,4,5,7,1,2,3,4,0,6,5,6])


if __name__ == '__main__':
    do_all_tasks()