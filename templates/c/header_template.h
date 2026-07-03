#ifndef {guard}
#define {guard}

#include "bntmx.h"

{object_classes_definition}
{object_ids_definition}
{tile_ids_definition}
#define bntmx_maps_{map_name}_height_in_pixels() ({height_in_pixels})
#define bntmx_maps_{map_name}_width_in_tiles() ({width_in_tiles})
#define bntmx_maps_{map_name}_height_in_tiles() ({height_in_tiles})
#define bntmx_maps_{map_name}_tile_width() ({tile_width})
#define bntmx_maps_{map_name}_tile_height() ({tile_height})
#define bntmx_maps_{map_name}_n_graphics_layers() ({graphics_layers_count})
#define bntmx_maps_{map_name}_n_objects_layers() ({objects_layers_count})
#define bntmx_maps_{map_name}_n_tiles_layers() ({tiles_layers_count})

const bntmx_map_object bntmx_maps_{map_name}_object(int id);
const bntmx_span bntmx_maps_{map_name}_objects(int objects_layer_index, int objects_class);
const bntmx_span bntmx_maps_{map_name}_tiles(int tiles_layer_index);

#endif
