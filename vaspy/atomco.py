# -*- coding:utf-8 -*-
"""
===================================================================
Provide coordinate file class which do operations on these files.
===================================================================
Written by PytLab <shaozhengjiang@gmail.com>, November 2014
Updated by PytLab <shaozhengjiang@gmail.com>, August 2015

==============================================================

"""
import numpy as np

from vaspy import VasPy, CarfileValueError
from functions import *


class AtomCo(VasPy):
    "Base class to be inherited by atomco classes."
    def __init__(self, filename):
        VasPy.__init__(self, filename)

    def __repr__(self):
        return self.get_content()

    def __str__(self):
        return self.__repr__()

    def __getattribute__(self, attr):
        '''
        确保atomco_dict能够及时根据data值的变化更新.
        '''
        if attr == 'atomco_dict':
            return self.get_atomco_dict(self.data)
        else:
            return object.__getattribute__(self, attr)

    def verify(self):
        if len(self.data) != self.ntot:
            raise CarfileValueError('Atom numbers mismatch!')

    def get_atomco_dict(self, data):
        "根据已获取的data和atoms, atoms_num, 获取atomco_dict"
        # [1, 1, 1, 16] -> [0, 1, 2, 3, 19]
        idx_list = [sum(self.atoms_num[:i]) for i in xrange(1, len(self.atoms)+1)]
        idx_list = [0] + idx_list
        data_list = data.tolist()
        atomco_dict = {}
        for atom, idx, next_idx in zip(self.atoms, idx_list[:-1], idx_list[1:]):
            atomco_dict.setdefault(atom, data_list[idx: next_idx])

        self.atomco_dict = atomco_dict

        return atomco_dict


class XyzFile(AtomCo):
    """
    Create a .xyz file class.

    Example:

    >>> a = XyzFile(filename='ts.xyz')

    Class attributes descriptions
    =======================================================================
      Attribute      Description
      ============  =======================================================
      filename       string, name of the file the direct coordiante data
                     stored in
      ntot           int, the number of total atom number
      step           int, STEP number in OUT.ANI file
      atoms          list of strings, atom types
      natoms         list of tuples, same shape with atoms.
                     (atom name, atom number)
                     atom number of atoms in atoms
      atomco_dict    dict, {atom name: coordinates}
      data           np.array, coordinates of atoms, dtype=float64
      ============  =======================================================
    """
    def __init__(self, filename):
        AtomCo.__init__(self, filename)
        self.load()
        self.verify()

    # 加载文件内容
    def load(self):
        with open(self.filename, 'r') as f:
            content_list = f.readlines()
        ntot = int(content_list[0].strip())  # total atom number
        step = int(str2list(content_list[1])[-1])  # iter step number

        #get atom coordinate and number info
        data_list = [str2list(line) for line in content_list[2:]]
        data_array = np.array(data_list)  # dtype=np.string
        atoms_list = list(data_array[:, 0])  # 1st column
        data = np.float64(data_array[:, 1:])  # rest columns

        #get atom number for each atom
        atoms = []
        for atom in atoms_list:
            if atom not in atoms:
                atoms.append(atom)
        atoms_num = [atoms_list.count(atom) for atom in atoms]
        natoms = zip(atoms, atoms_num)

        #set class attrs
        self.ntot = ntot
        self.step = step
        self.atoms = atoms
        self.atoms_num = atoms_num
        self.natoms = natoms
        self.data = data

        #get atomco_dict
        self.get_atomco_dict(data)

        return

    def coordinate_transfrom(self, axes=np.array([[1.0, 0.0, 0.0],
                                                  [0.0, 1.0, 0.0],
                                                  [0.0, 0.0, 1.0]])):
        "相对坐标和实坐标转换"
        "Use Ax=b to do coordinate transform. direct to cartesian"
        b = np.matrix(self.data.T)
        A = np.matrix(axes).T
        x = A.I*b

        return np.array(x.T)

    def get_content(self):
        "获取最新文件内容字符串"
        ntot = "%12d\n" % self.ntot
        step = "STEP =%9d\n" % self.step
        data = atomdict2str(self.atomco_dict, self.atoms)
        content = ntot + step + data

        return content

    def tofile(self, filename='atomco.xyz'):
        "XyzFile object to .xyz file."
        content = self.get_content()

        with open(filename, 'w') as f:
            f.write(content)

        return


class PosCar(AtomCo):
    def __init__(self, filename='POSCAR'):
        """
        Class to generate POSCAR or CONTCAR-like objects.

        Example:

        >>> a = PosCar(filename='POSCAR')

        Class attributes descriptions
        =======================================================================
          Attribute      Description
          ============  =======================================================
          filename       string, name of the file the direct coordiante data
                         stored in
          axes_coeff     float, Scale Factor of axes
          axes           np.array, axes of POSCAR
          atoms          list of strings, atom types
          ntot           int, the number of total atom number
          natoms         list of int, same shape with atoms
                         atom number of atoms in atoms
          tf             list of list, T&F info of atoms
          data           np.array, coordinates of atoms, dtype=float64
          ============  =======================================================
        """
        AtomCo.__init__(self, filename)
        #load all data in file
        self.load()
        self.verify()

    def load(self):
        "获取文件数据信息"
        "Load all information in POSCAR."
        with open(self.filename, 'r') as f:
            content_list = f.readlines()
        #get scale factor
        axes_coeff = float(content_list[1])
        #axes
        axes = [str2list(axis) for axis in content_list[2:5]]
        #atom info
        atoms = str2list(content_list[5])
        atoms_num = str2list(content_list[6])  # atom number
        #data
        data, tf = [], []  # data and T or F info
        for line_str in content_list[9:]:
            line_list = str2list(line_str)
            data.append(line_list[:3])
            if len(line_list) > 3:
                tf.append(line_list[3:])
        #data type convertion
        axes = np.float64(np.array(axes))  # to float
        atoms_num = [int(i) for i in atoms_num]
        data = np.float64(np.array(data))

        #set class attrs
        self.axes_coeff = axes_coeff
        self.axes = axes
        self.atoms = atoms
        self.atoms_num = atoms_num
        self.ntot = sum(atoms_num)
        self.natoms = zip(atoms, atoms_num)
        self.data = data
        self.tf = tf

        #get atomco_dict
        self.get_atomco_dict(data)

        return

    def get_content(self):
        "根据对象数据获取文件内容字符串"
        content = 'Created by VASPy\n'
        axe_coeff = " %.9f\n" % self.axes_coeff
        #axes
        axes_list = self.axes.tolist()
        axes = ''
        for axis in axes_list:
            axes += "%14.8f%14.8f%14.8f\n" % tuple(axis)
        #atom info
        atoms, atoms_num = zip(*self.natoms)
        atoms = ("%5s"*len(atoms)+"\n") % atoms
        atoms_num = ("%5d"*len(atoms_num)+"\n") % atoms_num
        #string
        info = "Selective Dynamics\nDirect\n"
        #data and tf
        data_tf = ''
        for data, tf in zip(self.data.tolist(), self.tf):
            data_tf += ("%18.12f"*3+"%5s"*3+"\n") % tuple(data+tf)
        #merge all strings
        content += axe_coeff+axes+atoms+atoms_num+info+data_tf

        return content

    def tofile(self, filename='POSCAR_c'):
        "生成文件"
        "PosCar object to POSCAR or CONTCAR."
        content = self.get_content()

        with open(filename, 'w') as f:
            f.write(content)

        return
