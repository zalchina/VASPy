# -*- coding:utf-8 -*-
#functions used in atomco


def str2list(rawstr):
    import string
    rawlist = rawstr.strip(string.whitespace).split(' ')
    #remove space elements in list
    cleanlist = [x for x in rawlist if x != ' ' and x != '']
    return cleanlist


def array2str(raw_array):
    """
    convert 2d array -> string
    """
    array_str = ''
    for array_1d in raw_array:
        array_str += '(%-20.16f, %-20.16f, %-20.16f)\n' % (tuple(array_1d))

    return array_str


def combine_atomco_dict(dict_1, dict_2):
    """
    Combine 2 dict of atomco_dict.
    Return a new combined dict.
    >>> a.atomco_dict
    >>> {'C': [['2.01115823704755', '2.33265069974919', '10.54948252493041']],
         'Co': [['0.28355818414485', '2.31976779057375', '2.34330019781397'],
                ['2.76900337448991', '0.88479534087197', '2.34330019781397']]}
    """
    new_atomco_dict = {}
    for atom_type_str in dict_1:
        if atom_type_str in dict_2:
            new_atomco_dict[atom_type_str] = dict_1[atom_type_str] + \
                                             dict_2[atom_type_str]
        else:
            new_atomco_dict[atom_type_str] = dict_1[atom_type_str]
    for atom_type_str in dict_2:
        if atom_type_str in dict_1:
            pass
        else:
            new_atomco_dict[atom_type_str] = dict_2[atom_type_str]

    return new_atomco_dict


def atomdict2str(atomco_dict, keys):
    """
    Convert atomco_dict to content_str.
    from
    {'C' : [['2.01115823704755', '2.33265069974919', '10.54948252493041']],
     'Co': [['0.28355818414485', '2.31976779057375', '2.34330019781397'],
            ['2.76900337448991', '0.88479534087197', '2.34330019781397']]}
    to
    'C   2.01115823704755   2.33265069974919   10.54948252493041\n
     Co  0.28355818414485   2.31976779057375   2.34330019781397 \n
     Co  2.76900337448991   0.88479534087197   2.34330019781397 \n'
    """
    content_str = ''
    for atom in keys:
        n = len(atomco_dict[atom])
        for i in xrange(n):
            line_tuple = tuple([atom] + atomco_dict[atom][i])
            content_str += '%-3s%16s%16s%16s\n' % line_tuple

    return content_str
