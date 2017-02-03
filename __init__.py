# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SerialPrint
                                 A QGIS plugin
 Adds each layer from a series of layers to a print composer and exports the latter.
                             -------------------
        begin                : 2017-02-03
        copyright            : (C) 2017 by Stefan Blumentrath - Norwegian Institute for Nature Research
        email                : stefan.blumentrath@nina.no
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load SerialPrint class from file SerialPrint.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .serial_print import SerialPrint
    return SerialPrint(iface)
