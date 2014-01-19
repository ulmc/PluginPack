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
__plugin_name__ = "UlmcRP-weather"
__plugin_version__ = "0.2"
__plugin_mainclass__ = "ulmc"

from boiler import Logger

from java.lang import Runnable
from java.io import File
from time import strftime
from random import randint, sample
from math import ceil
import org.bukkit.Bukkit as Bukkit
import org.bukkit.block.Biome as Biome

server = Bukkit.getServer()
logs = Logger(__plugin_name__)


class SeasonEditor(Runnable):
    def __init__(self, months):
        self.months = months
        self.world = server.getWorld('world')

    hot = (Biome.RIVER, Biome.PLAINS, Biome.FOREST, Biome.FOREST_HILLS, Biome.EXTREME_HILLS,
           Biome.SMALL_MOUNTAINS, Biome.BEACH)

    cold = (Biome.FROZEN_RIVER, Biome.ICE_PLAINS, Biome.TAIGA, Biome.TAIGA_HILLS, Biome.ICE_MOUNTAINS)

    replace = {Biome.FROZEN_RIVER: Biome.RIVER, Biome.ICE_PLAINS: Biome.PLAINS, Biome.TAIGA: Biome.FOREST,
               Biome.TAIGA_HILLS: Biome.FOREST_HILLS, Biome.ICE_MOUNTAINS: Biome.EXTREME_HILLS,
               Biome.RIVER: Biome.FROZEN_RIVER, Biome.PLAINS: Biome.ICE_PLAINS, Biome.FOREST: Biome.TAIGA,
               Biome.FOREST_HILLS: Biome.TAIGA_HILLS, Biome.EXTREME_HILLS: Biome.ICE_MOUNTAINS,
               Biome.SMALL_MOUNTAINS: Biome.ICE_MOUNTAINS, Biome.BEACH: Biome.ICE_PLAINS}

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
            for z in xrange(16):
                xx, zz = cx + x, cz + z
                biome = self.world.getBiome(xx, zz)
                if biome in season:
                    chunkbiomes += [(biome, xx, zz, x, z)]
        return chunkbiomes

    def summerise(self, shot, x, y, z, xx, zz):
        if shot.getBlockTypeId(x, y, z) == 78 and y < randint(129, 134):
            self.world.getBlockAt(xx, y, zz).setTypeId(0)
        elif shot.getBlockTypeId(x, y - 1, z) == 79 and y < randint(129, 131):
            self.world.getBlockAt(xx, y - 1, zz).setTypeId(9)

    def winterise(self, shot, x, y, z, xx, zz):
        if shot.getBlockTypeId(x, y - 1, z) == 9 and shot.getBlockData(x, y - 1, z) == 0:
            self.world.getBlockAt(xx, y - 1, zz).setTypeId(79)
        elif shot.getBlockTypeId(x, y, z) == 0 and shot.getBlockTypeId(x, y - 1, z) not in (9, 8):
            def glass():
                for j in range(y + 1, 255):
                    if shot.getBlockTypeId(x, j, z) != 0:
                        return False
                return True

            if glass():
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


class NewChunkTimer(Runnable):
    def __init__(self):
        self.world = server.getWorld('world')
        self.chunks = []

    def add(self, chunk):
        self.chunks += [[chunk.getX(), chunk.getZ(), 2]]

    def run(self):
        for chunk in self.chunks:
            if chunk[2] == 0:
                timer.change(self.world.getChunkAt(chunk[0], chunk[1]))
                self.chunks.remove(chunk)
            else:
                chunk[2] -= 1


def savedata():
    if not pyplugin.dataFolder.exists():
        pyplugin.dataFolder.mkdirs()
    f = open(File(pyplugin.dataFolder, "config").getCanonicalPath(), "w")
    f.write('\n'.join(("%d:%d" % (x, y) for x, y in timer.months.items())))
    f.close()


def loaddata():
    filepath = File(pyplugin.dataFolder, "config")
    months = {0: 0, 1: 1, 2: 2, 3: 2, 4: 3, 5: 0, 6: 0}
    if filepath.exists():
        for line in open(filepath.getCanonicalPath()):
            data = line.strip().split(':')
            try:
                if int(data[0]) in months:
                    months[int(data[0])] = int(data[1])
            except:
                logs.info("error in configfile")
    return months


@hook.enable
def onEnable():
    global timer, newchunktimer
    timer = SeasonEditor(loaddata())
    newchunktimer = NewChunkTimer()
    server.getScheduler().scheduleSyncRepeatingTask(pyplugin, timer, 2000, 20 * 60 * 20)
    server.getScheduler().scheduleSyncRepeatingTask(pyplugin, newchunktimer, 100, 20 * 5)
    logs.info("enabled")


@hook.disable
def onDisable():
    savedata()
    logs.info("disabled")


@hook.event("world.ChunkLoadEvent", "normal")
def onloadchunk(event):
    if not event.isNewChunk():
        chunk = event.getChunk()
        timer.change(chunk)
    else:
        newchunktimer.add(event.getChunk())
    return True


@hook.command("seasonrep")
def onSRCommand(sender, args):
    name = sender.getName()
    if name == "CONSOLE":
        timer.run()
    else:
        chunk = sender.getLocation().getChunk()
        timer.change(chunk)
        logs.msg(sender, "chunk's season repared")
    return True


@hook.command("seasonedit")
def onSECommand(sender, args):
    rep = {"w": 2, "s": 0, "p": 3, "a": 1}
    if args[0][0] in rep:
        timer.months[int(strftime('%w'))] = rep[args[0][0]]
        logs.msg(sender, "season edited")
    return True
