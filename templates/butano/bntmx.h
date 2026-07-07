/*
 * Copyright (c) 2023 Adrien Plazas <kekun.plazas@laposte.net>
 * zlib License, see LICENSE file.
 */

#ifndef BNTMX_H
#define BNTMX_H

#include <bn_fixed_point.h>
#include <bn_optional.h>
#include <bn_point.h>
#include <bn_regular_bg_item.h>
#include <bn_size.h>
#include <bn_span.h>

namespace bntmx
{

struct map_object
{
    bn::fixed_point position;
    uint16_t id;
};

typedef uint16_t map_tile;

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
     * @brief Returns the graphics layers of the map.
     */
    virtual constexpr  bn::optional<bn::regular_bg_item> graphics() const = 0;

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

    /**
     * @brief Returns the index of the referenced map tile in the specified map tile coordinates.
     *
     * @param tile_x Horizontal position of the map tile [0..dimensions_in_tiles().width()).
     * @param tile_y Vertical position of the map tile [0..dimensions_in_tiles().height()).
     * @return The index of the referenced map tile.
     */
    [[nodiscard]] constexpr int tile_index(int tile_x, int tile_y) const
    {
        int width = dimensions_in_tiles().width();
        BN_ASSERT(tile_x >= 0 && tile_x < width, "Invalid map tile x: ", tile_x, " - ", width);
        BN_ASSERT(tile_y >= 0 && tile_y < dimensions_in_tiles().height(), "Invalid map tile y: ", tile_y, " - ", dimensions_in_tiles().height());

        return (tile_y * width) + tile_x;
    }

    /**
     * @brief Returns the index of the referenced map tile in the specified map tile coordinates.
     *
     * @param map_position Position of the map tile.
     * @return The index of the referenced map tile.
     */
    [[nodiscard]] constexpr int tile_index(const bn::point& map_position) const
    {
        return tile_index(map_position.x(), map_position.y());
    }

    /**
     * @brief Returns the referenced map tile in the specified map tile coordinates.
     *
     * @param tile_x Horizontal position of the map tile [0..dimensions_in_tiles().width()).
     * @param tile_y Vertical position of the map tile [0..dimensions_in_tiles().height()).
     * @return The referenced map tile.
     */
    [[nodiscard]] constexpr bntmx::map_tile tile(int tiles_layer_index, int tile_x, int tile_y) const
    {
        return tiles(tiles_layer_index)[tile_index(tile_x, tile_y)];
    }

    /**
     * @brief Returns the index of the referenced map tile in the specified map tile coordinates.
     *
     * @param tile_x Horizontal position of the map tile [0..dimensions_in_tiles().width()).
     * @param tile_y Vertical position of the map tile [0..dimensions_in_tiles().height()).
     * @return The index of the referenced map tile.
     */
    [[nodiscard]] constexpr int tile_index_in_pixels(int tile_x, int tile_y) const
    {
        return tile_index(tile_x / tile_dimensions().width(), tile_y / tile_dimensions().height());
    }

    /**
     * @brief Returns the index of the referenced map tile in the specified map tile coordinates.
     *
     * @param map_position Position of the map tile.
     * @return The index of the referenced map tile.
     */
    [[nodiscard]] constexpr int tile_index_in_pixels(const bn::point& map_position) const
    {
        return tile_index_in_pixels(map_position.x(), map_position.y());
    }

    /**
     * @brief Returns the referenced map tile in the specified map tile coordinates.
     *
     * @param tile_x Horizontal position of the map tile [0..dimensions_in_tiles().width()).
     * @param tile_y Vertical position of the map tile [0..dimensions_in_tiles().height()).
     * @return The referenced map tile.
     */
    [[nodiscard]] constexpr bntmx::map_tile tile_in_pixels(int tiles_layer_index, int tile_x, int tile_y) const
    {
        return tiles(tiles_layer_index)[tile_index_in_pixels(tile_x, tile_y)];
    }
};

}

#endif
