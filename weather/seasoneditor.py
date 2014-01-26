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

from java.lang import Runnable
from random import randint, sample
from math import ceil
from time import strftime

import org.bukkit.block.Biome as Biome


class SeasonEditor(Runnable):
    def __init__(self, world, months):
        self.months = months
        self.world = world

    hot = (Biome.RIVER, Biome.PLAINS, Biome.FOREST, Biome.FOREST_HILLS, Biome.EXTREME_HILLS,
           Biome.SMALL_MOUNTAINS)

    cold = (Biome.FROZEN_RIVER, Biome.ICE_PLAINS, Biome.TAIGA, Biome.TAIGA_HILLS, Biome.ICE_MOUNTAINS)

    replace = {Biome.FROZEN_RIVER: Biome.RIVER, Biome.ICE_PLAINS: Biome.PLAINS, Biome.TAIGA: Biome.FOREST,
               Biome.TAIGA_HILLS: Biome.FOREST_HILLS, Biome.ICE_MOUNTAINS: Biome.EXTREME_HILLS,
               Biome.RIVER: Biome.FROZEN_RIVER, Biome.PLAINS: Biome.ICE_PLAINS, Biome.FOREST: Biome.TAIGA,
               Biome.FOREST_HILLS: Biome.TAIGA_HILLS, Biome.EXTREME_HILLS: Biome.ICE_MOUNTAINS,
               Biome.SMALL_MOUNTAINS: Biome.ICE_MOUNTAINS}

    def seasons(self, times):
        if self.months[times] in (2, 1):
            self.editor = self.winterise
            return self.hot
        else:
            self.editor = self.summerise
            return self.cold

    speed = {0: 1., 1: 10., 2: 1., 3: 10.}

    def cells(self, season, cx, cz):
        chunkbiomes = []
        for x in xrange(16):
            xx = cx + x
            for z in xrange(16):
                zz = cz + z
                biome = self.world.getBiome(xx, zz)
                if biome in season:
                    chunkbiomes += [(biome, xx, zz, x, z)]
        return chunkbiomes

    def summerise(self, shot, x, y, z, xx, zz):
        if 15 < y < randint(129, 134):
            for i in range(y, y - 15, -1):
                if shot.getBlockTypeId(x, i, z) == 78:
                    self.world.getBlockAt(xx, i, zz).setTypeId(0)
                elif shot.getBlockTypeId(x, i - 1, z) == 79:
                    self.world.getBlockAt(xx, i - 1, zz).setTypeId(8)
                    break

    def winterise(self, shot, x, y, z, xx, zz):
        # def ice(H):
        #     if 0 < x < 15 and 0 < z < 15:
        #         for i, j in ((1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1)):
        #             bb = shot.getBlockTypeId(x + i, H, z + j)
        #             if bb == 8 and shot.getBlockData(x + i, H, z + j) == 0:
        #                 self.world.getBlockAt(xx + i, H, zz + j).setTypeId(79)
        #             if bb == 9:
        #                 self.world.getBlockAt(xx + i, H, zz + j).setTypeId(79)

        if 15 < y < 230:
            y1 = shot.getBlockTypeId(x, y - 1, z)
            if y1 == 9:
                self.world.getBlockAt(xx, y - 1, zz).setTypeId(79)
            elif y1 == 8 and shot.getBlockData(x, y - 1, z) == 0:
                self.world.getBlockAt(xx, y - 1, zz).setTypeId(79)
            elif y1 == 18:
                for i in xrange(y - 2, y - 25, -1):
                    y2 = shot.getBlockTypeId(x, i, z)
                    if y2 not in (18, 0, 17):
                        if y2 == 9:
                            self.world.getBlockAt(xx, i, zz).setTypeId(79)
                        elif y2 == 8 and shot.getBlockData(x, i, z) == 0:
                            self.world.getBlockAt(xx, i, zz).setTypeId(79)
                        break
            elif shot.getBlockTypeId(x, y, z) == 0:
                # def glass():
                #     for j in range(y + 1, y + 25):
                #         if shot.getBlockTypeId(x, j, z) != 0:
                #             return False
                #     return True
                #
                # if glass():
                self.world.getBlockAt(xx, y, zz).setTypeId(78)

    def change(self, chunk):
        cx, cz = chunk.getX() * 16, chunk.getZ() * 16
        times = int(strftime('%w'))
        season = self.seasons(times)
        chunkbiomes = self.cells(season, cx, cz)

        if chunkbiomes:
            b = True
            shot = chunk.getChunkSnapshot(b, b, b)
            for i in sample(chunkbiomes, int(ceil(len(chunkbiomes) / self.speed[self.months[times]]))):
                self.world.setBiome(i[1], i[2], self.replace[i[0]])
                y = shot.getHighestBlockYAt(i[3], i[4])
                self.editor(shot, i[3], y, i[4], i[1], i[2])

    def run(self):
        chunks = self.world.getLoadedChunks()
        for chunk in chunks:
            self.change(chunk)

