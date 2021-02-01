# -*- coding: utf-8 -*-
"""
/***************************************************************************
 opeNoise

 Qgis Plugin to compute noise levels

                             -------------------
        begin                : January 2021
        copyright            : (C) 2019 by Arpa Piemonte
        email                : s.masera@arpa.piemonte.it
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


from qgis.core import QgsProject
from qgis import processing


def creategrid(layer, hpace, vpace):
    
    project = QgsProject.instance()

    crs_layer = layer.crs().authid()
    
    extent = layer.extent()
    xmax = extent.xMaximum()
    ymax = extent.yMaximum()
    xmin = extent.xMinimum()
    ymin = extent.yMinimum()

    extent_coords = "%f,%f,%f,%f" %(xmin, xmax, ymin, ymax) 

    params = { 'CRS' : crs_layer,
    'EXTENT' : extent_coords, 
    'HOVERLAY' : 0, 
    'HSPACING' : hpace, 
    'OUTPUT' : 'TEMPORARY_OUTPUT', 
    'TYPE' : 0, 
    'VOVERLAY' : 0, 
    'VSPACING' : vpace }

    processing.runAndLoadResults("native:creategrid", params)
