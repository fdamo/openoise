from qgis.core import (QgsProject, QgsVectorLayer, QgsVectorFileWriter,
                        QgsFeature, QgsField, QgsFields, 
                        QgsRasterLayer, QgsWkbTypes)
from qgis.utils import iface
from qgis import processing
from PyQt5.QtCore import QVariant

import os


def creategrid(resolution, overlay_layer_path, raster_path):
    
    project = QgsProject.instance()
    crs_project = project.crs().authid()
    
    overlay_layer_name = os.path.splitext(
        os.path.basename(overlay_layer_path))[0]
    overlay_layer = QgsVectorLayer(
        overlay_layer_path, 
        overlay_layer_name, 
        "ogr")   
    
    extent = iface.mapCanvas().extent()
    xmax = extent.xMaximum()
    ymax = extent.yMaximum()
    xmin = extent.xMinimum()
    ymin = extent.yMinimum()
    extent_coords = "%f,%f,%f,%f" %(xmin, xmax, ymin, ymax)           

    # native:creategrid
    params_creategrid = { 'CRS' : crs_project,
       'EXTENT' : extent_coords, 
       'HOVERLAY' : 0, 
       'HSPACING' : resolution, 
       'OUTPUT' : 'memory:', 
       'TYPE' : 0, 
       'VOVERLAY' : 0, 
       'VSPACING' : resolution }

    result_grid = processing.run("native:creategrid", params_creategrid)
    grid_output = result_grid['OUTPUT']

    # native:difference
    params_difference = { 'INPUT' : grid_output,
        'OUTPUT' : 'memory:', 
        'OVERLAY' : overlay_layer }
    
    result_difference =  processing.run("native:difference", params_difference)
    difference_output = result_difference['OUTPUT']

    # gdal:rasterize
    params_rasterize = {'BURN' : 0, 
        'DATA_TYPE' : 5, 
        'EXTENT' : extent_coords, 
        'EXTRA' : '', 
        'FIELD' : 'id', 
        'HEIGHT' : resolution, 
        'INIT' : None, 
        'INPUT' : difference_output, 
        'INVERT' : False, 
        'NODATA' : 0, 
        'OPTIONS' : '', 
        'OUTPUT' : raster_path, 
        'UNITS' : 1, 
        'WIDTH' : resolution }

    result_rasterize = processing.run("gdal:rasterize", params_rasterize)
    rasterize_output = result_rasterize['OUTPUT']

    raster_name = os.path.splitext(os.path.basename(raster_path))[0]  
    raster_layer = QgsRasterLayer(rasterize_output, raster_name)
    
    project.addMapLayer(raster_layer)
    
