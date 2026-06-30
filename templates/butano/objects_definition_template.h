    // Objects are sorted by layers, then within layers they are sorted by
    // classes (with classless objects first), then within classes they are
    // sorted in the order they are found.
    // Because object IDs are assigned in the same order, they are also sorted
    // by ID.
    static constexpr bntmx::map_object _objects[] = {objects};

    // This purposefully doesn't use bn::span so we can use smaller types,
    // saving ROM space.
    static constexpr struct {{uint16_t index; uint16_t length;}} _objects_spans[{n_objects_layers}][{n_objects_classes}] = {objects_spans};
