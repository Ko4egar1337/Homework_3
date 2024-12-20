import argparse
import xml.etree.ElementTree as ET
from xml.etree import ElementTree
import re


def parse_args():
    parser = argparse.ArgumentParser(description="Конвертер из XML в учебны конфигурационный язык")
    parser.add_argument('-i', '--input', required=True, help='Путь к XML файлу')
    parser.add_argument('-o', '--output', required=True, help='Путь к выходному файлу')
    return parser.parse_args()


def convert_xml_to_config(xml_element, constants, indent_num=1):
    indent = "\t" * indent_num

    config = ""
    for item in xml_element:


        if item.tag == ET.Comment:
            comment = item.text.strip()

            #Многострочны комментарий
            if '\n' in comment:
                config += f"{indent}<#\n"
                for line in comment.split('\n'):
                    config += f"{indent}{line.strip()}\n"
                config += f"{indent}#>\n"

            else:
                config += f"{indent}<# {comment} #>\n"

        #Объявления константы
        elif item.tag == 'const':
            #Преобразем имя в нижний регистр
            name = item.get('name').lower()
            value = item.text.strip()

            config += f"{indent}const {name} = {value}\n"
            constants[name] = value

        #Обработка вычисления константы
        elif item.tag == 'eval':
            #Преобразуем имя в нижний регистр
            name = item.text.strip().lower()

            if name not in constants:
                raise ValueError(f"Константа '{name}' не объявлена.")
            config += f"{indent}^{{{name}}}\n"

        #Обработка массивов
        elif item.tag == 'array':
            values = ' '.join(child.text.strip() for child in item)
            config += f"{indent}.({values})\n"

        #Обработка значений чисел и строк
        else:
            #Преобразуем имя в нижний регистр
            name = item.tag.lower()
            value = item.text.strip() if item.text else ""

            #Проверка на число
            if re.match(r'^-?\d+$', value):  # Число
                config += f"{indent}.{name} : {value},\n"
            #Проверка на строку
            elif value.startswith('"') and value.endswith('"'):  # Строка
                config += f"{indent}.{name} : @{value},\n"
            #Рандом значение в формате [[ ]]
            else:
                config += f"{indent}.{name} : [[{value}]],\n"

        #Рекурсивно обрабатываем
        if len(item):
            config += f"{indent}{{\n"
            config += convert_xml_to_config(item, constants, indent_num + 1)
            config += f"{indent}}}\n"

    return config


def main():
    args = parse_args()

    try:
        tree = ET.parse(args.input, parser=ElementTree.XMLParser(target=ElementTree.TreeBuilder(insert_comments=True)))
        root = tree.getroot()

        constants = {}

        config = convert_xml_to_config(root, constants)

        with open(args.output, 'w') as output_file:
            output_file.write(config)

        print(f"Конвертация спешна. Результат записан в {args.output}")
    except ET.ParseError as e:
        print(f"Ошибка при обработке XML: {e}")
    except ValueError as e:
        print(f"Ошибка при конвертаци значений: {e}")
    except Exception as e:
        print(f"Неизвестная ошибка: {e}")


if __name__ == "__main__":
    main()
