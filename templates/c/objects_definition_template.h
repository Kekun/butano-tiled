/* Objects are sorted by layers, then within layers they are sorted by classes
 * (with classless objects first), then within classes they are sorted in the
 * order they are found.
 * Because object IDs are assigned in the same order, they are also sorted by
 * ID.
 */
static const bntmx_map_object _objects[] = {objects};

/* This purposefully doesn't use bntmx_span so we can use smaller types, saving
 * ROM space.
 */
static const struct {{uint16_t index; uint16_t length;}} _objects_spans[{objects_layers_count}][{objects_classes_count}] = {objects_spans};
