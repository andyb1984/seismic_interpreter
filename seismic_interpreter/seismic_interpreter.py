# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SeismicInterpreter
                                 A QGIS plugin
 2D SEG-Y Viewer and Horizon Picker for QGIS
 ***************************************************************************/
"""
import importlib
import os.path
from qgis.PyQt.QtCore import QLocale, QTranslator, QCoreApplication, Qt
from qgis.core import QgsSettings
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

from . import seismic_interpreter_dockwidget


class SeismicInterpreter:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor."""
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)

        locale = QgsSettings().value('locale/userLocale', QLocale().name())[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            '{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        self.actions = []
        self.menu = self.tr(u'&Seismic Interpreter')
        self.toolbar = self.iface.addToolBar(u'SeismicInterpreter')
        self.toolbar.setObjectName(u'SeismicInterpreter')

        self.pluginIsActive = False
        self.dockwidget = None

    def tr(self, message):
        return QCoreApplication.translate('SeismicInterpreter', message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(self.menu, action)

        self.actions.append(action)
        return action

    def initGui(self):
        icon_path = os.path.join(os.path.dirname(__file__), 'icon.png')
        self.add_action(
            icon_path,
            text=self.tr(u'Open Seismic Interpreter'),
            callback=self.run,
            parent=self.iface.mainWindow())

    def onClosePlugin(self):
        if self.dockwidget:
            try:
                self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)
            except Exception:
                pass
        self.pluginIsActive = False

    def unload(self):
        for action in self.actions:
            self.iface.removePluginMenu(self.tr(u'&Seismic Interpreter'), action)
            self.iface.removeToolBarIcon(action)

        # Safely teardown resources and unparent before unloading
        if self.dockwidget:
            try:
                self.dockwidget.cleanup_resources()
            except Exception:
                pass
            self.iface.removeDockWidget(self.dockwidget)
            self.dockwidget.deleteLater()
            self.dockwidget = None

        self.pluginIsActive = False

        if hasattr(self, 'toolbar') and self.toolbar:
            del self.toolbar

    def run(self):
        importlib.reload(seismic_interpreter_dockwidget)

        if not self.pluginIsActive or self.dockwidget is None:
            self.pluginIsActive = True

            self.dockwidget = seismic_interpreter_dockwidget.SeismicInterpreterDockWidget(self.iface)
            self.dockwidget.closingPlugin.connect(self.onClosePlugin)

            self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.dockwidget)
            self.dockwidget.show()
        else:
            self.dockwidget.show()
            self.dockwidget.raise_()