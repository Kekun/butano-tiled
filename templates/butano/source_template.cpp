#include "{header_filename}"

namespace bntmx::maps
{{
{objects_definition}

{tiles_definition}

    const bntmx::map_object {map_name}::object(int id) const
    {{
        BN_ASSERT(id < {n_objects}, "Invalid object ID: ", id);
        return {object_getter};
    }}

    const bn::span<const bntmx::map_object> {map_name}::objects(int objects_layer_index) const
    {{
        BN_ASSERT(objects_layer_index < {n_objects_layers}, "Invalid objects layer index: ", objects_layer_index);
        return {objects_getter_classless};
    }}

    const bn::span<const bntmx::map_object> {map_name}::objects(int objects_layer_index, int objects_class) const
    {{
        BN_ASSERT(objects_layer_index < {n_objects_layers}, "Invalid objects layer index: ", objects_layer_index);
        BN_ASSERT(objects_class < {n_objects_classes}, "Invalid objects class: ", objects_class);
        return {objects_getter_with_class};
    }}

    const bn::span<const bntmx::map_tile> {map_name}::tiles(int tiles_layer_index) const
    {{
        BN_ASSERT(tiles_layer_index < {n_tiles_layers}, "Invalid tiles layer index: ", tiles_layer_index);
        return {tiles_getter};
    }}
}}

