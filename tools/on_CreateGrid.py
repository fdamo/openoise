from qgis.core import (QgsProject, QgsVectorLayer, QgsVectorFileWriter)
from qgis.utils import iface
from qgis import processing

import os
from qgis._core import QgsFeature, QgsField, QgsFields, QgsWkbTypes
from PyQt5.QtCore import QVariant



def creategrid(pace, buildings_layer_path, grid_point_path):
    
    project = QgsProject.instance()

    crs_project = project.crs().authid()
    
    extent = iface.mapCanvas().extent()

    xmax = extent.xMaximum()
    ymax = extent.yMaximum()
    xmin = extent.xMinimum()
    ymin = extent.yMinimum()

    extent_coords = "%f,%f,%f,%f" %(xmin, xmax, ymin, ymax)           

    params_creategrid = { 'CRS' : crs_project,
       'EXTENT' : extent_coords, 
       'HOVERLAY' : 0, 
       'HSPACING' : pace, 
       'OUTPUT' : 'TEMPORARY_OUTPUT', 
       'TYPE' : 0, 
       'VOVERLAY' : 0, 
       'VSPACING' : pace }

    result_grid = processing.run("native:creategrid", params_creategrid)

    grid_points = result_grid['OUTPUT']

    buildings_layer_name = os.path.splitext(
        os.path.basename(buildings_layer_path))[0]

    buildings_layer = QgsVectorLayer(
        buildings_layer_path, 
        buildings_layer_name, 
        "ogr")

    params_difference = { 'INPUT' : grid_points,
        'OUTPUT' : 'memory:', 
        'OVERLAY' : buildings_layer }
    
    result_difference =  processing.run("native:difference", params_difference)

    difference_output = result_difference['OUTPUT']
    
    QgsVectorFileWriter.writeAsVectorFormat(difference_output, 
                                            grid_point_path, 
                                            "UTF-8", 
                                            difference_output.crs(), 
                                            "ESRI Shapefile")
    
    grid_name = os.path.splitext(os.path.basename(grid_point_path))[0]
    grid = QgsVectorLayer(grid_point_path, str(grid_name), "ogr")

    project.addMapLayer(grid)
    
