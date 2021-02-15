# -*- coding: utf-8 -*-
"""
/***************************************************************************
 opeNoise

 Qgis Plugin to compute noise levels

                             -------------------
        begin                : February 2019
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

from qgis.core import QgsProject, QgsMapLayerProxyModel
import processing
from qgis.PyQt import QtCore
from PyQt5 import QtGui, uic
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog

import os
import sys

from . import on_CreateGrid, on_Settings

ui_path = os.path.join(
    os.path.dirname(__file__),
    'ui_CreateGrid.ui'
)

FORM_CLASS, _ = uic.loadUiType(ui_path, resource_suffix='')


class Dialog(QDialog, FORM_CLASS):
        
    def __init__(self, iface):
        QDialog.__init__(self, iface.mainWindow())
        self.iface = iface 
        self.setupUi(self)
        self.populate_overlayLayer()
        self.populate_layerList()
        self.populate_layerTOrasterize()
        self.gridSave_pushButton.clicked.connect(self.outputFile_grid)
        self.rasterSave_pushButton.clicked.connect(self.outputFile_raster)
        self.runGrid_pushButton.clicked.connect(self.runGrid)
        self.runRaster_pushButton.clicked.connect(self.runRasterize)
       
        pixel_spacing = ['5', '10','20','30','40','50']
        self.resolution_comboBox.clear()
        for pixel in pixel_spacing:
            self.resolution_comboBox.addItem(pixel)


    def populate_overlayLayer(self):

        self.overlayLayer_ComboBox.clear()
        self.overlayLayer_ComboBox.setFilters(QgsMapLayerProxyModel.VectorLayer) 
    

    def populate_layerTOrasterize(self):

        self.layerTOrasterize_ComboBox.clear()
        self.layerTOrasterize_ComboBox.setFilters(QgsMapLayerProxyModel.VectorLayer)


    def populate_layerList(self):

        self.layerList_ComboBox.clear()
        self.layerList_ComboBox.setFilters(QgsMapLayerProxyModel.VectorLayer) 


    def outputFile_grid(self):
        
        self.gridpoint_lineEdit.clear()
        self.fileName = QFileDialog.getSaveFileName(
            None, 
            'Open file', 
            on_Settings.getOneSetting('directory_last') , 
            "Shapefile (*.shp);;All files (*)")

        if self.fileName is None or self.fileName == "":
            return
            
        if str.find(self.fileName[0],".shp") == -1 and str.find(self.fileName[0],".SHP") == -1:
            self.gridpoint_lineEdit.setText( self.fileName[0] + ".shp")
        else:
            self.gridpoint_lineEdit.setText( self.fileName[0])
       
        pathFile = on_Settings.setOneSetting('directory_last', 
            os.path.dirname(self.gridpoint_lineEdit.text()))


    def outputFile_raster(self):

        self.raster_lineEdit.clear()
        self.fileName = QFileDialog.getSaveFileName(
            None, 
            'Open file', 
            on_Settings.getOneSetting('directory_last') , 
            "Raster (*.tif);;All files (*)")

        if self.fileName is None or self.fileName == "":
            return
            
        if str.find(self.fileName[0],".tif") == -1 and str.find(self.fileName[0],".TIF") == -1:
            self.raster_lineEdit.setText( self.fileName[0] + ".tif")
        else:
            self.raster_lineEdit.setText( self.fileName[0])
       
        pathFile = on_Settings.setOneSetting('directory_last', 
            os.path.dirname(self.raster_lineEdit.text()))

            
    def runGrid(self):
               
        resolution = int(self.resolution_comboBox.currentText())
        overlay_layer = self.overlayLayer_ComboBox.currentLayer()
        overlay_layer_path = overlay_layer.source()
        grid_path = self.gridpoint_lineEdit.text()

        on_CreateGrid.creategrid(resolution, overlay_layer_path, grid_path)

        
    def runRasterize(self):
        
        resolution = int(self.resolution_comboBox.currentText())
        layerTorasterize = self.layerTOrasterize_ComboBox.currentLayer()
        layerTorasterize_path = layerTorasterize.source()
        field = self.fieldsLayer_ComboBox.currentText()
        raster_path = self.raster_lineEdit.text()

        on_CreateGrid.createRaster(resolution, layerTorasterize_path, field, raster_path)

        self.close()

