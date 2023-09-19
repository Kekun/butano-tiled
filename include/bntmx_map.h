/*
 * Copyright (c) 2023 Adrien Plazas <kekun.plazas@laposte.net>
 * zlib License, see LICENSE file.
 */

#ifndef BNTMX_MAP_H
#define BNTMX_MAP_H

namespace bntmx
{
    class Scene;
}

#include <bn_fixed.h>
#include <bn_optional.h>
#include <bn_regular_bg_ptr.h>
#include "bntmx_map_id.h"
#include "bntmx_map_item.h"
#include "bntmx_teleport.h"

#define BNTMX_TILE_SIZE 16

namespace bntmx
{
    class Map
    {
        public:
            virtual ~Map() {}
            virtual constexpr uint16_t width() const = 0;
            virtual constexpr uint16_t height() const = 0;
            virtual constexpr uint8_t n_layers() const = 0;
            virtual constexpr uint8_t n_items(uint8_t layer_index) const = 0;
            virtual constexpr const uint8_t* collisions(uint8_t layer_index) const = 0;

            constexpr int get_tile_x(const bn::fixed& x) const
            {
                return bn::clamp(x.integer() / BNTMX_TILE_SIZE, 0, width() - 1);
            }

            constexpr int get_tile_y(const bn::fixed& y) const
            {
                return bn::clamp(y.integer() / BNTMX_TILE_SIZE, 0, height() - 1);
            }

            virtual MapItem get_item(uint8_t layer_index, uint8_t item_index) const = 0;

            virtual bn::regular_bg_ptr& background() = 0;
            virtual bn::regular_bg_ptr& foreground() = 0;

            virtual bn::regular_bg_ptr create_layer(uint8_t layer_index) const = 0;

            virtual void init(Scene& scene) = 0;
            virtual void enter(Scene& scene) = 0;
            virtual void leave(Scene& scene) = 0;
            virtual void deinit(Scene& scene) = 0;
            virtual void interact_with_item(Scene& scene, int item_id) = 0;
            virtual void update_background(bn::fixed camera_x,
                                           bn::fixed camera_y) = 0;
            virtual void update_foreground(bn::fixed camera_x,
                                           bn::fixed camera_y) = 0;
            virtual bn::optional<Teleport> out_of_bounds(bn::fixed_point position) = 0;
    };

    Map* create_map(MapId map_id);
}

#endif
