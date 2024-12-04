# def create_dictionary(n1, n2, s1, s2):
#     if type(n1) == type(n2) and type(s1) == type(s2) and (type(n1) == type(1.0) or type(n1) == type(1)) and type(s1) == type('str'):
#         dictionary = {s1: n1, s2: n2}
#         return dictionary

# dictionary = create_dictionary(50, 100, 'Первое число', 'Второе число')

# print(dictionary)


# def number_of_letters(s):
#     if type(s) == type('str'):
#         count = 0
#         for i in s:
#             if  "a" == i or "i" == i:
#                 count += 1
#         return count

# count = number_of_letters(input("Введите строку содержащую буквы английского алфавита 'a' и 'i', а я их посчитаю: "))

# print("кол-во букв 'a' и 'i':", count)



x = int(input("какой длины вы хотите словарь: "))
d = {}
for i in range(x):
    key = input("Введите ключ: ")
    value = int(input(f"Введите значение ключа '{key}': "))
    d[key] = value

def positive_count(input_dict):
    count = 0
    for value in input_dict.values():
        if value > 0:
            count += 1
    return count

count = positive_count(d)
print("Количество положительных значений:", count)
print("Словарь:", d)
print("Значения в формате int:", list(d.values()))
