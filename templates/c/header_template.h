#ifndef BNTMX_MAPS_{map._name_upper}_H
#define BNTMX_MAPS_{map._name_upper}_H

{includes}

{regular_bg_grit_literal}
{regular_bg_literal}
{objects_classes_definition}
{object_ids_definition}
{tile_ids_definition}
#define bntmx_maps_{map._name}_height_in_pixels() ({map._height_in_pixels})
#define bntmx_maps_{map._name}_width_in_tiles() ({map._width_in_tiles})
#define bntmx_maps_{map._name}_height_in_tiles() ({map._height_in_tiles})
#define bntmx_maps_{map._name}_tile_width() ({map._tile_width})
#define bntmx_maps_{map._name}_tile_height() ({map._tile_height})
#define bntmx_maps_{map._name}_n_regular_bg_layers() ({map._regular_bg_layers_count})
#define bntmx_maps_{map._name}_n_objects_layers() ({map._objects_layers_count})
#define bntmx_maps_{map._name}_n_tiles_layers() ({map._tiles_layers_count})

const bntmx_map_object bntmx_maps_{map._name}_object(int id);
const bntmx_span bntmx_maps_{map._name}_objects(int objects_layer_index, int objects_class);
const bntmx_span bntmx_maps_{map._name}_tiles(int tiles_layer_index);

#endif
