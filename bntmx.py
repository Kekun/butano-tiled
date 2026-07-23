"""
Copyright (c) 2023 Adrien Plazas <kekun.plazas@laposte.net>
zlib License, see LICENSE file.
"""

from enum import Enum
from PIL import Image
from tmx import TMX
import argparse
import json
import os
import re
import subprocess
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'modules/butano/butano/tools')))
import file_tools
from bmp import BMP
from butano_graphics_tool import append_compression_command, compression_label, parse_colors_count, remove_file


class Target(Enum):
    butano = 'butano'
    c = 'c'

    def __str__(self):
        return self.value

def read_template(target, template):
    bntmx_dir = os.path.dirname(os.path.realpath(__file__))
    template_filename = os.path.join(bntmx_dir, 'templates', str(target), template)
    template_file = open(template_filename, 'r')
    return template_file.read()

_templates = {
    Target.butano: {
        'affine_bg_item_declaration': read_template(Target.butano, 'affine_bg_item_declaration.h'),
        'affine_bg_map': read_template(Target.butano, 'affine_bg_map.h'),
        'affine_bg_tiles': read_template(Target.butano, 'affine_bg_tiles.h'),
        'bg_palette': read_template(Target.butano, 'bg_palette.h'),
        'bg_palette_item': read_template(Target.butano, 'bg_palette_item.h'),
        'header_template': read_template(Target.butano, 'header_template.h'),
        'indentation': '    ',
        'regular_bg_item_declaration': read_template(Target.butano, 'regular_bg_item_declaration.h'),
        'regular_bg_map': read_template(Target.butano, 'regular_bg_map.h'),
        'regular_bg_tiles': read_template(Target.butano, 'regular_bg_tiles.h'),
        'source_template': read_template(Target.butano, 'source_template.cpp'),
    },
    Target.c: {
        'header_template': read_template(Target.c, 'header_template.h'),
        'indentation': '    ',
        'source_template': read_template(Target.c, 'source_template.c'),
    },
}

def flatten(list_list: list):
    return [element for sublist in list_list for element in sublist]

def write_to_file(filename: str, text: str):
    f = open(filename, "w")
    f.write(text)
    f.close()

def lines(l: list, tail: str) -> str:
    """
    Return a string with a line for each element.

    :param l: the list of the elements
    :returns: a string with a line for each element
    """

    if not l:
        return ''

    return (tail + '\n').join(map(str, l)) + tail

def indent(s: str, indentation: str, depth: int) -> str:
    """
    Return the indented multiline string

    Empty lines are left unindented.

    :param s: the string to indent
    :param indentation: the characters to use for an indentation level
    :param depth: the depth of the indentation
    :returns: the indented multiline string
    """

    line_indentation = indentation * depth

    return '\n'.join(map(lambda line: line_indentation + line if line != '' else '', s.splitlines()))

def inline_c_array(l: list) -> str:
    """
    Return the inline C or C++ literal array or struct for the elements in the list.

    :param l: the list of the array elements
    :returns: the inline array literal
    """

    return '{ ' + ', '.join(map(str, l)) + ' }'

def multiline_c_array(l: list, indentation: str, depth: int) -> str:
    """
    Return the multiline C or C++ literal array or struct for the elements in the list.

    :param l: the list of the array elements
    :param indentation: the characters to use for an indentation level
    :param depth: the depth of the indentation
    :returns: the multiline array literal
    """

    return '{\n' + indent(lines(l, ','), indentation, depth + 1) + '\n' + (indentation * depth) + '}'

def multiline(l: list, indentation: str, depth: int) -> str:
    """
    Return the multiline C or C++ literal array or struct for the elements in the list.

    :param l: the list of the array elements
    :param indentation: the characters to use for an indentation level
    :param depth: the depth of the indentation
    :returns: the multiline array literal
    """

    return '\n'.join(map(lambda s: indent(str(s), indentation, depth), l))

def mangle(name: str) -> str:
    """
    Return the lowercase mangled C or C++ name for the given name.

    Names are mangled in the following way:
    - leading characters that aren't ASCII letters are trimmed
    - trailing characters that aren't ASCII letters or digits are trimmed
    - sequences of characters that aren't ASCII letters or digits are replaced
      by a single underscore character
    - letters are lowercased

    :param name: the name to mangle
    :returns: the lowercase mangled name
    """

    match = re.match('^[0-9_]*([a-z0-9_]+?)_*$', re.sub('[^a-z0-9]+', '_', name.lower()))
    return "" if match is None else match.group(1)

def includes(foreign_includes: set, local_includes: set) -> str:
    return '\n'.join(
        list(map(lambda i: '#include <' + i + '>', sorted(foreign_includes))) +
        list(map(lambda i: '#include "' + i + '"', sorted(local_includes)))
    )

"""
RegularBgItem:

Based on https://github.com/GValiente/butano/blob/21.7.1/butano/tools/butano_graphics_tool.py

Copyright (c) 2020-2026 Gustavo Valiente gustavo.valiente@protonmail.com
zlib License, see LICENSE file.
"""
class RegularBgItem:

    def __init__(self, target: Target, file_path, file_name_no_ext, build_folder_path, info):
        self.__target = target
        bmp = BMP(file_path)
        self.__file_path = file_path
        self.__file_name_no_ext = file_name_no_ext
        self.__build_folder_path = build_folder_path

        width = bmp.width

        if width % 256 != 0:
            raise ValueError('Regular BGs width must be divisible by 256: ' + str(width))

        try:
            height = int(info['height'])

            if bmp.height % height:
                raise ValueError('File height is not divisible by item height: ' +
                                 str(bmp.height) + ' - ' + str(height))

            self.__maps = int(bmp.height / height)
        except KeyError:
            height = bmp.height
            self.__maps = 1

        if height % 256 != 0:
            raise ValueError('Regular BGs height must be divisible by 256: ' + str(height))

        big_dimensions = width > 512 or height > 512

        try:
            self.__big = bool(info['big'])

            if self.__big:
                if width == 256 and height == 256:
                    raise ValueError('Too small size for a big regular BG: ' + str(width) + ' - ' + str(height))

                if width > 16384 or height > 16384:
                    raise ValueError('Too big size for a big regular BG: ' + str(width) + ' - ' + str(height))
            else:
                if big_dimensions:
                    raise ValueError('Too big size for a not big regular BG: ' + str(width) + ' - ' + str(height))
        except KeyError:
            self.__big = big_dimensions

        self.__width = int(width / 8)
        self.__height = int(height / 8)
        self.__bpp_8 = False

        if self.__big:
            self.__sbb = False
        else:
            self.__sbb = width == 512 or height == 512

        try:
            self.__repeated_tiles_reduction = bool(info['repeated_tiles_reduction'])
        except KeyError:
            self.__repeated_tiles_reduction = True

        try:
            self.__flipped_tiles_reduction = bool(info['flipped_tiles_reduction'])
        except KeyError:
            self.__flipped_tiles_reduction = True

        try:
            self.__palette_reduction = bool(info['palette_reduction'])
        except KeyError:
            self.__palette_reduction = True

        try:
            self.__palette_item = str(info['palette_item'])
            validate_palette_item(self.__palette_item)
            self.__colors_count = 0
        except KeyError:
            self.__palette_item = None
            self.__colors_count = parse_colors_count(info, bmp)

        try:
            bpp_mode = str(info['bpp_mode'])

            if bpp_mode == 'bpp_8':
                self.__bpp_8 = True
            elif bpp_mode == 'bpp_4_auto':
                if self.__palette_item is not None:
                    raise ValueError('BPP mode not supported with an external palette item: ' + bpp_mode)

                self.__file_path = self.__build_folder_path + '/' + file_name_no_ext + '.bntmx_quantized.bmp'
                self.__colors_count = bmp.quantize(self.__file_path)
            elif bpp_mode != 'bpp_4' and bpp_mode != 'bpp_4_manual':
                raise ValueError('Invalid BPP mode: ' + bpp_mode)
        except KeyError:
            if self.__palette_item is not None:
                raise ValueError('bpp_mode field not found in graphics json file: ' + file_name_no_ext + '.json')

            if self.__colors_count > 16:
                self.__bpp_8 = True

        try:
            self.__tiles_compression = info['tiles_compression']
            validate_compression(self.__tiles_compression)
        except KeyError:
            try:
                self.__tiles_compression = info['compression']
                validate_compression(self.__tiles_compression)
            except KeyError:
                self.__tiles_compression = 'none'

        if self.__palette_item is not None:
            self.__palette_compression = 'none'
        else:
            try:
                self.__palette_compression = info['palette_compression']
                validate_compression(self.__palette_compression)
            except KeyError:
                try:
                    self.__palette_compression = info['compression']
                    validate_compression(self.__palette_compression)
                except KeyError:
                    self.__palette_compression = 'none'

        try:
            self.__map_compression = info['map_compression']
            validate_compression(self.__map_compression)
        except KeyError:
            try:
                self.__map_compression = info['compression']
                validate_compression(self.__map_compression)
            except KeyError:
                self.__map_compression = 'none'

    def process(self, grit):
        tiles_compression = self.__tiles_compression
        palette_compression = self.__palette_compression
        map_compression = self.__map_compression

        if tiles_compression.startswith('auto'):
            test_huffman = tiles_compression == 'auto'
            tiles_compression, file_size = self.__test_tiles_compression(grit, tiles_compression, 'none', None)
            tiles_compression, file_size = self.__test_tiles_compression(grit, tiles_compression, 'run_length',
                                                                         file_size)
            tiles_compression, file_size = self.__test_tiles_compression(grit, tiles_compression, 'lz77', file_size)

            if test_huffman:
                tiles_compression, file_size = self.__test_tiles_compression(grit, tiles_compression, 'huffman',
                                                                             file_size)

        if palette_compression.startswith('auto'):
            test_huffman = palette_compression == 'auto'
            palette_compression, file_size = self.__test_palette_compression(grit, palette_compression, 'none', None)
            palette_compression, file_size = self.__test_palette_compression(grit, palette_compression, 'run_length',
                                                                             file_size)
            palette_compression, file_size = self.__test_palette_compression(grit, palette_compression, 'lz77',
                                                                             file_size)

            if test_huffman:
                palette_compression, file_size = self.__test_palette_compression(grit, palette_compression, 'huffman',
                                                                                 file_size)

        if map_compression.startswith('auto'):
            test_huffman = map_compression == 'auto'
            map_compression, file_size = self.__test_map_compression(grit, map_compression, 'none', None)
            map_compression, file_size = self.__test_map_compression(grit, map_compression, 'run_length', file_size)
            map_compression, file_size = self.__test_map_compression(grit, map_compression, 'lz77', file_size)

            if test_huffman:
                map_compression, file_size = self.__test_map_compression(grit, map_compression, 'huffman', file_size)

        self.__execute_command(grit, tiles_compression, palette_compression, map_compression)
        return self.__write_header(tiles_compression, palette_compression, map_compression, False)

    def __test_tiles_compression(self, grit, best_tiles_compression, new_tiles_compression, best_file_size):
        self.__execute_command(grit, new_tiles_compression, 'none', 'none')
        new_file_size = self.__write_header(new_tiles_compression, 'none', 'none', True)

        if best_file_size is None or new_file_size < best_file_size:
            return new_tiles_compression, new_file_size

        return best_tiles_compression, best_file_size

    def __test_palette_compression(self, grit, best_palette_compression, new_palette_compression, best_file_size):
        self.__execute_command(grit, 'none', new_palette_compression, 'none')
        new_file_size = self.__write_header('none', new_palette_compression, 'none', True)

        if best_file_size is None or new_file_size < best_file_size:
            return new_palette_compression, new_file_size

        return best_palette_compression, best_file_size

    def __test_map_compression(self, grit, best_map_compression, new_map_compression, best_file_size):
        self.__execute_command(grit, 'none', 'none', new_map_compression)
        new_file_size = self.__write_header('none', 'none', new_map_compression, True)

        if best_file_size is None or new_file_size < best_file_size:
            return new_map_compression, new_file_size

        return best_map_compression, best_file_size

    def __write_header(self, tiles_compression, palette_compression, map_compression, skip_write):
        name = self.__file_name_no_ext
        grit_file_path = self.__build_folder_path + '/' + name + '_bntmx_gfx.h'
        header_file_path = self.__build_folder_path + '/bntmx_regular_bg_items_' + name + '.h'

        with open(grit_file_path, 'r') as grit_file:
            grit_data = file_tools.remove_grit_timestamp(grit_file.read())
            if self.__target == Target.butano:
                grit_data = grit_data.replace('unsigned int', 'bn::tile', 1)
                grit_data = grit_data.replace('unsigned short', 'bn::regular_bg_map_cell', 1)

                if self.__palette_item is None:
                    grit_data = grit_data.replace('unsigned short', 'bn::color', 1)

            for grit_line in grit_data.splitlines():
                if ' tiles ' in grit_line:
                    for grit_word in grit_line.split():
                        try:
                            tiles_count = int(grit_word)
                            break
                        except ValueError:
                            pass

                    if tiles_count > 1024:
                        raise ValueError('Regular BGs with more than 1024 tiles not supported: ' + str(tiles_count))

                if 'Total size:' in grit_line:
                    total_size = int(grit_line.split()[-1])

                    if skip_write:
                        return total_size
                    else:
                        break

        remove_file(grit_file_path)

        if self.__bpp_8:
            bpp_mode_label = 'bpp_mode::BPP_8'
            tiles_count *= 2
        else:
            bpp_mode_label = 'bpp_mode::BPP_4'

        if self.__target == Target.butano:
            grit_data = re.sub(r'Tiles\[([0-9]+)]', 'Tiles[' + str(tiles_count) + ']', grit_data)
            grit_data = re.sub(r'Pal\[([0-9]+)]', 'Pal[' + str(self.__colors_count) + ']', grit_data)

        regular_bg_data = {
            'big': str(self.__big).lower(),
            'bpp_mode_label': 'bn::' + bpp_mode_label,
            'colors_count': str(self.__colors_count),
            'grit_data': grit_data,
            'height': self.__height,
            'map_compression_label': 'bn::' + compression_label(map_compression),
            'maps': str(self.__maps),
            'name': name,
            'palette_compression_label': 'bn::' + compression_label(palette_compression),
            'palette_item': self.__palette_item,
            'tiles_compression_label': 'bn::' + compression_label(tiles_compression),
            'tiles_count': str(tiles_count),
            'total_size': total_size,
            'width': self.__width,
        }

        return regular_bg_data

    def __execute_command(self, grit, tiles_compression, palette_compression, map_compression):
        command = [grit, self.__file_path]

        if self.__colors_count > 0:
            command.append('-pe' + str(self.__colors_count))
        else:
            command.append('-p!')

        map_argument = '-mR'

        if self.__repeated_tiles_reduction:
            map_argument += 't'

        if self.__flipped_tiles_reduction:
            map_argument += 'f'

        if self.__bpp_8:
            command.append('-gB8')
        else:
            command.append('-gB4')

            if self.__palette_reduction:
                map_argument += 'p'

        if map_argument == '-mR':
            map_argument += '!'

        command.append(map_argument)

        if self.__sbb:
            command.append('-mLs')
        else:
            command.append('-mLf')

        append_compression_command('g', tiles_compression, command)
        append_compression_command('p', palette_compression, command)
        append_compression_command('m', map_compression, command)
        command.append('-o' + self.__build_folder_path + '/' + self.__file_name_no_ext + '_bntmx_gfx')
        command = ' '.join(command)

        try:
            subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            raise ValueError(grit + ' call failed (return code ' + str(e.returncode) + '): ' + str(e.output))

"""
AffineBgItem:

Based on https://github.com/GValiente/butano/blob/21.7.1/butano/tools/butano_graphics_tool.py

Copyright (c) 2020-2026 Gustavo Valiente gustavo.valiente@protonmail.com
zlib License, see LICENSE file.
"""
class AffineBgItem:

    def __init__(self, target, file_path, file_name_no_ext, build_folder_path, info):
        self.__target = target
        bmp = BMP(file_path)
        self.__file_path = file_path
        self.__file_name_no_ext = file_name_no_ext
        self.__build_folder_path = build_folder_path

        width = bmp.width

        if width != 128 and width % 256 != 0:
            raise ValueError('Affine BGs width must be 128 or divisible by 256: ' + str(width))

        try:
            height = int(info['height'])

            if bmp.height % height:
                raise ValueError('File height is not divisible by item height: ' +
                                 str(bmp.height) + ' - ' + str(height))

            self.__maps = int(bmp.height / height)
        except KeyError:
            height = bmp.height
            self.__maps = 1

        if height != 128 and height % 256 != 0:
            raise ValueError('Affine BGs height must be 128 or divisible by 256: ' + str(height))

        if width == 128 and height != 128:
            raise ValueError('If the width of an affine BG is 128, its height must be 128: ' +
                             str(width) + ' - ' + str(height))

        if height == 128 and width != 128:
            raise ValueError('If the height of an affine BG is 128, its width must be 128: ' +
                             str(width) + ' - ' + str(height))

        big_dimensions = width != height or (width != 128 and width != 256 and width != 512 and width != 1024)

        try:
            self.__big = bool(info['big'])

            if self.__big:
                if width <= 256 and height <= 256:
                    raise ValueError('Too small size for a big affine BG: ' + str(width) + ' - ' + str(height))

                if width > 16384 or height > 16384:
                    raise ValueError('Too big size for a big affine BG: ' + str(width) + ' - ' + str(height))
            else:
                if big_dimensions:
                    raise ValueError('Too big size for a not big affine BG: ' + str(width) + ' - ' + str(height))
        except KeyError:
            self.__big = big_dimensions

        self.__width = int(width / 8)
        self.__height = int(height / 8)

        try:
            self.__repeated_tiles_reduction = bool(info['repeated_tiles_reduction'])
        except KeyError:
            self.__repeated_tiles_reduction = True

        try:
            self.__palette_item = str(info['palette_item'])
            validate_palette_item(self.__palette_item)
            self.__colors_count = 0
        except KeyError:
            self.__palette_item = None
            self.__colors_count = parse_colors_count(info, bmp)

        try:
            self.__tiles_compression = info['tiles_compression']
            validate_compression(self.__tiles_compression)
        except KeyError:
            try:
                self.__tiles_compression = info['compression']
                validate_compression(self.__tiles_compression)
            except KeyError:
                self.__tiles_compression = 'none'

        if self.__palette_item is not None:
            self.__palette_compression = 'none'
        else:
            try:
                self.__palette_compression = info['palette_compression']
                validate_compression(self.__palette_compression)
            except KeyError:
                try:
                    self.__palette_compression = info['compression']
                    validate_compression(self.__palette_compression)
                except KeyError:
                    self.__palette_compression = 'none'

        try:
            self.__map_compression = info['map_compression']
            validate_compression(self.__map_compression)
        except KeyError:
            try:
                self.__map_compression = info['compression']
                validate_compression(self.__map_compression)
            except KeyError:
                self.__map_compression = 'none'

    def process(self, grit):
        tiles_compression = self.__tiles_compression
        palette_compression = self.__palette_compression
        map_compression = self.__map_compression

        if tiles_compression.startswith('auto'):
            test_huffman = tiles_compression == 'auto'
            tiles_compression, file_size = self.__test_tiles_compression(grit, tiles_compression, 'none', None)
            tiles_compression, file_size = self.__test_tiles_compression(grit, tiles_compression, 'run_length',
                                                                         file_size)
            tiles_compression, file_size = self.__test_tiles_compression(grit, tiles_compression, 'lz77', file_size)

            if test_huffman:
                tiles_compression, file_size = self.__test_tiles_compression(grit, tiles_compression, 'huffman',
                                                                             file_size)

        if palette_compression.startswith('auto'):
            test_huffman = palette_compression == 'auto'
            palette_compression, file_size = self.__test_palette_compression(grit, palette_compression, 'none', None)
            palette_compression, file_size = self.__test_palette_compression(grit, palette_compression, 'run_length',
                                                                             file_size)
            palette_compression, file_size = self.__test_palette_compression(grit, palette_compression, 'lz77',
                                                                             file_size)

            if test_huffman:
                palette_compression, file_size = self.__test_palette_compression(grit, palette_compression, 'huffman',
                                                                                 file_size)

        if map_compression.startswith('auto'):
            test_huffman = map_compression == 'auto'
            map_compression, file_size = self.__test_map_compression(grit, map_compression, 'none', None)
            map_compression, file_size = self.__test_map_compression(grit, map_compression, 'run_length', file_size)
            map_compression, file_size = self.__test_map_compression(grit, map_compression, 'lz77', file_size)

            if test_huffman:
                map_compression, file_size = self.__test_map_compression(grit, map_compression, 'huffman', file_size)

        self.__execute_command(grit, tiles_compression, palette_compression, map_compression)
        return self.__write_header(tiles_compression, palette_compression, map_compression, False)

    def __test_tiles_compression(self, grit, best_tiles_compression, new_tiles_compression, best_file_size):
        self.__execute_command(grit, new_tiles_compression, 'none', 'none')
        new_file_size = self.__write_header(new_tiles_compression, 'none', 'none', True)

        if best_file_size is None or new_file_size < best_file_size:
            return new_tiles_compression, new_file_size

        return best_tiles_compression, best_file_size

    def __test_palette_compression(self, grit, best_palette_compression, new_palette_compression, best_file_size):
        self.__execute_command(grit, 'none', new_palette_compression, 'none')
        new_file_size = self.__write_header('none', new_palette_compression, 'none', True)

        if best_file_size is None or new_file_size < best_file_size:
            return new_palette_compression, new_file_size

        return best_palette_compression, best_file_size

    def __test_map_compression(self, grit, best_map_compression, new_map_compression, best_file_size):
        self.__execute_command(grit, 'none', 'none', new_map_compression)
        new_file_size = self.__write_header('none', 'none', new_map_compression, True)

        if best_file_size is None or new_file_size < best_file_size:
            return new_map_compression, new_file_size

        return best_map_compression, best_file_size

    def __write_header(self, tiles_compression, palette_compression, map_compression, skip_write):
        name = self.__file_name_no_ext
        grit_file_path = self.__build_folder_path + '/' + name + '_bntmx_gfx.h'
        header_file_path = self.__build_folder_path + '/bntmx_affine_bg_items_' + name + '.h'

        with open(grit_file_path, 'r') as grit_file:
            grit_data = file_tools.remove_grit_timestamp(grit_file.read())
            if self.__target == Target.butano:
                grit_data = grit_data.replace('unsigned int', 'bn::tile', 1)
                grit_data = grit_data.replace('unsigned char', 'bn::affine_bg_map_cell', 1)

                if self.__palette_item is None:
                    grit_data = grit_data.replace('unsigned short', 'bn::color', 1)

            for grit_line in grit_data.splitlines():
                if ' tiles ' in grit_line:
                    for grit_word in grit_line.split():
                        try:
                            tiles_count = int(grit_word)
                            break
                        except ValueError:
                            pass

                if 'Total size:' in grit_line:
                    total_size = int(grit_line.split()[-1])

                    if skip_write:
                        return total_size
                    else:
                        break

        remove_file(grit_file_path)

        tiles_count *= 2
        if self.__target == Target.butano:
            grit_data = re.sub(r'Tiles\[([0-9]+)]', 'Tiles[' + str(tiles_count) + ']', grit_data)
            grit_data = re.sub(r'Pal\[([0-9]+)]', 'Pal[' + str(self.__colors_count) + ']', grit_data)

        affine_bg_data = {
            'big': str(self.__big).lower(),
            'colors_count': str(self.__colors_count),
            'grit_data': grit_data,
            'height': self.__height,
            'map_compression_label': 'bn::' + compression_label(map_compression),
            'maps': str(self.__maps),
            'name': name,
            'palette_compression_label': 'bn::' + compression_label(palette_compression),
            'palette_item': self.__palette_item,
            'tiles_compression_label': 'bn::' + compression_label(tiles_compression),
            'tiles_count': str(tiles_count),
            'total_size': total_size,
            'width': self.__width,
        }

        return affine_bg_data

    def __execute_command(self, grit, tiles_compression, palette_compression, map_compression):
        command = [grit, self.__file_path, '-gB8', '-mLa', '-mu8']

        if self.__colors_count > 0:
            command.append('-pe' + str(self.__colors_count))
        else:
            command.append('-p!')

        if self.__repeated_tiles_reduction:
            command.append('-mRt')
        else:
            command.append('-mR!')

        append_compression_command('g', tiles_compression, command)
        append_compression_command('p', palette_compression, command)
        append_compression_command('m', map_compression, command)
        command.append('-o' + self.__build_folder_path + '/' + self.__file_name_no_ext + '_bntmx_gfx')
        command = ' '.join(command)

        try:
            subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            raise ValueError(grit + ' call failed (return code ' + str(e.returncode) + '): ' + str(e.output))

class OrthogonalMapItem:
    def __init__(self, target: Target, tmx: TMX, name: str, info: dict):
        self._templates = {
            'indentation': '    ',
            'map_tiles_data_declaration': read_template(target, 'map_tiles_data_declaration.h'),
            'map_tiles_data_definition': read_template(target, 'map_tiles_data_definition.h'),
            'orthogonal_map_item_declaration': read_template(target, 'orthogonal_map_item_declaration.h'),
            'tile_ids_definition_template': read_template(target, 'tile_ids_definition_template.h'),
            'tiles_getter_template': read_template(target, 'tiles_getter_template.h'),
        }

        match target:
            case Target.butano:
                self._templates['namespace'] = ''
            case Target.c:
                self._templates['namespace'] = 'BNTMX_MAP_ITEMS_' + name.upper() + '_'
            case _:
                raise ValueError('Unknown target: ' + str(target))

        self._target = target
        self._name = name
        self._tmx = tmx
        self._info = info

        self._layers = info['layers'] if 'layers' in info else list()
        self._layers_count = len(self._layers)
        if self._layers_count <= 0:
            raise ValueError('Invalid tile layers count: ' + str(self._layers_count))

        self._width, self._height = self._tmx.dimensions_in_tiles()
        if self._width <= 0:
            raise ValueError('Invalid map width: ' + str(self._width))
        if self._height <= 0:
            raise ValueError('Invalid map height: ' + str(self._height))

        self._tile_width, self._tile_height = self._tmx.tile_dimensions()
        if self._tile_width <= 0:
            raise ValueError('Invalid tile width: ' + str(self._tile_width))
        if self._tile_height <= 0:
            raise ValueError('Invalid tile height: ' + str(self._tile_height))

        self._tiles_count = self._width * self._height * self._layers_count
        self._layers_tiles_count = self._width * self._height

    def _tile_ids_enum(self):
        # Return the list of enumeration definitions for the map tile ids in the whole map

        tile_ids = []
        for first, last, tsx in self._tmx.tilesets():
            enum_base = mangle(os.path.splitext(os.path.basename(tsx.filename()))[0]).upper()
            tile_ids.append(self._templates['namespace'] + enum_base + '=' + str(first))
            tile_ids.append(self._templates['namespace'] + enum_base + '_LAST=' + str(last))
        return tile_ids

    def process(self):
        header_foreign_includes = set()
        header_local_includes = set()
        source_foreign_includes = set()
        source_local_includes = set()

        header_local_includes.add('bntmx.h')
        match self._target:
            case Target.butano:
                header_foreign_includes.add('bn_array.h')
                source_foreign_includes.add('bn_array.h')

        tile_ids = self._tile_ids_enum()
        if len(tile_ids) == 0:
            tile_ids_definition = None
        else:
            tile_ids_literal = multiline_c_array(tile_ids, self._templates['indentation'], 0)
            tile_ids_definition = self._templates['tile_ids_definition_template'].format(map_tiles_item=self, tile_ids=tile_ids_literal)

        # Get a list of C or C++ array row literals for the given list of tiles, matching lines and columns of the map for readability.
        tiles_to_array_row_literals = lambda tiles: [', '.join(tiles[i:i + self._width]) for i in range(0, len(tiles), self._width)]
        # Get a list of C or C++ array row literals for the given tiles layer path, matching lines and columns of the map for readability.
        tiles_layer_path_to_array_row_literals = lambda layer_path: tiles_to_array_row_literals(self._tmx.tiles(layer_path))
        # Literal array of tiles, per tiles layer either nested or flattened.
        tiles_nested_literal = multiline_c_array(map(lambda layer_path: multiline_c_array(tiles_layer_path_to_array_row_literals(layer_path), self._templates['indentation'], 0), self._layers), self._templates['indentation'], 0)
        tiles_flat_literal = multiline_c_array(flatten(map(tiles_layer_path_to_array_row_literals, self._layers)), self._templates['indentation'], 0)

        # Data declarations
        tiles_literal = self._templates['orthogonal_map_item_declaration'].format(map_tiles_item=self)
        tiles_declaration_literal = self._templates['map_tiles_data_declaration'].format(map_tiles_item=self)
        tiles_definition = self._templates['map_tiles_data_definition'].format(
            map_tiles_item=self,
            tiles=tiles_flat_literal)
        tiles_getter = self._templates['tiles_getter_template'].format(map_tiles_item=self)

        return {
            'header_foreign_includes': header_foreign_includes,
            'header_local_includes': header_local_includes,
            'source_foreign_includes': source_foreign_includes,
            'source_local_includes': source_local_includes,
            'data_declarations': [
                tiles_declaration_literal,
            ],
            'item_declarations': [
                tiles_literal,
            ],
            'data_definitions': [
                tiles_definition,
            ],
        }

class MapObjectsItem:
    def __init__(self, target: Target, tmx: TMX, name: str, info: dict):
        self._templates = {
            'indentation': '    ',
            'map_object_template': read_template(target, 'map_object_template.h'),
            'map_objects_class_enum_declaration': read_template(target, 'map_objects_class_enum_declaration.h'),
            'map_objects_class_enum_pair': read_template(target, 'map_objects_class_enum_pair.h'),
            'map_objects_class_names_declaration': read_template(target, 'map_objects_class_names_declaration.h'),
            'map_objects_class_names_pair': read_template(target, 'map_objects_class_names_pair.h'),
            'map_objects_data_declaration': read_template(target, 'map_objects_data_declaration.h'),
            'map_objects_data_definition': read_template(target, 'map_objects_data_definition.h'),
            'map_objects_enum_pair': read_template(target, 'map_objects_enum_pair.h'),
            'map_objects_item_declaration': read_template(target, 'map_objects_item_declaration.h'),
            'map_objects_names_declaration': read_template(target, 'map_objects_names_declaration.h'),
            'map_objects_names_pair': read_template(target, 'map_objects_names_pair.h'),
            'map_objects_slice': read_template(target, 'map_objects_slice.h'),
            'map_objects_slices_data_declaration': read_template(target, 'map_objects_slices_data_declaration.h'),
            'map_objects_slices_data_definition': read_template(target, 'map_objects_slices_data_definition.h'),
            'object_getter': read_template(target, 'object_getter.h'),
            'objects_getter_with_class': read_template(target, 'objects_getter_with_class.h'),
        }

        self._target = target
        self._name = name
        self._tmx = tmx
        self._info = info

        #FIXME

        self._layers = info['layers'] if 'layers' in info else list()

        # The list of MapObjects for the list of object layers
        self._objects_per_layer = list(map(lambda layer_path: self._tmx.objects(layer_path), self._layers))
        # This needs to be called once self._objects_per_layer is set
        self._assign_id_and_layer_to_objects()
        # The list of MapObjects for the whole map
        #
        # This needs to be called after self._assign_id_and_layer_to_objects()
        # as otherwise it wouldn't match self._objects_per_layer anynmore
        self._objects = sorted([map_object for layer_map_objects in self._objects_per_layer for _, info in layer_map_objects.objects().items() for map_object in info], key=lambda o: o.map_id)

        self._class_enum_type = info['class_enum_type'] if 'class_enum_type' in info else None
        match target:
            case Target.butano:
                self._class_enum_prefix = self._class_enum_type + '::' if self._class_enum_type is not None else ''
            case Target.c:
                self._class_enum_prefix = info['class_enum_prefix'] if 'class_enum_prefix' in info else ''
            case _:
                raise ValueError('Unknown target: ' + str(target))

        self._enum_type = info['enum_type'] if 'enum_type' in info else None
        self._enum_prefix = info['enum_prefix'] if 'enum_prefix' in info else ''

        self._layers_count = len(self._layers)

        # -1 because the lack of class isn't a class.
        self._class_count = max(len(self._classes()) - 1, 0)
        self._objects_slices_count = (self._class_count + 1) * self._layers_count
        self._objects_count = len(self._objects)

    def _assign_id_and_layer_to_objects(self):
        objects_classes = self._classes()
        id = 0

        # Layers are already sorted, let's first sort by layers
        for layer_index, layer_map_objects in enumerate(self._objects_per_layer):
            objects = layer_map_objects.objects()

            # Then sort by classes
            for object_class in objects_classes:
                if object_class not in objects:
                    continue

                # Then sort in whatever order the objects come in
                for object in objects[object_class]:
                    object.map_layer = layer_index
                    object.map_id = id
                    id += 1

    def _classes(self):
        # Return the sorted set of map object class names in the whole map, including the "" class
        # If there are no objects layers an empty list is returned, there is not even the "" class.

        return sorted(set([map_object_class for layer_map_objects in self._objects_per_layer for map_object_class in layer_map_objects.objects().keys()]))

    def _spans(self):
        # Return a list for each layer of lists of (index,length) pairs for each
        # object of a given class in the layer, so objects can be flattened but
        # they can still be found per layer and class.

        index_lengths = []
        index = 0
        objects_classes = self._classes()
        for layer in self._objects_per_layer:
            layer_index_lengths = []
            for object_class in objects_classes:
                length = len(layer.objects()[object_class]) if object_class in layer.objects() else 0
                layer_index_lengths.append((index, length))
                index = index + length
            index_lengths.append(layer_index_lengths)
        return index_lengths

    def process(self):
        header_foreign_includes = set()
        header_local_includes = set()
        source_foreign_includes = set()
        source_local_includes = set()

        header_local_includes.add('bntmx.h')
        match self._target:
            case Target.butano:
                header_foreign_includes.add('bn_array.h')
                header_foreign_includes.add('bn_span.h')
                header_foreign_includes.add('bn_string_view.h')
                header_foreign_includes.add('bn_utility.h')
                source_foreign_includes.add('bn_array.h')

        map_objects_classes_labels = list(map(lambda i_and_object_class: self._templates['map_objects_class_names_pair'].format(
            object_class_name=mangle(i_and_object_class[1]),
            object_class_id=str(i_and_object_class[0])), enumerate(self._classes())))[1:]
        map_objects_classes_labels_literal = multiline_c_array(map_objects_classes_labels, self._templates['indentation'], 0)
        map_objects_classes_labels_definition = self._templates['map_objects_class_names_declaration'].format(
            map_objects_item=self,
            map_objects_classes=map_objects_classes_labels_literal)

        if self._class_enum_type is not None:
            object_class_enum = list(map(lambda i_and_object_class: self._templates['map_objects_class_enum_pair'].format(
                map_objects_item=self,
                class_id=str(i_and_object_class[0]),
                class_name=mangle(i_and_object_class[1])), enumerate(self._classes())))[1:]
            map_object_class_enum_literal = multiline_c_array(object_class_enum, self._templates['indentation'], 0)
            map_objects_class_enum_declaration = self._templates['map_objects_class_enum_declaration'].format(
                map_objects_item=self,
                object_class_enum=map_object_class_enum_literal)
        else:
            map_objects_class_enum_declaration = None

        map_objects_data_declaration = self._templates['map_objects_data_declaration'].format(map_objects_item=self)
        map_objects_slices_data_declaration = self._templates['map_objects_slices_data_declaration'].format(map_objects_item=self)
        map_objects_item_declaration = self._templates['map_objects_item_declaration'].format(map_objects_item=self)
        map_objects_getter_with_class = self._templates['objects_getter_with_class']

        object_ids = list(map(lambda map_object: self._templates['map_objects_names_pair'].format(
            object_name=mangle(map_object.id) if map_object.id is not None else '',
            object_id=str(map_object.map_id)), [map_object for map_object in self._objects]))

        object_ids_literal = multiline_c_array(object_ids, self._templates['indentation'], 0)
        object_ids_definition = self._templates['map_objects_names_declaration'].format(
            map_objects_item=self,
            object_ids=object_ids_literal)

        if self._enum_type is not None:
            object_enum = list(map(lambda i_and_object_class: self._templates['map_objects_enum_pair'].format(
                id=str(i_and_object_class[0]),
                enum_prefix=self._enum_prefix,
                name=mangle(i_and_object_class[1])), enumerate(self._objects_classes())))[1:]
            object_enum_literal = multiline_c_array(object_enum, self._templates['indentation'], 0)
            map_objects_enum_declaration = self._templates['map_objects_enum_declaration'].format(
                enum_type=self._enum_type,
                map_objects_item=self,
                object_count=self._objects_count,
                object_enum=object_enum_literal)
        else:
            map_objects_enum_declaration = None

        # Literal array of object spans for each object class, per objects layer either nested or flattened.
        objects_slices_nested_literal = multiline_c_array(map(lambda layer: multiline_c_array(map(lambda span: self._templates['map_objects_slice'].format(index=span[0], length=span[1]), layer), self._templates['indentation'], 0), self._spans()), self._templates['indentation'], 0)
        objects_slices_flat_literal = multiline_c_array(lines(map(lambda layer: lines(map(lambda span: self._templates['map_objects_slice'].format(index=span[0], length=span[1]), layer), ''), self._spans()), '').splitlines(), self._templates['indentation'], 0)
        object_to_cpp_literal = lambda o: self._templates['map_object_template'].format(x=o.x, y=o.y, id=o.map_id)
        objects_literal = multiline_c_array(list(map(object_to_cpp_literal, self._objects)), self._templates['indentation'], 0)

        map_object_getter = self._templates['object_getter']
        map_objects_definition = self._templates['map_objects_data_definition'].format(
            map_objects_item=self,
            objects=objects_literal)
        map_objects_slices_definition = self._templates['map_objects_slices_data_definition'].format(
            map_objects_item=self,
            map_objects_slices=objects_slices_flat_literal)
        map_objects_getter_with_class = self._templates['objects_getter_with_class']

        return {
            'header_foreign_includes': header_foreign_includes,
            'header_local_includes': header_local_includes,
            'source_foreign_includes': source_foreign_includes,
            'source_local_includes': source_local_includes,
            'data_declarations': [
                map_objects_data_declaration,
                map_objects_slices_data_declaration,
            ],
            'item_declarations': [
                map_objects_item_declaration,
                map_objects_classes_labels_definition,
                map_objects_class_enum_declaration,
                map_objects_enum_declaration,
                object_ids_definition,
            ],
            'data_definitions': [
                map_objects_definition,
                map_objects_slices_definition,
            ],
        }

        # FIXME
        # object_getter=map_object_getter,
        # objects_getter_with_class=map_objects_getter_with_class)

class MapItem:
    def __init__(self, target: Target, tmx_filename):
        self._target = target
        self._tmx = TMX(tmx_filename)
        self._basename = os.path.splitext(os.path.basename(tmx_filename))[0]
        self._name = mangle(self._basename)
        self._name_upper = self._name.upper()
        descriptor = open(os.path.splitext(tmx_filename)[0] + ".json")
        descriptor = json.load(descriptor)

        regular_bg = descriptor["regular_bg"] if "regular_bg" in descriptor else dict()
        self._regular_bg_layers = regular_bg["layers"] if "layers" in regular_bg else list()

        affine_bg = descriptor["affine_bg"] if "affine_bg" in descriptor else dict()
        self._affine_bg_layers = affine_bg["layers"] if "layers" in affine_bg else list()

        self._map_tiles_item = OrthogonalMapItem(target, self._tmx, self._name, descriptor['map_tiles']) if 'map_tiles' in descriptor else None

        self._map_objects_item = MapObjectsItem(target, self._tmx, self._name, descriptor['map_objects']) if 'map_objects' in descriptor else None

        self._width_in_pixels, self._height_in_pixels = self._tmx.dimensions_in_pixels()

        self._regular_bg_layers_count = len(self._regular_bg_layers)
        self._affine_bg_layers_count = len(self._affine_bg_layers)

        # Regular background info

        # Copy regular_bg so we don't modify it
        self._regular_bg_info = dict(regular_bg)

        # Remove butano-tiled-specific fields
        if 'layers' in self._regular_bg_info:
            del self._regular_bg_info['layers']

        # Ensure the user didn't set the fields we handle, and set them
        assert 'type' not in regular_bg
        assert 'height' not in regular_bg
        self._regular_bg_info['type'] = 'regular_bg'
        self._regular_bg_info['height'] = self.regular_bg_dimensions()[1]

        # Affine background info

        # Copy affine_bg so we don't modify it
        self._affine_bg_info = dict(affine_bg)

        # Remove butano-tiled-specific fields
        if 'layers' in self._affine_bg_info:
            del self._affine_bg_info['layers']

        # Ensure the user didn't set the fields we handle, and set them
        assert 'type' not in affine_bg
        assert 'height' not in affine_bg
        self._affine_bg_info['type'] = 'affine_bg'
        self._affine_bg_info['height'] = self.affine_bg_dimensions()[1]

    def dependencies(self):
        return self._tmx.dependencies()

    def basename(self):
        # Return the basename of the map

        return self._basename

    def name(self):
        # Return the basename of the map

        return self._name

    def regular_bg_dimensions(self):
        width, height = self._tmx.dimensions_in_pixels()

        bg_width = width if width % 256 == 0 else (width // 256 + 1) * 256
        bg_height = height if height % 256 == 0 else (height // 256 + 1) * 256

        return bg_width, bg_height

    def regular_bg_image(self):
        # Convert the TMX into its regular background image.

        if self._regular_bg_layers_count == 0:
            return None

        # The size of each individual background
        bg_width, bg_height = self.regular_bg_dimensions()

        # Compose the layers into a single background image
        gfx_im = Image.new("RGBA", (bg_width, bg_height * self._regular_bg_layers_count), self._tmx.background_color())
        for i, layer_path in enumerate(self._regular_bg_layers):
            self._tmx.compose(gfx_im, layer_path, 0, bg_height * i)

        # Make the image paletted
        gfx_im = gfx_im.quantize(256)

        return gfx_im

    def small_affine_bg_dimensions(self):
        width, height = self._tmx.dimensions_in_pixels()

        for size in [128, 256, 512, 1024]:
            if width <= size and height <= size:
                return size, size

        return None, None

    def big_affine_bg_dimensions(self):
        width, height = self._tmx.dimensions_in_pixels()

        bg_width = width if width % 256 == 0 else (width // 256 + 1) * 256
        bg_height = height if height % 256 == 0 else (height // 256 + 1) * 256

        return bg_width, bg_height

    def affine_bg_dimensions(self):
        width, height = self._tmx.dimensions_in_pixels()
        small_dimensions = self.small_affine_bg_dimensions()
        big_dimensions = self.big_affine_bg_dimensions()

        if 'draw_big' in self._affine_bg_info:
            draw_big = bool(self._affine_bg_info['draw_big'])

            if draw_big:
                return big_dimensions
            elif small_dimensions == (None, None):
                raise ValueError('Too big size for a not big affine BG: ' + str(width) + ' - ' + str(height))
            else:
                return small_dimensions
        else:
            if small_dimensions == (None, None):
                return big_dimensions
            else:
                return small_dimensions

    def affine_bg_image(self):
        # Convert the TMX into its affine background image.

        if self._affine_bg_layers_count == 0:
            return None

        # The size of each individual background
        bg_width, bg_height = self.affine_bg_dimensions()

        # Compose the layers into a single background image
        gfx_im = Image.new("RGBA", (bg_width, bg_height * self._affine_bg_layers_count), self._tmx.background_color())
        for i, layer_path in enumerate(self._affine_bg_layers):
            self._tmx.compose(gfx_im, layer_path, 0, bg_height * i)

        # Make the image paletted
        gfx_im = gfx_im.quantize(256)

        return gfx_im

    def butano_header(self, regular_bg_data, affine_bg_data):
        # Convert the TMX into its C++ header.

        header_foreign_includes = set()
        header_local_includes = set()
        data_declarations = list()
        item_declarations = list()

        header_local_includes.add('bntmx.h')

        template = _templates[self._target]
        match self._target:
            case Target.butano:
                regular_bg = self._name + '_regular_bg' if self._regular_bg_layers_count > 0 else "bn::optional<bn::regular_bg_item>()"
                indentation_depth = 1
            case Target.c:
                regular_bg = ""
                indentation_depth = 0
            case _:
                raise ValueError('Unknown target: ' + str(self._target))

        # Regular background
        if self._target == Target.butano and regular_bg_data is not None:
            header_foreign_includes.add('bn_regular_bg_item.h')

            regular_bg_grit_literal = regular_bg_data['grit_data']

            regular_bg_map_literal = template['regular_bg_map'].format(
                big=regular_bg_data['big'],
                height=regular_bg_data['height'],
                map_compression=regular_bg_data['map_compression_label'],
                maps=regular_bg_data['maps'],
                name=regular_bg_data['name'],
                width=regular_bg_data['width'])

            if regular_bg_data['palette_item'] is None:
                regular_bg_palette_literal = template['bg_palette'].format(
                    bpp_mode=regular_bg_data['bpp_mode_label'],
                    colors_count=regular_bg_data['colors_count'],
                    palette_compression=regular_bg_data['palette_compression_label'],
                    name=regular_bg_data['name'])
            else:
                header_local_includes.add('bn_bg_palette_items_{palette_item}.h'.format(
                    palette_item=regular_bg_data['palette_item']))

                regular_bg_palette_literal = template['bg_palette_item'].format(
                    palette_item=regular_bg_data['palette_item'])

            regular_bg_tiles_literal = template['regular_bg_tiles'].format(
                bpp_mode=regular_bg_data['bpp_mode_label'],
                name=regular_bg_data['name'],
                tiles_compression=regular_bg_data['tiles_compression_label'],
                tiles_count=regular_bg_data['tiles_count'])

            regular_bg_item_declaration = template['regular_bg_item_declaration'].format(
                name=regular_bg_data['name'],
                regular_bg_map_literal=regular_bg_map_literal,
                regular_bg_palette_literal=regular_bg_palette_literal,
                regular_bg_tiles_literal=regular_bg_tiles_literal)

            data_declarations += [regular_bg_grit_literal]
            item_declarations += [regular_bg_item_declaration]
        elif self._target == Target.c and regular_bg_data is not None:
            regular_bg_grit_literal = regular_bg_data['grit_data']

            data_declarations += [regular_bg_grit_literal]

        # Affine background
        if self._target == Target.butano and affine_bg_data is not None:
            header_foreign_includes.add('bn_affine_bg_item.h')

            affine_bg_grit_literal = affine_bg_data['grit_data']

            affine_bg_map_literal = template['affine_bg_map'].format(
                big=affine_bg_data['big'],
                height=affine_bg_data['height'],
                map_compression=affine_bg_data['map_compression_label'],
                maps=affine_bg_data['maps'],
                name=affine_bg_data['name'],
                width=affine_bg_data['width'])

            if affine_bg_data['palette_item'] is None:
                affine_bg_palette_literal = template['bg_palette'].format(
                    bpp_mode='bn::bpp_mode::BPP_8',
                    colors_count=affine_bg_data['colors_count'],
                    palette_compression=affine_bg_data['palette_compression_label'],
                    name=affine_bg_data['name'])
            else:
                header_local_includes.add('bn_bg_palette_items_{palette_item}.h'.format(
                    palette_item=affine_bg_data['palette_item']))

                affine_bg_palette_literal = template['bg_palette_item'].format(
                    palette_item=affine_bg_data['palette_item'])

            affine_bg_tiles_literal = template['affine_bg_tiles'].format(
                name=affine_bg_data['name'],
                tiles_compression=affine_bg_data['tiles_compression_label'],
                tiles_count=affine_bg_data['tiles_count'])

            affine_bg_item_declaration = template['affine_bg_item_declaration'].format(
                name=affine_bg_data['name'],
                affine_bg_map_literal=affine_bg_map_literal,
                affine_bg_palette_literal=affine_bg_palette_literal,
                affine_bg_tiles_literal=affine_bg_tiles_literal)

            data_declarations += [affine_bg_grit_literal]
            item_declarations += [affine_bg_item_declaration]
        elif self._target == Target.c and affine_bg_data is not None:
            affine_bg_grit_literal = affine_bg_data['grit_data']

            data_declarations += [affine_bg_grit_literal]

        # Map tiles
        if self._map_tiles_item is not None:
            data = self._map_tiles_item.process()
            header_foreign_includes |= data['header_foreign_includes']
            header_local_includes |= data['header_local_includes']
            data_declarations += data['data_declarations']
            item_declarations += data['item_declarations']

        # Map objects
        if self._map_objects_item is not None:
            data = self._map_objects_item.process()
            header_foreign_includes |= data['header_foreign_includes']
            header_local_includes |= data['header_local_includes']
            data_declarations += data['data_declarations']
            item_declarations += data['item_declarations']

        return template['header_template'].format(
            data_declarations='\n\n'.join([d for d in data_declarations if d is not None]),
            includes=includes(header_foreign_includes, header_local_includes),
            item_declarations=indent('\n\n'.join([d for d in item_declarations if d is not None]), template['indentation'], indentation_depth),
            map=self,
            regular_bg=regular_bg)

    def butano_source(self):
        # Convert the TMX into its C++ source.

        source_foreign_includes = set()
        source_local_includes = set()
        data_definitions = list()

        template = _templates[self._target]

        # Map tiles
        if self._map_tiles_item is not None:
            data = self._map_tiles_item.process()
            source_foreign_includes |= data['source_foreign_includes']
            source_local_includes |= data['source_local_includes']
            data_definitions += data['data_definitions']

        # FIXME Drop tiles_getter
        tiles_getter = ''

        # Map objects
        if self._map_objects_item is not None:
            data = self._map_objects_item.process()
            source_foreign_includes |= data['source_foreign_includes']
            source_local_includes |= data['source_local_includes']
            data_definitions += data['data_definitions']

        # FIXME Drop map_object_getter
        map_object_getter = ''
        # FIXME Drop map_objects_getter_with_class
        map_objects_getter_with_class = ''

        return template['source_template'].format(
            data_definitions='\n\n'.join([d for d in data_definitions if d is not None]),
            includes=includes(source_foreign_includes, source_local_includes),
            map=self,
            object_getter=map_object_getter,
            objects_getter_with_class=map_objects_getter_with_class,
            tiles_getter=tiles_getter)

def process(target: Target, grit, maps_dirs, build_dir):
    if isinstance(target, str):
        target = Target[target]

    bntmx_dir = os.path.dirname(os.path.realpath(__file__))
    build_src_dir = os.path.join(build_dir, "src")

    if not os.path.exists(build_dir):
        os.makedirs(build_dir)
    if not os.path.exists(build_src_dir):
        os.makedirs(build_src_dir)

    # Export the global header
    include_filename = os.path.join(build_dir, "bntmx.h")
    include = read_template(target, "bntmx.h")
    write_to_file(include_filename, include)

    for maps_dir in maps_dirs:
        for map_file in os.listdir(maps_dir):
            if map_file.endswith('.tmx') and os.path.isfile(os.path.join(maps_dir, map_file)):
                tmx_filename = os.path.join(maps_dir, map_file)
                item = MapItem(target, tmx_filename)
                map_basename = item.basename()
                map_name = item.name()

                tmx_json_filename = os.path.join(maps_dir, map_basename + ".json")
                regular_bg_bmp_filename = os.path.join(build_dir, map_name + "_regular_bg.bntmx.bmp")
                affine_bg_bmp_filename = os.path.join(build_dir, map_name + "_affine_bg.bntmx.bmp")
                header_filename = os.path.join(build_dir, "bntmx_map_items_" + map_name + ".h")
                match target:
                    case Target.butano:
                        source_filename = os.path.join(build_dir, "src", "bntmx_map_items_" + map_name + ".cpp")
                    case Target.c:
                        source_filename = os.path.join(build_dir, "src", "bntmx_map_items_" + map_name + ".c")
                    case _:
                        raise ValueError('Unknown target: ' + str(target))

                # Don't rebuild unchanged files
                input_mtime = max(map(lambda filename : os.path.getmtime(filename) if os.path.isfile(filename) else 0, [tmx_filename, tmx_json_filename] + item.dependencies()))
                output_mtime = min(map(lambda filename : os.path.getmtime(filename) if os.path.isfile(filename) else 0, [regular_bg_bmp_filename, affine_bg_bmp_filename, header_filename, source_filename]))
                if input_mtime < output_mtime:
                    continue

                # Export the regular background
                regular_bg_image = item.regular_bg_image()
                if regular_bg_image is not None:
                    regular_bg_image.save(regular_bg_bmp_filename, "BMP")
                    _, src_height = item._tmx.dimensions_in_pixels()
                    regular_bg_item = RegularBgItem(target, regular_bg_bmp_filename, map_name + '_regular_bg', build_dir, item._regular_bg_info)
                    regular_bg_data = regular_bg_item.process(grit)
                else:
                    regular_bg_data = None

                # Export the affine background
                affine_bg_image = item.affine_bg_image()
                if affine_bg_image is not None:
                    affine_bg_image.save(affine_bg_bmp_filename, "BMP")
                    _, src_height = item._tmx.dimensions_in_pixels()
                    affine_bg_item = AffineBgItem(target, affine_bg_bmp_filename, map_name + '_affine_bg', build_dir, item._affine_bg_info)
                    affine_bg_data = affine_bg_item.process(grit)
                else:
                    affine_bg_data = None

                # Export the C++ header
                write_to_file(header_filename, item.butano_header(regular_bg_data, affine_bg_data))

                # Export the C++ source
                write_to_file(source_filename, item.butano_source())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Compile Tiled maps into code and data usable by the game engine.')
    parser.add_argument('--target', type=Target, choices=list(Target), required=True, help='build target')
    parser.add_argument('--grit', required=True, help='grit executable path')
    parser.add_argument('--build', required=True, help='build directory path')
    parser.add_argument('mapsdirs', metavar='mapsdir', nargs='+',
                        help='maps directories paths')
    args = parser.parse_args()
    process(args.target, args.grit, args.mapsdirs, args.build)
