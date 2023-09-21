/*
 * Copyright (c) 2023 Adrien Plazas <kekun.plazas@laposte.net>
 * zlib License, see LICENSE file.
 */

#ifndef BNTMX_MAP_OBJECT_H
#define BNTMX_MAP_OBJECT_H

#include <bn_fixed_point.h>

namespace bntmx
{

struct map_object
{
    bn::fixed_point position;
    int id;
};

}

#endif
