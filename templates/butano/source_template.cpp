#include "bntmx_map_items_{map._name}.h"

{data_definitions}

namespace bntmx::map_items
{{
{objects_definition}

{tiles_definition}

    const bntmx::map_object {map._name}::object(int id) const
    {{
        BN_ASSERT(id < {map._objects_count}, "Invalid object ID: ", id);
        return {object_getter};
    }}

    const bn::span<const bntmx::map_object> {map._name}::objects(int objects_layer_index) const
    {{
        BN_ASSERT(objects_layer_index < {map._objects_layers_count}, "Invalid objects layer index: ", objects_layer_index);
        return {objects_getter_classless};
    }}

    const bn::span<const bntmx::map_object> {map._name}::objects(int objects_layer_index, int objects_class) const
    {{
        BN_ASSERT(objects_layer_index < {map._objects_layers_count}, "Invalid objects layer index: ", objects_layer_index);
        BN_ASSERT(objects_class < {map._objects_classes_count}, "Invalid objects class: ", objects_class);
        return {objects_getter_with_class};
    }}

    const bn::span<const bntmx::map_tile> {map._name}::tiles(int tiles_layer_index) const
    {{
        BN_ASSERT(tiles_layer_index < {map._tiles_layers_count}, "Invalid tiles layer index: ", tiles_layer_index);
        return {tiles_getter};
    }}
}}

