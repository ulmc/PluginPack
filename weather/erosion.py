# -*- coding: utf-8 -*-
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#

__author__ = 'stsouko'

import org.bukkit.block.Biome as Biome


class Erosion():
    def __init__(self, world):
        self.world = world

    replace = {130: Biome.ICE_MOUNTAINS,
               Biome.RIVER: 1, Biome.PLAINS: 1, Biome.FOREST: 1,
               Biome.FOREST_HILLS: 0, Biome.EXTREME_HILLS: 0,
               Biome.SMALL_MOUNTAINS: 0, Biome.BEACH: 12}

    def river(self, chunk):
        cx, cz = chunk.getX() * 16, chunk.getZ() * 16
        snap = chunk.getChunkSnapshot()

        for x in xrange(16):
            xx = cx + x
            for z in xrange(16):
                zz = cz + z
                y = snap.getHighestBlockYAt(x, z) - 1
                if self.world.getBiome(xx, zz) not in (Biome.RIVER, Biome.FROZEN_RIVER, Biome.OCEAN, Biome.SWAMPLAND, Biome.JUNGLE, Biome.JUNGLE_HILLS, Biome.BEACH):
                    if self.chkwater(snap, y, x, z):
                        if self.world.getBiome(xx, zz) in (Biome.DESERT, Biome.DESERT_HILLS):
                            self.world.setBiome(xx, zz, Biome.BEACH)
                        else:
                            self.world.setBiome(xx, zz, Biome.RIVER)
                elif self.world.getBiome(xx, zz) in (Biome.RIVER, Biome.FROZEN_RIVER):
                    if not self.chkwater(snap, y, x, z):
                        if y > 130:
                            self.world.setBiome(xx, zz, Biome.ICE_MOUNTAINS)
                        elif y > 90:
                            self.world.setBiome(xx, zz, Biome.FOREST_HILLS)
                        else:
                            self.world.setBiome(xx, zz, Biome.PLAINS)

    def chkwater(self, snap, H, x, z):
        for h in xrange(H, H - 10, -1):
            block = snap.getBlockTypeId(x, h, z)
            if block in (8, 9, 79):
                if snap.getBlockTypeId(x, h - 1, z) in (8, 9, 79):
                    return True
            elif block in (1, 2, 3, 4, 7, 12, 13, 24):
                break
        return False