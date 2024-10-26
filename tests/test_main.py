import pytest
from lark import Lark
from main import parse_config, grammar, CONSTS

@pytest.fixture(autouse=True)
def clear_globals():
    CONSTS.clear()

def test_array():
    content = """
    global array = #( 10 10 10 )
    """
    config_parser = Lark(grammar)
    result = parse_config(config_parser, content)
    assert result == {'array': [10.0, 10.0, 10.0]}

def test_dict():
    content = """
    global dict = begin a:=10; b:=10 end
    """
    config_parser = Lark(grammar)
    result = parse_config(config_parser, content)
    assert result == {'dict': {'a': 10.0, 'b': 10.0}}

def test_dict_of_dicts():
    content = """
    global dict = begin a:= begin b:=10 end
    end
    """
    config_parser = Lark(grammar)
    result = parse_config(config_parser, content)
    assert result == {'dict': {'a': {'b': 10.0}}}

def test_array_of_arrays():
    content = """
    global array = #( 10 #( 10 10 ))
    """
    config_parser = Lark(grammar)
    result = parse_config(config_parser, content)
    assert result == {'array': [10.0, [10.0, 10.0]]}

def test_array_of_dicts():
    content = """
    global array = #(begin a:=10 end begin b:=10 end)
    """
    config_parser = Lark(grammar)
    result = parse_config(config_parser, content)
    assert result == {'array': [{'a': 10.0}, {'b': 10.0}]}

def test_dict_of_arrays():
    content = """
    global dict = begin a:=#(10 10) end
    """
    config_parser = Lark(grammar)
    result = parse_config(config_parser, content)
    assert result == {'dict': {'a': [10.0, 10.0]}}

def test_dict_of_calculations():
    content = """
    global x = 16
    global y = 4
    global dict = begin
        sum:=@[+ x y];
        sub:=@[- x y];
        mul:=@[* x y];
        div:=@[/ x y];
        sqrt:=@[sqrt() x];
        pow:=@[pow() x y]
    end
    """
    config_parser = Lark(grammar)
    result = parse_config(config_parser, content)
    assert result == {'dict': {'div': 4.0, 'mul': 64, 'pow': 65536, 'sqrt': 4.0, 'sub': 12, 'sum': 20}, 'x': 16.0, 'y': 4.0}

def test_error_KeyError():
    try:
        content = """
            global x = ghjg
            """
        config_parser = Lark(grammar)
        parse_config(config_parser, content)
    except Exception as err:
        assert str(err) == """Ошибка при обработке:\nError trying to process rule "clone_value":\n\nНеизвестное значение - 'ghjg'"""

def test_error_TypeError():
    try:
        content = """
            global array = #( 10 )
            global x = @[sqrt() array]
            """
        config_parser = Lark(grammar)
        parse_config(config_parser, content)
    except Exception as err:
        assert str(err) == """Ошибка при обработке:\nError trying to process rule "clone_value_digit":\n\nНевозможно использовать массив или словарь для вычислений  - int() argument must be a string, a bytes-like object or a real number, not 'list'"""

def test_error_UnexpectedCharacter():
    try:
        content = """
            global x 10
            """
        config_parser = Lark(grammar)
        parse_config(config_parser, content)
    except Exception as err:
        print(str(err))
        assert str(err) == """Неожиданный символ: 
No terminal matches '1' in the current parser context, at line 2 col 22

            global x 10
                     ^
Expected one of: 
	* EQUAL\n"""