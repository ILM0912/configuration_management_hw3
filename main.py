from math import sqrt
from lark import Lark, Transformer, exceptions
import json

input_file = 'edu_lang.SENYA'
output_file = 'output.json'

grammar = """
start: constants
root_value: array | dict
value:  NUMBER | array | dict | clone_value | calculation

calculation: add | subtract | multiply | divide | power | sqrt
add: "@[" "+" argument argument "]"
subtract: "@[" "-" argument argument "]"
multiply: "@[" "*" argument argument "]"
divide: "@[" "/" argument argument "]"
power: "@[" "pow()" argument argument "]"
sqrt: "@[" "sqrt()" argument "]"

argument: NUMBER | calculation | clone_value_digit
clone_value_digit: NAME
clone_value: NAME
constants: (const_declaration)*
const_declaration: "global" NAME "=" value
array: "#(" value (" " value)* ")"
dict: "begin" [pair (";" pair)*] "end"
pair: NAME ":=" value
NAME: /[a-z]+/
NUMBER: /[0-9]+([.][0-9]+)?/
%import common.WS
%ignore WS
"""

class JSONTransformer(Transformer):
    def start(self, items):
        return items[0] if items else None

    def constants(self, items):
        global CONSTS
        return CONSTS

    def const_declaration(self, items):
        global CONSTS
        CONSTS[items[0]] = items[1]
        return items

    def clone_value(self, item):
        global CONSTS
        try:
            return CONSTS[str(item[0])]
        except KeyError as err:
            raise Exception(f"Неизвестное значение - {str(err)}")

    def clone_value_digit(self, item):
        global CONSTS
        result = CONSTS[str(item[0])]
        try:
            return int(result)
        except TypeError as err:
            raise Exception(f"Невозможно использовать массив или словарь для вычислений  - {str(err)}")

    def calculation(self, result):
        return result[0]

    def argument(self, item):
        return item[0]

    def add(self, item):
        return item[0]+item[1]

    def subtract(self, item):
        return item[0]-item[1]

    def divide(self, item):
        return item[0]/item[1]

    def multiply(self, item):
        return item[0]*item[1]

    def power(self, item):
        return pow(item[0],item[1])

    def sqrt(self, item):
        return sqrt(item[0])

    def value(self, item):
        return item[0]

    def root_value(self, item):
        return item[0]

    def array(self, items):
        return items

    def dict(self, items):
        dict = {}
        for item in items:
            dict[item[0]] = item[1]
        return dict

    def pair(self, items):
        return [items[0],items[1]]

    def NAME(self, item):
        return str(item)

    def NUMBER(self, item):
        return float(item)




def parse_config(input_text):
    try:
        parsed_data = config_parser.parse(input_text)
        transformer = JSONTransformer()
        parsed_data = transformer.transform(parsed_data)
        result = json.dumps(parsed_data, indent=4)
        return result
    except exceptions.UnexpectedCharacters as UnexpectedCharacters:
        raise Exception(f"Неожиданный символ: \n{str(UnexpectedCharacters)}")
    except exceptions.LarkError as LarkError:
        raise Exception(f"Ошибка при обработке:\n{str(LarkError)}")

config_parser = Lark(grammar)
CONSTS = {}
with open(input_file, 'r') as file:
    content = file.read()
result = parse_config(content)
with open(output_file, 'w') as file:
    file.write(result)