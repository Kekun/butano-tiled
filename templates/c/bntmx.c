/*
 * Copyright (c) 2026 Adrien Plazas <kekun.plazas@laposte.net>
 * zlib License, see LICENSE file.
 */

#include "bntmx.h"

#include <assert.h>

/**
 * @brief Returns the dimensions of the map.
 */
bntmx_size bntmx_map_tiles_item_dimensions(const bntmx_map_tiles_item* this)
{
    return this->dimensions;
}

/**
 * @brief Returns the width of the map.
 */
int bntmx_map_tiles_item_width(const bntmx_map_tiles_item* this)
{
    return this->dimensions.width;
}

/**
 * @brief Returns the height of the map.
 */
int bntmx_map_tiles_item_height(const bntmx_map_tiles_item* this)
{
    return this->dimensions.height;
}

/**
 * @brief Returns the number of referenced layers.
 */
int bntmx_map_tiles_item_layers_count(const bntmx_map_tiles_item* this)
{
    return this->layers_count;
}

/**
 * @brief Returns the tiles of the given layer of the map.
 * @param layer_index Index of the tiles layer.
 */
const bntmx_map_tile* bntmx_map_tiles_item_tiles(const bntmx_map_tiles_item* this, int layer_index)
{
    int tiles_count = this->dimensions.width * this->dimensions.height;
    assert(layer_index < this->layers_count);
    return this->tiles_ptr + layer_index * tiles_count;
}

/**
 * @brief Returns the index of the referenced map tile in the specified map tile coordinates.
 *
 * @param tile_x Horizontal position of the map tile [0..width).
 * @param tile_y Vertical position of the map tile [0..height).
 * @return The index of the referenced map tile.
 */
int bntmx_map_tiles_item_tile_index(const bntmx_map_tiles_item* this, int tile_x, int tile_y)
{
    assert(tile_x >= 0 && tile_x < this->dimensions.width);
    assert(tile_y >= 0 && tile_y < this->dimensions.height);

    return (tile_y * this->dimensions.width) + tile_x;
}

/**
 * @brief Returns the referenced map tile in the specified map tile coordinates.
 *
 * @param layer_index Index of the tiles layer.
 * @param tile_x Horizontal position of the map tile [0..width).
 * @param tile_y Vertical position of the map tile [0..height).
 * @return The referenced map tile.
 */
bntmx_map_tile bntmx_map_tiles_item_tile(const bntmx_map_tiles_item* this, int layer_index, int tile_x, int tile_y)
{
    return bntmx_map_tiles_item_tiles(this, layer_index)[bntmx_map_tiles_item_tile_index(this, tile_x, tile_y)];
}

/**
 * @brief Returns the dimensions of the map.
 */
bntmx_size bntmx_orthogonal_map_item_dimensions(const bntmx_orthogonal_map_item* this)
{
    return (bntmx_size) { bntmx_map_tiles_item_width(&this->tiles_item) * this->tile_dimensions.width, bntmx_map_tiles_item_height(&this->tiles_item) * this->tile_dimensions.height };
}

/**
 * @brief Returns the width of the map.
 */
int bntmx_orthogonal_map_item_width(const bntmx_orthogonal_map_item* this)
{
    return bntmx_map_tiles_item_width(&this->tiles_item) * this->tile_dimensions.width;
}

/**
 * @brief Returns the height of the map.
 */
int bntmx_orthogonal_map_item_height(const bntmx_orthogonal_map_item* this)
{
    return bntmx_map_tiles_item_height(&this->tiles_item) * this->tile_dimensions.height;
}

/**
 * @brief Returns the dimensions of each tile of the map.
 */
bntmx_size bntmx_orthogonal_map_item_tile_dimensions(const bntmx_orthogonal_map_item* this)
{
    return this->tile_dimensions;
}

/**
 * @brief Returns the width of each tile of the map.
 */
int bntmx_orthogonal_map_item_tile_width(const bntmx_orthogonal_map_item* this)
{
    return this->tile_dimensions.width;
}

/**
 * @brief Returns the height of each tile of the map.
 */
int bntmx_orthogonal_map_item_tile_height(const bntmx_orthogonal_map_item* this)
{
    return this->tile_dimensions.height;
}

/**
 * @brief Returns the map tiles item.
 */
const bntmx_map_tiles_item* bntmx_orthogonal_map_item_tiles_item(const bntmx_orthogonal_map_item* this)
{
    return &this->tiles_item;
}

/**
 * @brief Returns the position of the referenced map tile in the specified map tile coordinates.
 *
 * @param x Horizontal position of the map tile [0...width).
 * @param y Vertical position of the map tile [0..height).
 * @return The position of the referenced map tile.
 */
bntmx_point bntmx_orthogonal_map_item_tile_position(const bntmx_orthogonal_map_item* this, int x, int y)
{
    assert(x >= 0 && x < bntmx_orthogonal_map_item_width(this));
    assert(y >= 0 && y < bntmx_orthogonal_map_item_height(this));

    return (bntmx_point) { x / this->tile_dimensions.width, y / this->tile_dimensions.height };
}

/**
 * @brief Returns the referenced map tile in the specified map tile coordinates.
 *
 * @param layer_index Index of the tiles layer.
 * @param x Horizontal position of the map tile [0..width).
 * @param y Vertical position of the map tile [0..height).
 * @return The referenced map tile.
 */
bntmx_map_tile bntmx_orthogonal_map_item_tile(const bntmx_orthogonal_map_item* this, int layer_index, int x, int y)
{
    assert(x >= 0 && x < bntmx_orthogonal_map_item_width(this));
    assert(y >= 0 && y < bntmx_orthogonal_map_item_height(this));

    bntmx_point tile_position = bntmx_orthogonal_map_item_tile_position(this, x, y);
    return bntmx_map_tiles_item_tile(&this->tiles_item, layer_index, tile_position.x, tile_position.y);
}

/**
 * @brief Returns the number of referenced layers.
 */
int bntmx_map_objects_item_layers_count(const bntmx_map_objects_item* this)
{
    return this->layers_count;
}

/**
 * @brief Returns the object with the given ID.
 * @param object_id ID of the objects.
 */
bntmx_map_object bntmx_map_objects_item_object(const bntmx_map_objects_item* this, int object_id)
{
    assert(object_id < this->objects_count);
    return this->objects[object_id];
}

/**
 * @brief Returns the objects of the given class and layer of the map.
 * @param objects_layer_index Index of the objects layer.
 * @param objects_class Class of the objects.
 */
bntmx_span bntmx_map_objects_item_objects(const bntmx_map_objects_item* this, int objects_layer_index, bntmx_map_object_class objects_class)
{
    assert(objects_layer_index < this->layers_count);
    assert(objects_class <= this->classes_count);
    const bntmx_slice* object_slices = this->object_slices + objects_layer_index * (this->classes_count + 1);
    const void* begin = &this->objects[object_slices[objects_class].index];
    const void* end = begin + sizeof(bntmx_map_object) * object_slices[objects_class].length;
    return (bntmx_span) { begin, end };
}
