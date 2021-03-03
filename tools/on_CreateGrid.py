import os

from PyQt5.QtCore import QVariant
from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsFeature,
    QgsField,
    QgsFields,
    QgsRasterLayer,
    QgsWkbTypes,
    QgsVectorFileWriter
)

from qgis.utils import iface
from qgis import processing


def createGrid(resolution, overlay_layer_path, grid_path):
    project = QgsProject.instance()

    overlay_layer_name = os.path.splitext(
        os.path.basename(overlay_layer_path))[0]

    overlay_layer = QgsVectorLayer(
        overlay_layer_path,
        overlay_layer_name,
        "ogr")

    crs_layer = overlay_layer.crs().authid()

    extent = iface.mapCanvas().extent()
    xmax = extent.xMaximum()
    ymax = extent.yMaximum()
    xmin = extent.xMinimum()
    ymin = extent.yMinimum()
    extent_coords = "%f,%f,%f,%f" % (xmin, xmax, ymin, ymax)

    # native:creategrid
    params_creategrid = {
        'CRS': crs_layer,
        'EXTENT': extent_coords,
        'HOVERLAY': 0,
        'HSPACING': resolution,
        'OUTPUT': 'memory:',
        'TYPE': 0,
        'VOVERLAY': 0,
        'VSPACING': resolution
    }

    result_grid = processing.run("native:creategrid", params_creategrid)
    grid_output = result_grid['OUTPUT']

    # native:difference
    params_difference = {
        'INPUT': grid_output,
        'OUTPUT': 'memory:',
        'OVERLAY': overlay_layer
    }

    result_difference = processing.run("native:difference", params_difference)
    difference_output = result_difference['OUTPUT']

    # native:multipart to single partS
    params_multiTosingle = {
        'INPUT': difference_output,
        'OUTPUT': 'memory:',
    }

    result_multiTOsingle = processing.run("native:multiparttosingleparts", params_multiTosingle)
    output_singlepart = result_multiTOsingle['OUTPUT']


    writer = QgsVectorFileWriter.writeAsVectorFormat(
        output_singlepart,
        grid_path,
        'utf-8',
        driverName='ESRI Shapefile',
        filterExtent=output_singlepart.extent()
    )

    grid_layer = iface.addVectorLayer(
        grid_path,
        '',
        'ogr'
    )

    fieldsTOdelete = grid_layer.attributeList()

    pr = grid_layer.dataProvider()

    pr.deleteAttributes(fieldsTOdelete[1:5])

    grid_layer.updateFields()


def createRaster(resolution, layerTOrasterize_path, field, raster_path):
    project = QgsProject.instance()

    layerTOrasterize_name = os.path.splitext(
        os.path.basename(layerTOrasterize_path))[0]

    layerTOrasterize = QgsVectorLayer(
        layerTOrasterize_path,
        layerTOrasterize_name,
        "ogr"
    )

    extent = layerTOrasterize.extent()
    xmax = extent.xMaximum()
    ymax = extent.yMaximum()
    xmin = extent.xMinimum()
    ymin = extent.yMinimum()
    extent_coords = "%f,%f,%f,%f" % (xmin, xmax, ymin, ymax)

    params_rasterize = {
        'BURN': 0,
        'DATA_TYPE': 5,
        'EXTENT': extent_coords,
        'EXTRA': '',
        'FIELD': field,
        'HEIGHT': resolution,
        'INIT': None,
        'INPUT': layerTOrasterize,
        'INVERT': False,
        'NODATA': 0,
        'OPTIONS': '',
        'OUTPUT': raster_path,
        'UNITS': 1,
        'WIDTH': resolution
    }

    result_rasterize = processing.run("gdal:rasterize", params_rasterize)
    rasterize_output = result_rasterize['OUTPUT']

    raster_name = os.path.splitext(
        os.path.basename(raster_path))[0]

    raster_layer = QgsRasterLayer(
        rasterize_output,
        raster_name
    )

    project.addMapLayer(raster_layer)


def createContour(raster_path, interval, contour_path):
    project = QgsProject.instance()

    raster_name = os.path.splitext(
        os.path.basename(raster_path))[0]

    raster = QgsRasterLayer(
        raster_path,
        raster_name,
        "gdal"
    )

    params_contour = {
        'BAND': 1,
        'CREATE_3D': False,
        'EXTRA': '',
        'FIELD_NAME': 'gen',
        'IGNORE_NODATA': False,
        'INPUT': raster,
        'INTERVAL': interval,
        'NODATA': None,
        'OFFSET': 0,
        'OUTPUT': contour_path
    }

    result_contour = processing.run("gdal:contour", params_contour)
    contour_output = result_contour['OUTPUT']

    contour_name = os.path.splitext(
        os.path.basename(contour_path))[0]

    contour_layer = QgsVectorLayer(
        contour_output,
        contour_name
    )

    project.addMapLayer(contour_layer)


def polygonize(raster_path, minimum, maximum, interval, poly_path):
    project = QgsProject.instance()

    raster_name = os.path.splitext(
        os.path.basename(raster_path))[0]

    raster = QgsRasterLayer(
        raster_path,
        raster_name,
        "gdal"
    )

    # native: reclassify by table
    table = []
    for i in range(minimum, maximum, interval):
        i += interval
        value = (minimum + i) / 2
        fillTbl = [minimum, i, value]
        table.extend(fillTbl)
        minimum += interval
    
    parameter_reclaBYtbl = { 
    'DATA_TYPE' : 5, 
    'INPUT_RASTER' : raster, 
    'NODATA_FOR_MISSING' : False, 
    'NO_DATA' : -9999, 
    'OUTPUT' : 'TEMPORARY_OUTPUT', 
    'RANGE_BOUNDARIES' : 3, 
    'RASTER_BAND' : 1, 
    'TABLE' : table 
    }

    result_reclas = processing.run("native:reclassifybytable", parameter_reclaBYtbl)
    reclas_output = result_reclas['OUTPUT']


    # gdal: polygonize
    parameter_poly = { 
    'BAND' : 1, 
    'EIGHT_CONNECTEDNESS' : False, 
    'EXTRA' : '', 
    'FIELD' : 'DN', 
    'INPUT' : reclas_output,
    'OUTPUT' : poly_path 
    }

    result_poly = processing.run("gdal:polygonize", parameter_poly)
    poly_output = result_poly['OUTPUT']

    poly_name = os.path.splitext(
        os.path.basename(poly_path))[0]

    poly_layer = QgsVectorLayer(
        poly_path,
        poly_name
    )

    project.addMapLayer(poly_layer)