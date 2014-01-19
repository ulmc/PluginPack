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

from java.util.logging import Level
import org.bukkit.Bukkit as Bukkit


class Logger():
    def __init__(self, plugin_name):
        self.chat_prefix = "[%s] " % plugin_name
        self.logger = Bukkit.getLogger()

    def info(self, *text):
        self.logger.log(Level.INFO, self.chat_prefix + " ".join(map(unicode, text)))

    def severe(self, *text):
        self.logger.log(Level.SEVERE, self.chat_prefix + " ".join(map(unicode, text)))

    def msg(self, recipient, *text):
        recipient.sendMessage(self.chat_prefix + " ".join(map(unicode, text)))
