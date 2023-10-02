"""
Copyright (c) 2023 Adrien Plazas <kekun.plazas@laposte.net>
zlib License, see LICENSE file.
"""

graphics = '''\
{{
    "type": "regular_bg",
    "bpp_mode": "bpp_4_auto",
    "height": {bg_height}
}}
'''

header = '''\
#ifndef {guard}
#define {guard}

#include "bntmx_map.h"

#include <bn_regular_bg_items_{map_name}.h>

namespace bntmx::maps
{{
    class {map_name} : public bntmx::map
    {{
        public:
            enum object_class {object_classes};

            enum object_id {object_ids};

            enum tile_id {tile_ids};

            constexpr {map_name}()
            {{
            }}

            constexpr ~{map_name}()
            {{
            }}

            constexpr bn::size dimensions_in_pixels() const
            {{
                return bn::size({width_in_pixels}, {height_in_pixels});
            }}

            constexpr bn::size dimensions_in_tiles() const
            {{
                return bn::size({width_in_tiles}, {height_in_tiles});
            }}

            constexpr bn::size tile_dimensions() const
            {{
                return bn::size({tile_width}, {tile_height});
            }}

            constexpr int width_in_pixels() const
            {{
                return {width_in_pixels};
            }}

            constexpr int height_in_pixels() const
            {{
                return {height_in_pixels};
            }}

            constexpr int width_in_tiles() const
            {{
                return {width_in_tiles};
            }}

            constexpr int height_in_tiles() const
            {{
                return {height_in_tiles};
            }}

            constexpr int tile_width() const
            {{
                return {tile_width};
            }}

            constexpr int tile_height() const
            {{
                return {tile_height};
            }}

            constexpr int n_graphics_layers() const
            {{
                return {n_graphics_layers};
            }}

            constexpr int n_objects_layers() const
            {{
                return {n_objects_layers};
            }}

            constexpr int n_tiles_layers() const
            {{
                return {n_tiles_layers};
            }}

            constexpr bn::regular_bg_item regular_bg_item() const
            {{
                return bn::regular_bg_items::{map_name};
            }}

            const bntmx::map_object object(int id) const;
            const bn::span<const bntmx::map_object> objects(int objects_layer_index) const;
            const bn::span<const bntmx::map_object> objects(int objects_layer_index, int objects_class) const;
            const bn::span<const bntmx::map_tile> tiles(int tiles_layer_index) const;
    }};
}}

#endif
'''

map_object = 'bntmx::map_object(bn::fixed_point({x}, {y}), {id})'

source = '''\
#include "{header_filename}"

namespace bntmx::maps
{{
    // Objects are sorted by layers, then within layers they are sorted by
    // classes (with classless objects first), then within classes they are
    // sorted in the order they are found.
    // Because object IDs are assigned in the same order, they are also sorted
    // by ID.
    static constexpr bntmx::map_object _objects[] = {objects};

    // This purposefully doesn't use bn::span so we can use smaller types,
    // saving ROM space.
    static constexpr struct {{uint16_t index; uint16_t length;}} _objects_spans[{n_objects_layers}][{n_objects_classes}] = {objects_spans};

    static const bntmx::map_tile _tiles[{n_tiles_layers}][{size}] = {tiles};

    const bntmx::map_object {map_name}::object(int id) const
    {{
        BN_ASSERT(id < {n_objects}, "Invalid object ID: ", id);
        return _objects[id];
    }}

    const bn::span<const bntmx::map_object> {map_name}::objects(int objects_layer_index) const
    {{
        BN_ASSERT(objects_layer_index < {n_objects_layers}, "Invalid objects layer index: ", objects_layer_index);
        return bn::span(&_objects[_objects_spans[objects_layer_index][0].index], _objects_spans[objects_layer_index][0].length);
    }}

    const bn::span<const bntmx::map_object> {map_name}::objects(int objects_layer_index, int objects_class) const
    {{
        BN_ASSERT(objects_layer_index < {n_objects_layers}, "Invalid objects layer index: ", objects_layer_index);
        BN_ASSERT(objects_class < {n_objects_classes}, "Invalid objects class: ", objects_class);
        return bn::span(&_objects[_objects_spans[objects_layer_index][objects_class].index], _objects_spans[objects_layer_index][objects_class].length);
    }}

    const bn::span<const bntmx::map_tile> {map_name}::tiles(int tiles_layer_index) const
    {{
        BN_ASSERT(tiles_layer_index < {n_tiles_layers}, "Invalid tiles layer index: ", tiles_layer_index);
        return bn::span(_tiles[tiles_layer_index], {size});
    }}
}}
'''
