#include "{header_filename}"

#include <assert.h>

{objects_definition}

{tiles_definition}

const bntmx_map_object bntmx_maps_{map_name}_object(int id)
{{
    assert(id < {objects_count});
    return {object_getter};
}}

const bntmx_span bntmx_maps_{map_name}_objects(int objects_layer_index, int objects_class)
{{
    assert(objects_layer_index < {objects_layers_count});
    assert(objects_class < {objects_classes_count});
    return {objects_getter_with_class};
}}

const bntmx_span bntmx_maps_{map_name}_tiles(int tiles_layer_index)
{{
    assert(tiles_layer_index < {tiles_layers_count});
    return {tiles_getter};
}}

