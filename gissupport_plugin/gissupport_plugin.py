# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GISSupportPlugin
                                 A QGIS plugin
 Wtyczka GIS Support
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2019-09-03
        git sha              : $Format:%H$
        copyright            : (C) 2019 by GIS Support
        email                : kamil.kozik@gis-support.pl
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import os.path

from PyQt5.QtCore import (QCoreApplication, Qt, QUrl)
from PyQt5.QtGui import QDesktopServices, QIcon
from PyQt5.QtWidgets import QAction
from pathlib import Path
import inspect
from importlib import util

from gissupport_plugin.modules.base import BaseModule
from .key_dialog import GisSupportPluginDialog
from .resources import resources

PLUGIN_NAME = "Wtyczka GIS Support"

class GISSupportPlugin:

    def __init__(self, iface):

        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)

        self.actions = []
        self.modules = []
        self.menu = self.tr(u'&Wtyczka GIS Support')
        self.toolbar = self.iface.addToolBar(PLUGIN_NAME)
        self.toolbar.addSeparator
        
        self.api_key_dialog = GisSupportPluginDialog()
        
    def tr(self, message):
        return QCoreApplication.translate('GISSupportPlugin', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_topmenu=False,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None,
        checkable = False):

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)
        action.setCheckable(checkable)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)
        
        if add_to_topmenu:
            self.topMenu.addAction(action)

        self.actions.append(action)

        return action

    def initModules(self):
        """ Włączenie modułów """

        modules_path = Path( self.plugin_dir ).joinpath('modules')
        #Iteracja po modułach dodatkowych
        for module_name in ['uldk', 'gugik_nmt', 'wms', 'mapster']:
            main_module = modules_path.joinpath(module_name).joinpath('main.py')
            #Załadowanie modułu
            spec = util.spec_from_file_location('main', main_module)
            module = util.module_from_spec(spec)
            spec.loader.exec_module(module)
            #Lista obiektów w module
            clsmembers = inspect.getmembers(module, inspect.isclass)
            for (_, c) in clsmembers:
                # Odrzucamy inne klasy niż dziedziczące po klasie bazowej
                if issubclass(c, BaseModule) and c is not BaseModule:
                    #Aktywacja i rejestracja modułu
                    self.modules.append( c(self) )

    def initGui(self):

        self.topMenu = self.iface.mainWindow().menuBar().addMenu(u'&GIS Support')

        #Load plugin modules
        self.initModules()

        self.topMenu.addSeparator()
        self.topMenu.setObjectName('gisSupportMenu')
        self.add_action(
            icon_path=None,
            text="Klucz GIS Support",
            add_to_menu=False,
            add_to_topmenu=True,
            callback=self.show_api_key_dialog,
            parent=self.iface.mainWindow(),
            add_to_toolbar=False
        )
        self.add_action(
            icon_path=':/plugins/gissupport_plugin/gissupport_small.jpg',
            text="O wtyczce",
            add_to_menu=False,
            add_to_topmenu=True,
            callback=self.open_about,
            parent=self.iface.mainWindow(),
            add_to_toolbar=False
        )

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.menu,
                action)
        #Wyłączenie modułów
        for module in self.modules:
            module.unload()

        self.toolbar.clear()
        self.toolbar.deleteLater()
        self.topMenu.clear()
        self.topMenu.deleteLater()

    def show_api_key_dialog(self):
        self.api_key_dialog.show()

    def open_about(self):
        QDesktopServices.openUrl(QUrl("https://gis-support.pl/wtyczka-gis-support"))
