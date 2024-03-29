# -*- coding: utf-8 -*-

import pytest, allure

from get_data import SwineCheck

allure.feature('Поиск лахты')
@pytest.mark.parametrize('swinestring', [
    "хохол",
    "хохлы",
    "тарас",
    "тарабс",
    "пидорашко",
    "пидорашенко",
    "усраина",
    "уссраина",
    "украина",
    "украбинец",
    "протоукры",
    "мивина",
    "гривны",
    "+15 гривен",
    "киберсвиньи",
    "киберсвыня",
    "свиносотня",
    "свинодвоечка",
    "свинявый",
    "свинорез",
    "свидомый",
    "хрю",
    "хрюю", 
    "хррю",
    "хрюкни", 
    "хрюкраина",
    "зрада",
    "зрадный",
    "перемога",
    "переможный",
    "говнопереможные",
    "генотьба",
    "майдан",
    "майдаун",
    "скакол",
    "скакел",
    "поскачи",
    "ципсошник",
    "рагуль",
    "безвизг",
    "пидарешт",
    "мои искандеры",
    "для моих искандеров",
    "дупаболь",
    "мыкола",
    "для мыколы",
    "с міколой", #i из украинской раскладки
    "о мiколе", #i из английской раскладки
    "биндеровец",
    "бандера",
    "оксанки",
    "оксанок",
    "салоед",
    "салочмо",
    "потужный",
    "натодопоможный",
    "нато допоможет"
    ])
def test_swine_regexp(swinestring):
    """Проверка регулярок на детект лахты. 
    Один из основных признаков кремлеботов и промытых ими - использование оскорблений по отношению к украинцам.
    Специфические слова должны быть обнаружены регулярками и пост помещен как лахтинский. 
    Автор не поддерживает использование оскорблений по национальному признаку, в данном коде они используются исключительно для определения постов"""
    swinechecker = SwineCheck(None)
    swines = swinechecker.check_str_for_swines(swinestring)
    assert swines == 1, 'Не найдено свинопостинга там, где они есть!'