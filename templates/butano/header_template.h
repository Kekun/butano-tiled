#ifndef {guard}
#define {guard}

#include "bntmx.h"

{graphics_include}

namespace bntmx::maps
{{

class {map_name} : public bntmx::map
{{

public:
{objects_classes_definition}
{object_ids_definition}
{tile_ids_definition}
    constexpr {map_name}() {{}}
    constexpr ~{map_name}() {{}}

    constexpr bn::size dimensions_in_pixels() const {{ return bn::size({width_in_pixels}, {height_in_pixels}); }}
    constexpr bn::size dimensions_in_tiles() const {{ return bn::size({width_in_tiles}, {height_in_tiles}); }}
    constexpr bn::size tile_dimensions() const {{ return bn::size({tile_width}, {tile_height}); }}
    constexpr int width_in_pixels() const {{ return {width_in_pixels}; }}
    constexpr int height_in_pixels() const {{ return {height_in_pixels}; }}
    constexpr int width_in_tiles() const {{ return {width_in_tiles}; }}
    constexpr int height_in_tiles() const {{ return {height_in_tiles}; }}
    constexpr int tile_width() const {{ return {tile_width}; }}
    constexpr int tile_height() const {{ return {tile_height}; }}
    constexpr int n_graphics_layers() const {{ return {graphics_layers_count}; }}
    constexpr int n_objects_layers() const {{ return {objects_layers_count}; }}
    constexpr int n_tiles_layers() const {{ return {tiles_layers_count}; }}
    constexpr std::variant<std::monostate, bn::regular_bg_item, bn::affine_bg_item> graphics() const {{ return {graphics}; }}

    const bntmx::map_object object(int id) const;
    const bn::span<const bntmx::map_object> objects(int objects_layer_index) const;
    const bn::span<const bntmx::map_object> objects(int objects_layer_index, int objects_class) const;
    const bn::span<const bntmx::map_tile> tiles(int tiles_layer_index) const;

}};

}}

#endif
