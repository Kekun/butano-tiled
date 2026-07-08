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

using map_tile = uint16_t;

struct map_object
{
    bn::fixed_point position;
    uint16_t id;
};

class map_tiles_item
{
public:
    /**
     * @brief Constructor.
     */
    constexpr map_tiles_item(const bntmx::map_tile& tiles_ref, bn::size dimensions, int layers_count)
        : _dimensions(dimensions)
        , _layers_count(layers_count)
        , _tiles_ptr(&tiles_ref)
    {
    }

    /**
     * @brief Returns the dimensions of the map.
     */
    [[nodiscard]] constexpr bn::size dimensions() const
    {
        return _dimensions;
    }

    /**
     * @brief Returns the width of the map.
     */
    [[nodiscard]] constexpr int width() const
    {
        return _dimensions.width();
    }

    /**
     * @brief Returns the height of the map.
     */
    [[nodiscard]] constexpr int height() const
    {
        return _dimensions.height();
    }

    /**
     * @brief Returns the number of referenced layers.
     */
    [[nodiscard]] constexpr int layers_count() const
    {
        return _layers_count;
    }

    /**
     * @brief Returns the tiles of the given layer of the map.
     * @param layer_index Index of the tiles layer.
     */
    [[nodiscard]] const bn::span<const bntmx::map_tile> tiles(int layer_index) const
    {
        int tiles_count = _dimensions.width() * _dimensions.height();
        BN_ASSERT(layer_index < _layers_count, "Invalid tiles layer index: ", layer_index);
        return bn::span<const bntmx::map_tile>(_tiles_ptr + layer_index * tiles_count, tiles_count);
    }

    /**
     * @brief Returns the index of the referenced map tile in the specified map tile coordinates.
     *
     * @param tile_x Horizontal position of the map tile [0..width()).
     * @param tile_y Vertical position of the map tile [0..height()).
     * @return The index of the referenced map tile.
     */
    [[nodiscard]] constexpr int tile_index(int tile_x, int tile_y) const
    {
        BN_ASSERT(tile_x >= 0 && tile_x < width(), "Invalid map tile x: ", tile_x, " - ", width());
        BN_ASSERT(tile_y >= 0 && tile_y < height(), "Invalid map tile y: ", tile_y, " - ", height());

        return (tile_y * width()) + tile_x;
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
     * @param layer_index Index of the tiles layer.
     * @param tile_x Horizontal position of the map tile [0..width()).
     * @param tile_y Vertical position of the map tile [0..height()).
     * @return The referenced map tile.
     */
    [[nodiscard]] constexpr bntmx::map_tile tile(int layer_index, int tile_x, int tile_y) const
    {
        return tiles(layer_index)[tile_index(tile_x, tile_y)];
    }

    /**
     * @brief Returns the referenced map tile in the specified map tile coordinates.
     *
     * @param layer_index Index of the tiles layer.
     * @param map_position Position of the map tile.
     * @return The referenced map tile.
     */
    [[nodiscard]] constexpr bntmx::map_tile tile(int layer_index, const bn::point& map_position) const
    {
        return tile(layer_index, map_position.x(), map_position.y());
    }

private:
    bn::size _dimensions;
    int _layers_count;
    const bntmx::map_tile* _tiles_ptr;
};

class orthogonal_map_item
{
public:
    /**
     * @brief Constructor.
     */
    constexpr orthogonal_map_item(bntmx::map_tiles_item tiles_item, bn::size tile_dimensions)
        : _tiles_item(tiles_item)
        , _tile_dimensions(tile_dimensions)
    {
    }

    /**
     * @brief Returns the dimensions of the map.
     */
    [[nodiscard]] constexpr bn::size dimensions() const
    {
        return bn::size(_tiles_item.width() * _tile_dimensions.width(), _tiles_item.height() * _tile_dimensions.height());
    }

    /**
     * @brief Returns the width of the map.
     */
    [[nodiscard]] constexpr int width() const
    {
        return _tiles_item.width() * _tile_dimensions.width();
    }

    /**
     * @brief Returns the height of the map.
     */
    [[nodiscard]] constexpr int height() const
    {
        return _tiles_item.height() * _tile_dimensions.height();
    }

    /**
     * @brief Returns the dimensions of each tile of the map.
     */
    [[nodiscard]] constexpr bn::size tile_dimensions() const
    {
        return _tile_dimensions;
    }

    /**
     * @brief Returns the width of each tile of the map.
     */
    [[nodiscard]] constexpr int tile_width() const
    {
        return _tile_dimensions.width();
    }

    /**
     * @brief Returns the height of each tile of the map.
     */
    [[nodiscard]] constexpr int tile_height() const
    {
        return _tile_dimensions.height();
    }

    /**
     * @brief Returns the map tiles item.
     */
    [[nodiscard]] const bntmx::map_tiles_item& tiles_item() const
    {
        return _tiles_item;
    }

    /**
     * @brief Returns the position of the referenced map tile in the specified map tile coordinates.
     *
     * @param x Horizontal position of the map tile [0...width()).
     * @param y Vertical position of the map tile [0..height()).
     * @return The position of the referenced map tile.
     */
    [[nodiscard]] constexpr bn::point tile_position(int x, int y) const
    {
        BN_ASSERT(x >= 0 && x < width(), "Invalid map x: ", x, " - ", width());
        BN_ASSERT(y >= 0 && y < height(), "Invalid map y: ", y, " - ", height());

        return bn::point(x / tile_width(), y / tile_height());
    }

    /**
     * @brief Returns the position of the referenced map tile in the specified map tile coordinates.
     *
     * @param position Position of the map tile.
     * @return The position of the referenced map tile.
     */
    [[nodiscard]] constexpr bn::point tile_position(const bn::point& position) const
    {
        return tile_position(position.x(), position.y());
    }

    /**
     * @brief Returns the referenced map tile in the specified map tile coordinates.
     *
     * @param layer_index Index of the tiles layer.
     * @param x Horizontal position of the map tile [0..width()).
     * @param y Vertical position of the map tile [0..height()).
     * @return The referenced map tile.
     */
    [[nodiscard]] constexpr bntmx::map_tile tile(int layer_index, int x, int y) const
    {
        BN_ASSERT(x >= 0 && x < width(), "Invalid map x: ", x, " - ", width());
        BN_ASSERT(y >= 0 && y < height(), "Invalid map y: ", y, " - ", height());

        return _tiles_item.tile(layer_index, tile_position(x, y));
    }

    /**
     * @brief Returns the referenced map tile in the specified map tile coordinates.
     *
     * @param layer_index Index of the tiles layer.
     * @param position Position of the map tile.
     * @return The referenced map tile.
     */
    [[nodiscard]] constexpr bntmx::map_tile tile(int layer_index, const bn::point& position) const
    {
        return tile(layer_index, position.x(), position.y());
    }

private:
    bntmx::map_tiles_item _tiles_item;
    bn::size _tile_dimensions;
};

class map_item
{

public:
    virtual constexpr ~map_item() {}

    /**
     * @brief Returns the dimensions of the map in pixels.
     */
    virtual constexpr bn::size dimensions_in_pixels() const = 0;

    /**
     * @brief Returns the width of the map in pixels.
     */
    virtual constexpr int width_in_pixels() const = 0;

    /**
     * @brief Returns the height of the map in pixels.
     */
    virtual constexpr int height_in_pixels() const = 0;

    /**
     * @brief Returns the number of regular background layers of the map.
     */
    virtual constexpr int regular_bg_layers_count() const = 0;

    /**
     * @brief Returns the number of objects layers of the map.
     */
    virtual constexpr int objects_layers_count() const = 0;

    /**
     * @brief Returns the regular background layers of the map.
     */
    virtual constexpr  bn::optional<bn::regular_bg_item> regular_bg() const = 0;

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
};

}

#endif
