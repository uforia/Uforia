# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2005/07/27
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "BSD" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.hardcoded.net/licenses/bsd_license

import re
import struct

from .util import open_if_filename, tryint
from .genres import genre_by_index

HEADER_SIZE = 8

re_atom_type = re.compile(ur'[A-Za-z0-9\-©]{4}')

def read_atom_header(readfunc, offset):
    header = readfunc(offset, HEADER_SIZE)
    if len(header) == HEADER_SIZE:
        size, byte_type = struct.unpack('!i4s', header)
        str_type = unicode(byte_type, u'latin-1')
        return (size, str_type)
    else:
        return ()

def is_valid_atom_type(atom_type):
    return re_atom_type.match(atom_type)
    return True

# Base atom classes *****************************************

class Atom(object):
    cls_data_model = ''

    def __init__(self, parent, start_offset, header=None):
        """parent is anything that has a read method"""
        self.parent = parent
        self.start_offset = start_offset
        self.size = 0
        self.type = ''
        self._valid = False
        self._data = None
        if header is None:
            header = read_atom_header(self.read, -HEADER_SIZE)
        if header:
            self.size, self.type = header
            self._valid = True

    #--- Protected
    def _get_data_model(self):
        return self.cls_data_model

    def _read_atom_data(self):
        dm = '!' + self._get_data_model()
        if '*s' in dm:
            prevsize = struct.calcsize(dm.replace('*s', ''))
            dm = dm.replace('*s', '%ds' % (self.content_size - prevsize), 1).replace('*s', '')
        self._datasize = struct.calcsize(dm)
        data = self.read(0, self._datasize)
        if len(data) < self._datasize:
            data = data.ljust(self._datasize)
        return struct.unpack(dm, data)

    #--- Public
    def read(self, startat=0, readcount= -1):
        if readcount < 0:
            readcount = self.content_size
        return self.parent.read(self.start_offset + HEADER_SIZE + startat, readcount)

    #--- Properties
    @property
    def content_size(self):
        return self.size - HEADER_SIZE

    @property
    def data(self):
        if self._data is None:
            self._data = self._read_atom_data()
        return self._data

    @property
    def valid(self):
        return self._valid


class AtomBox(Atom):
    def __init__(self, parent, start_offset, header=None):
        Atom.__init__(self, parent, start_offset, header)
        self._children = None

    #--- Protected
    def _read_children(self):
        children = []
        self.data  # pre-read data
        # self.data[-1] is the data of the children
        startat = self._datasize
        while startat < self.content_size:
            header = read_atom_header(self.read, startat)
            if not header:
                break
            if header[0] == 0:  # when size is zero, it takes the rest of the atom
                header = (self.content_size - startat, header[1])
            if header[0] < HEADER_SIZE:  # safeguard
                header = (HEADER_SIZE, header[1])
            if is_valid_atom_type(header[1]):
                subatom = self._get_atom_class(header[1])(self, startat, header)
                children.append(subatom)
            startat += header[0]

        return tuple(children)

    def _get_atom_class(self, type):
        return ATOM_SPECS.get(type, Atom)

    #--- Public
    def find(self, atom_type):
        gotta_find = atom_type[:4]
        # You'd think that iterating through atoms is slow and that there should be a {type:atom}
        # mapping, but the tests I've done on real data shows that doing so is in fact slower.
        # I think this is because most atoms have only a few subatoms.
        for atom in self.atoms:
            if atom.type == gotta_find:
                if len(atom_type) >= 9:
                    return atom.find(atom_type[5:])
                else:
                    return atom

    #--- Properties
    @property
    def atoms(self):
        if self._children is None:
            self._children = self._read_children()
        return self._children


#Specific atoms *************************************************************

class AttributeAtom(AtomBox):
    def _get_atom_class(self, type):
        return AttributeDataAtom

    @property
    def attr_data(self):
        try:
            return self.atoms[0].attr_data
        except IndexError:
            # For some reason, our attribute atom has no data sub-atom, no biggie, just return nothing.
            return ''


class AttributeDataAtom(Atom):
    def _get_data_model(self, integer_type='i'):
        [data_type] = struct.unpack('!i', self.read(0, 4))
        return '2i' + (integer_type if data_type == 0 else '*s')

    def _read_atom_data(self):
        result = Atom._read_atom_data(self)
        # Convert to unicode if needed
        if isinstance(result[2], str):
            result = list(result)
            result[2] = result[2].decode(u'utf-8', u'ignore')
            result = tuple(result)
        return result

    @property
    def attr_data(self):
        return self.data[2]


class EsdsAtom(Atom):
    cls_data_model = '26si'

    @property
    def bitrate(self):
        return self.data[1]


class GnreAtom(AttributeAtom):
    def _get_atom_class(self, type):
        return GnreDataAtom


class GnreDataAtom(AttributeDataAtom):
    def _get_data_model(self):
        return AttributeDataAtom._get_data_model(self, 'H')


class MetaAtom(AtomBox):
    cls_data_model = 'i'

class MdhdAtom(Atom):
    def _get_data_model(self):
        [version] = struct.unpack('B', self.read(0, 1))
        return '20s2i' if version > 0 else '12s2i'

    @property
    def sample_rate(self):
        return self.data[1]

    @property
    def duration(self):
        return self.data[2]


class StsdAtom(AtomBox):
    def _get_data_model(self):
        [version] = struct.unpack('4s', self.read(12, 4))
        if version in ('mp4v', 'avc1', 'encv', 's263'):
            return '94s'
        elif version in ('mp4a', 'drms', 'enca', 'samr', 'sawb'):
            return '44s'
        else:
            return '24s'


ATOM_SPECS = {
    u'©nam': AttributeAtom,
    u'©ART': AttributeAtom,
    u'©wrt': AttributeAtom,
    u'©alb': AttributeAtom,
    u'©too': AttributeAtom,
    u'©day': AttributeAtom,
    u'©cmt': AttributeAtom,
    u'©gen': AttributeAtom,
    u'data': AttributeDataAtom,
    u'esds': EsdsAtom,
    u'gnre': GnreAtom,
    u'ilst': AtomBox,
    u'mdhd': MdhdAtom,
    u'mdia': AtomBox,
    u'meta': MetaAtom,
    u'minf': AtomBox,
    u'moov': AtomBox,
    u'stbl': AtomBox,
    u'stsd': StsdAtom,
    u'trak': AtomBox,
    u'trkn': AttributeAtom,
    u'udta': AtomBox,
}

# Mp4 File **********************************************************

class File(AtomBox):
    def __init__(self, infile):
        self._fp, self._shouldclose = open_if_filename(infile, u'rb')
        self._fp.seek(0, 2)
        AtomBox.__init__(self, None, 0, (self._fp.tell(), u'root'))

    def _get_attr(self, path):
        atom = self.find(path)
        return atom.attr_data if atom else ''

    def close(self):
        if self._fp and self._shouldclose:
            self._fp.close()
            self._fp = None

    def read(self, startat=0, readcount= -1):
        if startat < 0:
            startat = 0
        self._fp.seek(startat)
        return self._fp.read(readcount)

    @property
    def album(self):
        return self._get_attr(u'moov.udta.meta.ilst.©alb')

    @property
    def artist(self):
        return self._get_attr(u'moov.udta.meta.ilst.©ART')

    @property
    def audio_offset(self):
        atoms = [a for a in self.atoms if (a.size > 8) and (a.type == u'mdat')]
        return atoms[0].start_offset if atoms else 0

    @property
    def audio_size(self):
        atoms = [a for a in self.atoms if (a.size > 8) and (a.type == u'mdat')]
        return atoms[0].size if atoms else 0

    @property
    def bitrate(self):
        atom = self.find(u'moov.trak.mdia.minf.stbl.stsd.esds')
        return atom.bitrate // 1000 if atom else 0

    @property
    def comment(self):
        return self._get_attr(u'moov.udta.meta.ilst.©cmt')

    @property
    def duration(self):
        atom = self.find(u'moov.trak.mdia.mdhd')
        return atom.duration // self.sample_rate if atom else 0

    @property
    def genre(self):
        data = self._get_attr(u'moov.udta.meta.ilst.gnre')
        if not data:
            data = self._get_attr(u'moov.udta.meta.ilst.©gen')
        if isinstance(data, unicode):
            return data
        elif isinstance(data, int):
            return genre_by_index(data - 1)
        else:
            return u''

    @property
    def sample_rate(self):
        atom = self.find(u'moov.trak.mdia.mdhd')
        return atom.sample_rate if atom else 0

    @property
    def title(self):
        return self._get_attr(u'moov.udta.meta.ilst.©nam')

    @property
    def track(self):
        return tryint(self._get_attr(u'moov.udta.meta.ilst.trkn'))

    @property
    def valid(self):
        return self.find(u'mdat') is not None

    @property
    def year(self):
        return self._get_attr(u'moov.udta.meta.ilst.©day')[:4]
