#include "{header_filename}"

#include <assert.h>

{objects_definition}

{tiles_definition}

const bntmx_map_object bntmx_maps_{map_name}_object(int id)
{{
    assert(id < {n_objects});
    return {object_getter};
}}

const bntmx_span bntmx_maps_{map_name}_objects(int objects_layer_index, int objects_class)
{{
    assert(objects_layer_index < {n_objects_layers});
    assert(objects_class < {n_objects_classes});
    return {objects_getter_with_class};
}}

const bntmx_span bntmx_maps_{map_name}_tiles(int tiles_layer_index)
{{
    assert(tiles_layer_index < {n_tiles_layers});
    return {tiles_getter};
}}

