#ifndef {guard}
#define {guard}

#include "bntmx.h"

{graphics_include}

namespace bntmx::maps
{{

class {map._name} : public bntmx::map
{{

public:
{objects_classes_definition}
{object_ids_definition}
{tile_ids_definition}
    constexpr {map._name}() {{}}
    constexpr ~{map._name}() {{}}

    constexpr bn::size dimensions_in_pixels() const {{ return bn::size({map._width_in_pixels}, {map._height_in_pixels}); }}
    constexpr bn::size dimensions_in_tiles() const {{ return bn::size({map._width_in_tiles}, {map._height_in_tiles}); }}
    constexpr bn::size tile_dimensions() const {{ return bn::size({map._tile_width}, {map._tile_height}); }}
    constexpr int width_in_pixels() const {{ return {map._width_in_pixels}; }}
    constexpr int height_in_pixels() const {{ return {map._height_in_pixels}; }}
    constexpr int width_in_tiles() const {{ return {map._width_in_tiles}; }}
    constexpr int height_in_tiles() const {{ return {map._height_in_tiles}; }}
    constexpr int tile_width() const {{ return {map._tile_width}; }}
    constexpr int tile_height() const {{ return {map._tile_height}; }}
    constexpr int n_graphics_layers() const {{ return {map._graphics_layers_count}; }}
    constexpr int n_objects_layers() const {{ return {map._objects_layers_count}; }}
    constexpr int n_tiles_layers() const {{ return {map._tiles_layers_count}; }}
    constexpr std::variant<std::monostate, bn::regular_bg_item, bn::affine_bg_item> graphics() const {{ return {graphics}; }}

    const bntmx::map_object object(int id) const;
    const bn::span<const bntmx::map_object> objects(int objects_layer_index) const;
    const bn::span<const bntmx::map_object> objects(int objects_layer_index, int objects_class) const;
    const bn::span<const bntmx::map_tile> tiles(int tiles_layer_index) const;

}};

}}

#endif
