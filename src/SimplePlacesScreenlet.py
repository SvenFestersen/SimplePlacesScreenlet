#!/usr/bin/env python
#
#       simpleClockScreenlet
#
#       Copyright 2009 Sven Festersen <sven@sven-festersen.de>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.
import datetime
import gtk
import gobject
import os
import screenlets
from screenlets.options import BoolOption
from os import system
import sys
import time

import theme

def get_pixbuf_from_icon_name(name, size):
    """
    Returns a pixbuf from the current icon theme for the icon with
    name and size.
    """
    theme = gtk.icon_theme_get_default()
    try:
        pb = theme.load_icon(name, size, gtk.ICON_LOOKUP_FORCE_SVG)
    except:
        pb = theme.load_icon("unknown", size, gtk.ICON_LOOKUP_FORCE_SVG)
    return pb

def load_bookmarks(size):
    bookmarks = [(os.path.expanduser("~"), os.path.basename(os.path.expanduser("~")), get_pixbuf_from_icon_name("user-home", size)),
                (os.path.expanduser("~/Desktop"), "Desktop", get_pixbuf_from_icon_name("user-desktop", size)),
                ("/", "/", get_pixbuf_from_icon_name("harddrive", size))]
    
    if os.path.exists(os.path.expanduser("~/.gtk-bookmarks")):
        f = open(os.path.expanduser("~/.gtk-bookmarks"), "r")
        data = f.read()
        f.close()
        lines = data.split("\n")
        for line in lines:
            pb = get_pixbuf_from_icon_name("folder", size)
            line = line.strip()
            a = line.split(" ", 1)
            path = line[7:]
            if len(a) == 2: path = a[0][7:]
            if line and line.startswith("file:///") and os.path.exists(path):
                if len(a) == 1:
                    bookmarks.append((path, os.path.basename(line), pb))
                elif len(a) == 2:
                    bookmarks.append((path, a[1], pb))
    
    return bookmarks


class SimplePlacesScreenlet(screenlets.Screenlet):
    """This Screenlet shows a places list."""

    __name__    = 'SimplePlacesScreenlet'
    __version__ = 'Beta'
    __author__  = 'Sven Festersen'
    __desc__    = __doc__

    default_width = 250
    default_height = 300
    _theme_info = None

    def __init__ (self, **keyword_args):
        screenlets.Screenlet.__init__(self, width=self.default_width, height=self.default_height, uses_theme=True, **keyword_args)
        self.theme_name = "BlackSquared"
        
        self._init_list()
        self._load_places()
        
    def _init_list(self):
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.set_border_width(10)
        model = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING, gtk.gdk.Pixbuf) #path, title, icon
        self._treeview = gtk.TreeView(model)
        self._treeview.set_headers_visible(False)
        self._treeview.connect("event-after", self._cb_treeview_event)
        
        renderer = gtk.CellRendererPixbuf()
        col = gtk.TreeViewColumn("", renderer, pixbuf=2)
        col.set_max_width(24)
        self._treeview.append_column(col)
        
        renderer = gtk.CellRendererText()
        col = gtk.TreeViewColumn("", renderer, text=1)
        self._treeview.append_column(col)
        
        sw.add(self._treeview)
        self.window.add(sw)
        self.window.show_all()
        
    def _load_places(self):
        places = load_bookmarks(16)
        model = self._treeview.get_model()
        model.clear()
        
        for path, title, pixbuf in places:
            model.set(model.append(None), 0, path, 1, title, 2, pixbuf)
            
    def _cb_treeview_event(self, widget, event):
        if event.type == gtk.gdk._2BUTTON_PRESS:
            selection = widget.get_selection()
            if selection.count_selected_rows() == 1:
                (model, iter) = selection.get_selected()
                path = model.get_value(iter, 0)
                system('xdg-open "%s"' % path)
    
    def on_init(self):
        self.add_default_menuitems()
        gobject.timeout_add(2500, self._update)
        
    def on_load_theme(self):
        self._theme_info = theme.ThemeInfo(self.theme.path + "/theme.conf")

    def on_draw(self, ctx):
        ctx.scale(self.scale, self.scale)
        self._theme_info.draw_background(ctx, self.default_width, self.default_height, self.scale)
        
    def on_draw_shape (self, ctx):
        if self._theme_info:
            self.on_draw(ctx)
            
    def _update(self):
        self._load_places()
        return True

if __name__ == '__main__':
    import screenlets.session
    screenlets.session.create_session(SimplePlacesScreenlet)
