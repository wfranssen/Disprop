#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2020 Wouter Franssen

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

def makeGrkList(alpha,eps,eta,iota,omi,rho,up,ohm):
    """
    A function to create a list of 25 None characters, with input for
    only the chars that can have diacritics in Greek.
    """
    lst = [None] * 25
    lst[0] = alpha
    lst[4] = eps
    lst[6] = eta
    lst[8] = iota
    lst[14] = omi
    lst[16] = rho
    lst[20] = up
    lst[24] = ohm
    return lst 	 		

# Make a dictionary with all possible Greek characters with diacritics.
# Every combination of diacritics is a separate entry.
# lower and upper case are with 'l' or 'u' index.
# Each list is 25 positions, with None used to signal that this character
# does not exist in unicode. We are very flexible in this way, and extra
# modifiers can be easily included. Coding is following:
# acute, tonos, grave, circum, smooth, rough, dia, macron, breve, iota
# ['A','T','G','C','S','R','D','M','B','I']
greekDiaDict = dict()
greekDiaDict['l'] = ['α','β','γ','δ','ε','ζ','η','θ','ι','κ','λ','μ','ν','ξ','ο','π','ρ','σ','ς','τ','υ','φ','χ','ψ','ω']
greekDiaDict['u'] = ['Α','Β','Γ','Δ','Ε','Ζ','Η','Θ','Ι','Κ','Λ','Μ','Ν','Ξ','Ο','Π','Ρ','Σ','Σ','Τ','Υ','Φ','Χ','Ψ','Ω']
greekDiaDict['lA'] = makeGrkList('ά','έ','ή','ί','ό',None,'ύ','ώ')
greekDiaDict['uA'] = makeGrkList('Ά','Έ','Ή','Ί','Ό',None,'Ύ','Ώ')
greekDiaDict['lT'] = makeGrkList('ά','έ','ή','ί','ό',None,'ύ','ώ')
greekDiaDict['uT'] = makeGrkList('Ά','Έ','Ή','Ί','Ό',None,'Ύ','Ώ')
greekDiaDict['lG'] = makeGrkList('ὰ','ὲ','ὴ','ὶ','ὸ',None,'ὺ','ὼ')
greekDiaDict['uG'] = makeGrkList('Ὰ','Ὲ','Ὴ','Ὶ','Ὸ',None,'Ὺ','Ὼ')
greekDiaDict['lC'] = makeGrkList('ᾶ',None,'ῆ','ῖ',None,None,'ῦ','ῶ')
#uC does not exist
greekDiaDict['lS'] = makeGrkList('ἀ','ἐ','ἠ','ἰ','ὀ','ῤ','ὐ','ὠ')
greekDiaDict['uS'] = makeGrkList('Ἀ','Ἐ','Ἠ','Ἰ','Ὀ',None,None,'Ὠ')
greekDiaDict['lR'] = makeGrkList('ἁ','ἑ','ἡ','ἱ','ὁ','ῥ','ὑ','ὡ')
greekDiaDict['uR'] = makeGrkList('Ἁ','Ἑ','Ἡ','Ἱ','Ὁ','Ῥ','Ὑ','Ὡ')
greekDiaDict['lD'] = makeGrkList(None,None,None,'ϊ',None,None,'ϋ',None)
greekDiaDict['uD'] = makeGrkList(None,None,None,'Ϊ',None,None,'Ϋ',None)
greekDiaDict['lM'] = makeGrkList('ᾱ',None,None,'ῑ',None,None,'ῡ',None)
greekDiaDict['uM'] = makeGrkList('Ᾱ',None,None,'Ῑ',None,None,'Ῡ',None)
greekDiaDict['lB'] = makeGrkList('ᾰ',None,None,'ῐ',None,None,'ῠ',None)
greekDiaDict['uB'] = makeGrkList('Ᾰ',None,None,'Ῐ',None,None,'Ῠ',None)
greekDiaDict['lI'] = makeGrkList('ᾳ',None,'ῃ',None,None,None,None,'ῳ')
greekDiaDict['uI'] = makeGrkList('ᾼ',None,'ῌ',None,None,None,None,'ῼ')
greekDiaDict['lAS'] = makeGrkList('ἄ','ἔ','ἤ','ἴ','ὄ',None,'ὔ','ὤ')
greekDiaDict['uAS'] = makeGrkList('Ἄ','Ἔ','Ἤ','Ἴ','Ὄ',None,None,'Ὤ')
greekDiaDict['lGS'] = makeGrkList('ἂ','ἒ','ἢ','ἲ','ὂ',None,'ὒ','ὢ')
greekDiaDict['uGS'] = makeGrkList('Ἂ','Ἒ','Ἢ','Ἲ','Ὂ',None,None,'Ὢ')
greekDiaDict['lCS'] = makeGrkList('ἆ',None,'ἦ','ἶ',None,None,'ὖ','ὦ')
greekDiaDict['uCS'] = makeGrkList('Ἆ',None,'Ἦ','Ἶ',None,None,None,'Ὦ')
greekDiaDict['lAR'] = makeGrkList('ἅ','ἕ','ἥ','ἵ','ὅ',None,'ὕ','ὥ')
greekDiaDict['uAR'] = makeGrkList('Ἅ','Ἕ','Ἥ','Ἵ','Ὅ',None,'Ὕ','Ὥ')
greekDiaDict['lGR'] = makeGrkList('ἂ','ἒ','ἢ','ἲ','ὂ',None,'ὒ','ὢ')
greekDiaDict['uGR'] = makeGrkList('Ἃ','Ἓ','Ἣ','Ἳ','Ὃ',None,'Ὓ','Ὣ')
greekDiaDict['lCR'] = makeGrkList('ἆ',None,'ἦ','ἶ',None,None,'ὗ','ὦ')
greekDiaDict['uCR'] = makeGrkList('Ἇ',None,'Ἧ','Ἷ',None,None,'Ὗ','Ὧ')
greekDiaDict['lAD'] = makeGrkList(None,None,None,'ΐ',None,None,'ΰ',None)
greekDiaDict['lGD'] = makeGrkList(None,None,None,'ῒ',None,None,'ῢ',None)
greekDiaDict['lCD'] = makeGrkList(None,None,None,'ῗ',None,None,'ῧ',None)
greekDiaDict['lTD'] = makeGrkList(None,None,None,'ΐ',None,None,'ΰ',None)
# In capital, no diaeresis combo's with other modifiers
greekDiaDict['lAI'] = makeGrkList('ᾴ',None,'ῄ',None,None,None,None,'ῴ')
# No uAI, uGi and uCI
greekDiaDict['lGI'] = makeGrkList('ᾲ',None,'ῂ',None,None,None,None,'ῲ')
greekDiaDict['lCI'] = makeGrkList('ᾷ',None,'ῇ',None,None,None,None,'ῷ')
greekDiaDict['lSI'] = makeGrkList('ᾀ',None,'ᾐ',None,None,None,None,'ᾠ')
greekDiaDict['uSI'] = makeGrkList('ᾈ',None,'ᾘ',None,None,None,None,'ᾨ')
greekDiaDict['lRI'] = makeGrkList('ᾁ',None,'ᾑ',None,None,None,None,'ᾡ')
greekDiaDict['uRI'] = makeGrkList('ᾉ',None,'ᾙ',None,None,None,None,'ᾩ')
greekDiaDict['lASI'] = makeGrkList('ᾄ',None,'ᾔ',None,None,None,None,'ᾤ')
greekDiaDict['uASI'] = makeGrkList('ᾌ',None,'ᾜ',None,None,None,None,'ᾬ')
greekDiaDict['lGSI'] = makeGrkList('ᾂ',None,'ᾒ',None,None,None,None,'ᾢ')
greekDiaDict['uGSI'] = makeGrkList('ᾊ',None,'ᾚ',None,None,None,None,'ᾪ')
greekDiaDict['lCSI'] = makeGrkList('ᾆ',None,'ᾖ',None,None,None,None,'ᾦ')
greekDiaDict['uCSI'] = makeGrkList('ᾎ',None,'ᾞ',None,None,None,None,'ᾮ')
greekDiaDict['lARI'] = makeGrkList('ᾅ',None,'ᾕ',None,None,None,None,'ᾥ')
greekDiaDict['uARI'] = makeGrkList('ᾍ',None,'ᾝ',None,None,None,None,'ᾭ')
greekDiaDict['lGRI'] = makeGrkList('ᾃ',None,'ᾓ',None,None,None,None,'ᾣ')
greekDiaDict['uGRI'] = makeGrkList('ᾋ',None,'ᾛ',None,None,None,None,'ᾫ')
greekDiaDict['lCRI'] = makeGrkList('ᾇ',None,'ᾗ',None,None,None,None,'ᾧ')
greekDiaDict['uCRI'] = makeGrkList('ᾏ',None,'ᾟ',None,None,None,None,'ᾯ')

specialChars = [['Ϗ','Ϛ','Ϝ','Ϟ','Ϡ','Ȣ'],
                ['ϗ','ϛ','ϝ','ϟ','ϡ','ȣ','᾽','·',';']]

#========Transliteration=========
# A list to replace Greek characters by the character without diacritics. Rough breathing is retained.
GREEK_REMOVE_DIA = [['άἀἂἄἆὰάᾀᾂᾄᾆᾰᾱᾲᾳᾴᾶᾷ','α'],['ἁἃἅἇᾁᾃᾅᾇ','ἁ'],['ΆἈἊἌἎᾈᾊᾌᾎᾸᾹᾺΆᾼ','Α'],['ἉἋἍἏᾉᾋᾍᾏ','Ἁ'],
        ['έἐἒἔὲέ','ε'],['ἑἓἕ','ἑ'],['ΈἘἚἜῈΈ','Ε'],['ἙἛἝ','Ἑ'],['ήἠἢἤἦὴήᾐᾒᾔᾖῂῃῄῆῇ','η'],['ἡἣἥἧᾑᾓᾕᾗ','ἡ'],
        ['ΉἨἪἬἮᾘᾚᾜᾞῊΉῌ','Η'],['ἩἫἭἯᾙᾛᾝᾟ','Ἡ'],['ϊίΐἰἲἴἶὶίῐῑῒΐῖῗ','ι'],['ἱἳἵἷ','ἱ'],['ΪΊἸἺἼἾῘῙῚΊ','Ι'],
        ['ἹἻἽἿ','Ἱ'],['όὀὂὄὸό','ο'],['ὁὃὅ','ὁ'],['ΌὈὊὌῸΌ','Ο'],['ὉὋὍ','Ὁ'],['ύϋΰὐὒὔὖὺύῠῡῢΰῦῧ','υ'],
        ['ὑὓὕὗ','ὑ'],['ΫΎῨῩῪΎ','Υ'],['ὙὛὝὟ','Ὑ'],['ώὠὢὤὦὼώᾠᾢᾤᾦῲῳῴῶῷ','ω'],['ὡὣὥὧᾡᾣᾥᾧ','ὡ'],
        ['ΏὨὪὬὮᾨᾪᾬᾮῺΏῼ','Ω'],['ὩὫὭὯᾩᾫᾭᾯ','Ὡ'],['ῤ','ρ'],['ῥ','ῥ'],['Ῥ','Ῥ']]

# A list to replace Greek characters by their latin transliteration.
GREEK_TRANSLITERATE = [['γγ','ng'],['γκ','nk'],['γξ','nx'],['γχ','nch'],['ρρ','rrh'],['α','a'],['ἁ','ha'],
        ['Α','A'],['Ἁ','Ha'],['β','b'],['Β','B'],['γ','g'],['Γ','G'],['δ','d'],['Δ','D'],['ε','e'],
        ['ἑ','he'],['Ε','E'],['Ἑ','He'],['ζ','z'],['Ζ','Z'],['η','ê'],['ἡ','hê'],['Η','Ê'],['Ἡ','Hê'],
        ['θ','th'],['ϑ','th'],['Θ','Th'],['ι','i'],['ἱ','hi'],['Ι','I'],['Ἱ','Hi'],['κ','k'],['Κ','K'],
        ['λ','l'],['Λ','L'],['μ','m'],['Μ','M'],['ν','n'],['Ν','N'],['ξ','x'],['Ξ','X'],['ο','o'],
        ['ὁ','ho'],['Ο','O'],['Ὁ','Ho'],['π','p'],['Π','P'],['ρ','r'],['ῥ','rh'],['Ρ','R'],['Ῥ','Rh'],
        ['ς','s'],['σ','s'],['Σ','S'],['τ','t'],['Τ','T'],['υ','u'],['ὑ','hu'],['Υ','U'],['Ὑ','Hu'],
        ['φ','ph'],['Φ','Ph'],['χ','ch'],['Χ','Ch'],['ψ','ps'],['Ψ','Ps'],['ω','ô'],['ὡ','hô'],
        ['Ω','Ô'],['Ὡ','Hô'],['΄','',],['͵',''],['᾽',''],['᾿','']]

#Diathongs (not sure if these are all used)
#In principle, a diaeresis will cause two vowels to not be a diathong.
#For us, this would only matter if the second vowel also has rough breathing. Not sure
#if this happens...

#Diathongs = [['αἱ','hai'],
#['εἱ','hei'],
#['οἱ','hoi'],
#['υἱ','hyi'],
#['αὑ','hau'],
#['οὑ','hou'],
#['εὑ','heu'],
#['ηὑ','hêu'],
#['ωὑ','hôu']]


