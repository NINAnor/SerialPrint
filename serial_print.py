# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SerialPrint
                                 A QGIS plugin
 Adds each layer from a series of layers to a print composer and exports the latter.
                              -------------------
        begin                : 2017-02-03
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Stefan Blumentrath - Norwegian Institute for Nature Research
        email                : stefan.blumentrath@nina.no
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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from serial_print_dialog import SerialPrintDialog
import os.path

from qgis.core import *

class SerialPrint:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'SerialPrint_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)


        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Serial print')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'SerialPrint')
        self.toolbar.setObjectName(u'SerialPrint')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('SerialPrint', message)


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
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        # Create the dialog (after translation) and keep reference
        self.dlg = SerialPrintDialog()

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
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/SerialPrint/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Export a composition for each layer'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Serial print'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def run(self):
        """Run method that performs all the real work"""
        # QgsComposerItem.ComposerMap
        # QgsComposerItem.ComposerLegend
        def getCompItemNames(composition, type):
            compItemNames = []
            for i in composition.items():
                if i.type() == type and i.scene():
                    compItemNames.append(i.displayName())
            return compItemNames
        # next
        def getCompItemFromTitle(composition, type, title):
            for i in composition.items():
                if i.type() == type and i.scene() and i.displayName() == title:
                    compItem = i
            return compItem

        # Predefine list of output formats
        output_formats = ['PNG', 'TIF', 'BMP', 'JPG', 'PDF']

        self.dlg.format.clear()
        self.dlg.format.addItems(output_formats)

        # Get available layers
        qlayers = self.iface.legendInterface().layers()
        layer_names = [l.name() for l in qlayers]
        self.dlg.layers.clear()
        self.dlg.layers.addItems(layer_names)

        if len(self.iface.activeComposers()) == 0:
            print 'Error'
        else:
            composers = [c.composerWindow().windowTitle() 
                         for c in self.iface.activeComposers()]
        self.dlg.composer.clear()
        self.dlg.composer.addItems(composers)

        maps = getCompItemNames(self.iface.activeComposers()[0],
                                QgsComposerItem.ComposerMap)
        self.dlg.map.clear()
        self.dlg.map.addItems(maps)

        legends = getCompItemNames(self.iface.activeComposers()[0],
                                   QgsComposerItem.ComposerLegend)
        self.dlg.legend.clear()
        self.dlg.legend.addItems(legends)

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.

            ### Parse user input
            # Composer name from ComboBox
            selectedComposer = self.dlg.composer.currentText()
            print selectedComposer
            slayers = list(self.dlg.layers.selectedItems()) if self.dlg.layers.selectedItems() else None
            layers = []
            for sl in [qsl.text() for qsl in slayers]:
                for ql in qlayers:
                    if sl == ql.name():
                        layers.append(ql) 
            #print slayers
            # 
            # Name of composer map from ComboBox
            composer_map = self.dlg.map.currentText()
            print layers

            # Name of legend from ComboBox
            composer_ledgend = self.dlg.legend.currentText()
            print layers

            # Output directory selected by user
            output_folder = self.dlg.directory.text()
            print output_folder

            # Output prefix given by user
            output_prefix = self.dlg.prefix.text()
            print output_prefix

            # Output format from ComboBox
            output_format = self.dlg.format.currentText()
            print output_format

            # Initialize composition
            for c in self.iface.activeComposers():
                if c.composerWindow().windowTitle() == selectedComposer:
                    comp = c.composition()

            # Initialize counter
            m = 0

            # Not sure which interaction with map canvas is required
            canvas = self.iface.mapCanvas()

            map_item = comp.getComposerItemById(composer_map)
            legend_item = comp.getComposerItemById(composer_ledgend)

            for a in layers:
                self.iface.legendInterface().setLayerVisible(a, False)

            comp.refreshItems()

            # 
            for layer in layers:
                m = m + 1
                self.iface.legendInterface().setLayerVisible(layer, True)
                #comp.refreshItems()
                # Not sure if it is required to set the map canvas
                map_item.setMapCanvas(canvas)
                # map_item.zoomToExtent(canvas.extent())
                #comp.refreshItems()
                # Update legend (remove old layer add new)
                #legend_item.modelV2().rootGroup().addLayer(layer)
                legend_item.modelV2().rootGroup().insertLayer(0, layer)
                legend_item.updateLegend()
                # Refresh composition
                comp.refreshItems()   
                # Write out result
                imageName = output_prefix + '{}.{}'.format(str(m), output_format.lower())
                imagePath = os.path.join(output_folder, imageName)
                if output_format != 'PDF':
                    image = comp.printPageAsRaster(0)
                    image.save(imagePath,output_format)
                else:
                    comp.exportAsPDF(imagePath)
                self.iface.legendInterface().setLayerVisible(layer, False)
                legend_item.modelV2().rootGroup().removeLayer(layer)
                legend_item.updateLegend()
