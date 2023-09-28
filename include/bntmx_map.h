/*
 * Copyright (c) 2023 Adrien Plazas <kekun.plazas@laposte.net>
 * zlib License, see LICENSE file.
 */

#ifndef BNTMX_MAP_H
#define BNTMX_MAP_H

#include <bn_size.h>
#include <bn_span.h>
#include <bn_regular_bg_item.h>
#include "bntmx_map_object.h"
#include "bntmx_map_tile.h"

namespace bntmx
{

class map
{

public:
    virtual constexpr ~map() {}

    /**
     * @brief Returns the dimensions of the map in pixels.
     */
    virtual constexpr bn::size dimensions_in_pixels() const = 0;

    /**
     * @brief Returns the dimensions of the map in tiles.
     */
    virtual constexpr bn::size dimensions_in_tiles() const = 0;

    /**
     * @brief Returns the dimensions of each tile of the map.
     */
    virtual constexpr bn::size tile_dimensions() const = 0;

    /**
     * @brief Returns the width of the map in pixels.
     */
    virtual constexpr int width_in_pixels() const = 0;

    /**
     * @brief Returns the height of the map in pixels.
     */
    virtual constexpr int height_in_pixels() const = 0;

    /**
     * @brief Returns the width of the map in tiles.
     */
    virtual constexpr int width_in_tiles() const = 0;

    /**
     * @brief Returns the height of the map in tiles.
     */
    virtual constexpr int height_in_tiles() const = 0;

    /**
     * @brief Returns the width of each tile of the map.
     */
    virtual constexpr int tile_width() const = 0;

    /**
     * @brief Returns the height of each tile of the map.
     */
    virtual constexpr int tile_height() const = 0;

    /**
     * @brief Returns the number of graphics layers of the map.
     */
    virtual constexpr int n_graphics_layers() const = 0;

    /**
     * @brief Returns the number of objects layers of the map.
     */
    virtual constexpr int n_objects_layers() const = 0;

    /**
     * @brief Returns the number of tiles layers of the map.
     */
    virtual constexpr int n_tiles_layers() const = 0;

    /**
     * @brief Returns the bn::regular_bg_item containing the graphics layers of the map.
     */
    virtual constexpr bn::regular_bg_item regular_bg_item() const = 0;

    /**
     * @brief Returns the object with the given ID.
     * @param object_id ID of the objects.
     */
    virtual const bntmx::map_object object(int object_id) const = 0;

    /**
     * @brief Returns the classless objects of the given layer of the map.
     * @param objects_layer_index Index of the objects layer.
     */
    virtual const bn::span<const bntmx::map_object> objects(int objects_layer_index) const = 0;

    /**
     * @brief Returns the objects of the given class and layer of the map.
     * @param objects_layer_index Index of the objects layer.
     * @param objects_class Class of the objects.
     */
    virtual const bn::span<const bntmx::map_object> objects(int objects_layer_index, int objects_class) const = 0;

    /**
     * @brief Returns the tiles of the given layer of the map.
     * @param tiles_layer_index Index of the tiles layer.
     */
    virtual const bn::span<const bntmx::map_tile> tiles(int tiles_layer_index) const = 0;
};

}

#endif
