#include "bntmx_maps_{map._name}.h"

#include <assert.h>

{objects_definition}

{tiles_definition}

const bntmx_map_object bntmx_maps_{map._name}_object(int id)
{{
    assert(id < {map._objects_count});
    return {object_getter};
}}

const bntmx_span bntmx_maps_{map._name}_objects(int objects_layer_index, int objects_class)
{{
    assert(objects_layer_index < {map._objects_layers_count});
    assert(objects_class < {map._objects_classes_count});
    return {objects_getter_with_class};
}}

const bntmx_span bntmx_maps_{map._name}_tiles(int tiles_layer_index)
{{
    assert(tiles_layer_index < {map._tiles_layers_count});
    return {tiles_getter};
}}
