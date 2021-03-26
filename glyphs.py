#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2021 Wouter Franssen

# This file is part of Disprop.
#
# Disprop is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Disprop is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Disprop. If not, see <http://www.gnu.org/licenses/>.

copticDict = dict()
copticDict['u'] = 'ⲀⲂⲄⲆⲈⲊⲌⲎⲐⲒⲔⲖⲘⲚⲜⲞⲠⲢⲤⲦⲨⲪⲬⲮⲰ'
copticDict['l'] = 'ⲁⲃⲅⲇⲉⲋⲍⲏⲑⲓⲕⲗⲙⲛⲝⲟⲡⲣⲥⲧⲩⲫⲭⲯⲱ'
copticDict['du'] = 'ϢϤϦϨϪϬϮ'
copticDict['dl'] = 'ϣϥϧϩϫϭϯ'
copticDict['other'] = 'ⳤ⳥⳦⳧⳨⳩⳪⳹⳺⳻⳼⳽⳾⳿'

# Cyrillic
cyrillicDict = dict()
cyrillicDict['u'] = 'АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
cyrillicDict['l'] = 'абвгдежзийклмнопрстуфхцчшщъыьэюя'
cyrillicDict['eu'] = 'ЀЁЂЃЄЅІЇЈЉЊЋЌЍЎЏ'
cyrillicDict['el'] = 'ѐёђѓєѕіїјљњћќѝўџ'


# DP character suites
DPSuitesDict = dict()
DPSuitesDict['Basic Greek'] = 'ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩαβγδεζηθικλμνξοπρςστυφχψω'

DPSuitesDict['Basic Latin'] = ' \n!"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLM'\
               'NOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~¡¢'\
               '£¤¥¦§¨©ª«¬®¯°±²³´µ¶·¸¹º»¼½¾¿ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖ×'\
               'ØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿŒœŠšŽžŸƒ‹›'

DPSuitesDict['Extended European Latin A'] = 'ĂăĈĉĜĝŊŋŜŝŬŭĤĥĴĵŐőŦŧŰűŴŵŶŷȘșȚț'

DPSuitesDict['Extended European Latin B'] = 'ĀāČčĎďĒēĚěĢģĪīĶķĹĺĻļĽľŅņŇňŌōŔŕŖŗŘřŠšŤťŪūŮůŽž'

DPSuitesDict['Extended European Latin C'] = 'ĄąĆćĊċČčĐđĖėĘęĠġĦħĮįŁłŃńŚśŠšŪūŲųŹźŻżŽž'

DPSuitesDict['Medievalist supplement'] = 'ĀāĂăđĒēĔĕĘęħĪīĬĭŌōŎŏŪūŬŭſƀƿǢǣǪǫǷǼǽȜȝȲȳ⁊Ꜵꜵꝑꝓꝕꝝꝥꝫꝭꝰ'

DPSuitesDict['Polytonic Greek'] = 'ʹ͵ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩΪΫαβγδεζηθικλμνξοπ'\
                                  'ρςστυφχψωϊϋϛϜϝϲϹΆΈΉΊΌΎΏΐάέήίΰόύώἀἁἂἃἄἅἆἇἈἉἊἋ'\
                                  'ἌἍἎἏἐἑἒἓἔἕἘἙἚἛἜἝἠἡἢἣἤἥἦἧἨἩἪἫἬἭἮἯἰἱἲἳἴἵἶἷἸἹἺἻ'\
                                  'ἼἽἾἿὀὁὂὃὄὅὈὉὊὋὌὍὐὑὒὓὔὕὖὗὙὛὝὟὠὡὢὣὤὥὦὧὨὩὪὫὬὭὮὯ'\
                                  'ὰὲὴὶὸὺὼᾀᾁᾂᾃᾄᾅᾆᾇᾈᾉᾊᾋᾌᾍᾎᾏᾐᾑᾒᾓᾔᾕᾖᾗᾘᾙᾚᾛᾜᾝᾞᾟᾠᾡᾢᾣᾤ'\
                                  'ᾥᾦᾧᾨᾩᾪᾫᾬᾭᾮᾯᾰᾱᾲᾳᾴᾶᾷᾸᾹᾺᾼῂῃῄῆῇῈῊῌῐῑῒῖῗῘῙῚῠῡῢῤῥῦ'\
                                  'ῧῨῩῪῬῲῳῴῶῷῸῺῼ'

# Excludes double symbol characters (i.e. with combining diacritics)
DPSuitesDict['Semitic and Indic transcriptions'] = 'ĀāĒēĪīŌōŚśŠšŪūʾʿḌḍḤḥḪḫḲḳḷḹṀṁṂṃṄṅṆṇṚṛṜṝṢṣṬṭẒẓẔẕẖ'

# Excludes variation selectors
DPSuitesDict['Symbols collection'] = 'ʒ℈℔℞℥☉☊☋☌☍☽☾☿♀♁♂♃♄♅♆♩♪♭♮♯♈♉♊♋♌♍♎♏♐♑♒♓'

