# -*- coding: utf-8 -*-

#Нужно для корректного вывода юникода в результатах выполнения тестов в консоли
def pytest_make_parametrize_id(config, val):
    return repr(val)
