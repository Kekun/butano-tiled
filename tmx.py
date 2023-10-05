"""
Copyright (c) 2023 Adrien Plazas <kekun.plazas@laposte.net>
zlib License, see LICENSE file.
"""

from PIL import Image
import logging
import os
import PIL
import xml.etree.ElementTree as ET

def _bg_size(size: int):
    """
    Return a size rounded up to the next 256 multiple. This helps converting the
    size of a map into the size of its background images.

    :param size: the size of the map
    :returns: the size of the background that can fit the requested size
    """

    return size if size % 256 == 0 else (size // 256 + 1) * 256

def _object_position(object_node: ET.Element) -> tuple[int,int]:
    """
    Return the center position of an object.

    :param object_node: the node of the object
    :returns: the abscissa and ordinate of the center of the object
    """

    # While the origin of maps is their top-left corner, the origin of
    # objects is their bottom left one, hence we have to substract half
    # their height and not add it to get their center.
    x = int(object_node.get("x")) + int(object_node.get("width")) // 2
    y = int(object_node.get("y")) - int(object_node.get("height")) // 2
    return x, y

def _objects_layer_path_to_xpath(layer_path: str) -> str:
    """
    Return the XPath to the node of the given objects layer path from the JSON descriptor.

    :param layer_path: the path to the objects layer
    :returns: the XPath
    """

    layer_path_elements = layer_path.split("/")
    xpath = "."
    for group in layer_path_elements[:-1]:
        xpath += "/group[@name='" + group + "']"
    xpath += "/objectgroup[@name='" + layer_path_elements[-1] + "']"

    return xpath

def _tiles_layer_path_to_xpath(layer_path: str) -> str:
    """
    Return the XPath to the node of the given tiles layer path from the JSON descriptor.

    :param layer_path: the path to the tiles layer
    :returns: the XPath
    """

    layer_path_elements = layer_path.split("/")
    xpath = "."
    for group in layer_path_elements[:-1]:
        xpath += "/group[@name='" + group + "']"
    xpath += "/layer[@name='" + layer_path_elements[-1] + "']"

    return xpath

class MapObject:
    def __init__(self, x: int, y: int, id: int, object_class: str):
        """
        :param x: the abscissa of the center of the object
        :param y: the ordinate of the center of the object
        :param id: the ID of the oject
        :param object_class: the class of the object
        """

        self.x = x
        self.y = y
        self.id = id
        self.object_class = object_class

class MapObjects:
    def __init__(self):
        self._map_objects = {"": []}

    def add(self, map_object: MapObject):
        """
        Add an object for the given class.

        :param map_object: the object
        """

        if map_object.object_class in self._map_objects:
            self._map_objects[map_object.object_class].append(map_object)
        else:
            self._map_objects[map_object.object_class] = [map_object]

    def ids(self) -> list[int]:
        """
        Return a list the ids of all map objects.

        :returns: a list the ids of all map objects
        """

        return [map_object.id for _, map_objects_list in self._map_objects.items() for map_object in map_objects_list]

    def objects(self) -> dict[str,list[MapObject]]:
        """
        Return the dict of objects per class.

        :returns: the dict of objects per class
        """

        return self._map_objects

class TSX:
    def __init__(self, filename: str):
        """
        :param filename: the filename of the *.tsx file to parse
        """

        self._filename = os.path.realpath(filename)
        self._root = ET.parse(filename)

        self._n_tiles = int(self._root.find(".").get("tilecount"))
        self._tile_width = int(self._root.find(".").get("tilewidth"))
        self._tile_height = int(self._root.find(".").get("tileheight"))
        self._columns = int(self._root.find(".").get("columns"))
        self._lines = self._n_tiles // self._columns
        self._image = Image.open(self.image_filename())

    def filename(self) -> str:
        """
        Return the filename of the *.tsx file.

        :returns: the filename of the *.tsx file
        """

        return self._filename

    def image_filename(self) -> str:
        """
        Return the filename of the tileset's image.

        :returns: the filename of the tileset's image
        """

        directory = os.path.dirname(self._filename)
        return os.path.join(directory, self._root.find("./image").get("source"))

    def n_tiles(self) -> int:
        """
        Return the number of tiles in the set.

        :returns: the number of tiles in the set
        """

        return self._n_tiles

    def compose(self, dst_image: PIL.Image.Image, tile_id: int, x: int, y: int):
        """
        Compose a tile on an image.

        :param dst_image: the image to draw the tile on
        :param tile_id: the ID of the tile to draw
        :param x: the abscissa of the top-left corner from which to draw
        :param y: the ordinate of the top-left corner from which to draw
        """

        src_x = (tile_id % self._columns) * self._tile_width
        src_y = (tile_id // self._columns) * self._tile_height
        dst_image.alpha_composite(self._image, (x, y), (src_x, src_y, src_x + self._tile_width, src_y + self._tile_height))

class TMX:
    def __init__(self, filename: str):
        """
        :param filename: the filename of the *.tmx file to parse
        """

        self._filename = os.path.realpath(filename)
        self._root = ET.parse(self._filename)

        self._columns = int(self._root.find(".").get("width"))
        self._lines = int(self._root.find(".").get("height"))

        self._tile_width = int(self._root.find(".").get("tilewidth"))
        self._tile_height = int(self._root.find(".").get("tileheight"))

        directory = os.path.dirname(self._filename)
        self._tilesets = []
        for tileset in self._root.findall("./tileset"):
            tsx = TSX(os.path.join(directory, tileset.get("source")))
            first_id = int(tileset.get("firstgid"))
            last_id = first_id + tsx.n_tiles() - 1
            self._tilesets.append((first_id, last_id, tsx))

    def dependencies(self) -> list[str]:
        """
        Return the list of filenames the map depends on.

        :returns: the list of filenames the map depends on
        """

        deps = []
        for first, last, tsx in self._tilesets:
            deps.append(tsx.filename())
            deps.append(tsx.image_filename())
        return deps

    def dimensions_in_pixels(self) -> tuple[int,int]:
        """
        Return the width and height of the map in pixels.

        :returns: the width and height of the map in pixels
        """

        return (self._columns * self._tile_width, self._lines * self._tile_height)

    def dimensions_in_tiles(self) -> tuple[int,int]:
        """
        Return the width and height of the map in tiles.

        :returns: the width and height of the map in tiles
        """

        return (self._columns, self._lines)

    def tile_dimensions(self) -> tuple[int,int]:
        """
        Return the width and height of the tiles in pixel.

        :returns: the width and height of the tiles in pixel
        """

        return (self._tile_width, self._tile_height)

    def background_color(self) -> str:
        """
        Return the background color hex code of the map, with the # prefix.

        :returns: the background color hex code
        """

        return self._root.find(".").get("backgroundcolor")

    def tilesets(self) -> list[tuple[int,int,TSX]]:
        """
        Return the list of tilesets consisting of their first ID in the map,
        their last ID in the map, and their TSX object.

        :returns: the tilesets
        """

        return self._tilesets

    def objects(self, layer_paths: list[str]|str) -> MapObjects:
        """
        Return the objects of layers. The objects are sorted by class in a dict.

        :param layer_paths: the paths (or single path) to the objects layers
        :returns: the objects
        """

        if isinstance(layer_paths, str):
            layer_paths = [layer_paths]

        objects = MapObjects()
        for layer_path in layer_paths:
            layer_xpath = _objects_layer_path_to_xpath(layer_path)
            layer_node = self._root.find(layer_xpath)
            if layer_node is None:
                logging.critical(self._filename + ": " + layer_path + ": Not an objects layer path")
                exit(1)

            xpath = layer_xpath + "/object"
            for item_node in self._root.findall(xpath):
                item_id = item_node.get("name")
                item_class = item_node.get("type")
                item_class = "" if item_class is None else item_class
                item_x, item_y = _object_position(item_node)
                objects.add(MapObject(item_x, item_y, item_id, item_class))
        return objects

    def compose(self, dst_image: PIL.Image.Image, layer_paths: list[str]|str, x: int, y: int):
        """
        Compose layers on an image. Each layer in composed over the previous ones.

        :param dst_image: the image to draw the layers on
        :param layer_paths: the paths (or single path) to the graphics layers
        :param x: the abscissa of the top-left corner from which to draw
        :param y: the ordinate of the top-left corner from which to draw
        """

        if isinstance(layer_paths, str):
            layer_paths = [layer_paths]

        for layer_path in layer_paths:
            layer_xpath = _tiles_layer_path_to_xpath(layer_path)
            layer_node = self._root.find(layer_xpath)
            if layer_node is None:
                logging.critical(self._filename + ": " + layer_path + ": Not a graphics layer path")
                exit(1)

            xpath = layer_xpath + "/data[@encoding='csv']"
            node = self._root.find(xpath)
            if node is None:
                logging.critical(self._filename + ": " + layer_path + ": Invalid graphics layer path, expected CSV-encoded data")
                exit(1)

            # The size of the map, in pixels
            src_width, src_height = self.dimensions_in_pixels()
            # The size of each individual background
            bg_width, bg_height = _bg_size(src_width), _bg_size(src_height)
            # The offset to center the layer on the background
            offset_x, offset_y = (bg_width - src_width) // 2, (bg_height - src_height) // 2

            y2 = 0
            for line in iter(node.text.splitlines()):
                if line == '':
                    continue;

                x2 = 0
                for tile_id in line.split(","):
                    if tile_id == '':
                        continue;

                    tile_id = int(tile_id)

                    if tile_id != 0:
                        for first, last, tsx in self._tilesets:
                            if tile_id >= first and tile_id <= last:
                                tsx.compose(dst_image, tile_id - first, x + x2 * self._tile_width + offset_x, y + y2 * self._tile_height + offset_y)

                    x2 = x2 + 1
                y2 = y2 + 1

    def _tiles(self, layer_path: str) -> list[str]:
        """
        Return the tiles of a layer.

        :param layer_path: the path to the tiles layer
        :returns: the tiles
        """

        # Parse the CSV tiles data to turn in into a Python list of tile IDs.
        line_is_not_empty = lambda line: line != ''

        layer_xpath = _tiles_layer_path_to_xpath(layer_path)
        layer_node = self._root.find(layer_xpath)
        if layer_node is None:
            logging.critical(self._filename + ": " + layer_path + ": Not a tiles layer path")
            exit(1)

        xpath = layer_xpath + "/data[@encoding='csv']"
        node = self._root.find(xpath)
        if node is None:
            logging.critical(self._filename + ": " + layer_path + ": Invalid tiles layer path, expected CSV-encoded data")
            exit(1)

        lines = filter(line_is_not_empty, node.text.splitlines())
        tiles = [str(int(tile)) for line in lines for tile in line.strip(",").split(",")]

        # Check the list of tile IDs is valid.
        n_tiles = len(tiles)
        expected_n_tiles = self._columns * self._lines
        if n_tiles != expected_n_tiles:
            logging.critical(self._filename + ": " + layer_path + ": Invalid number of tiles, expected " + str(expected_n_tiles) + ", got " + str(n_tiles))
            exit(1)

        return tiles

    def tiles(self, layer_paths: list[str]|str) -> list[str]:
        """
        Return the tiles of layers. The latest non-empty tile is used for each layer.

        :param layer_paths: the paths (or single path) to the tiles layers
        :returns: the tiles
        """

        if isinstance(layer_paths, str):
            return self._tiles(layer_paths)

        n_tiles = self._columns * self._lines
        n_layers = len(layer_paths)
        # Reversed so we can look for non-empty tiles starting from the topmost layer
        tiles_layers = reversed(list(map(self._tiles, layer_paths)))
        tiles = []
        for i in range(0, n_tiles):
            tile = '0'
            for tiles_layer in tiles_layers:
                if tiles_layer[i] != '0':
                    tile = tiles_layer[i]
                    # We can stop here because we look from the topmost layer
                    break
            tiles.append(tile)

        return tiles
