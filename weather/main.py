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
from seasoneditor import SeasonEditor

from java.lang import Runnable
from java.io import File
from time import strftime

import org.bukkit.Bukkit as Bukkit

server = Bukkit.getServer()
logs = Logger(__plugin_name__)


class NewChunkTimer(Runnable):
    def __init__(self, world):
        self.world = world
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
    world = server.getWorld('world')
    global timer, newchunktimer
    timer = SeasonEditor(world, loaddata())
    newchunktimer = NewChunkTimer(world)
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
