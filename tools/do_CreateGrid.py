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
        self.populate_layer()
        self.outputSave_pushButton.clicked.connect(self.outputFile)
        self.run_pushButton.clicked.connect(self.run)
       
        pixel_spacing = ['5', '10','20','30','40','50']
        self.resolution_comboBox.clear()
        for pixel in pixel_spacing:
            self.resolution_comboBox.addItem(pixel)

  
    def populate_layer( self ):

        self.overlayLayer_ComboBox.clear()
        self.overlayLayer_ComboBox.setFilters(QgsMapLayerProxyModel.VectorLayer) 
    

    def outputFile(self):

        self.gridpoint_lineEdit.clear()
        self.fileName = QFileDialog.getSaveFileName(
            None, 
            'Open file', 
            on_Settings.getOneSetting('directory_last') , 
            "Raster (*.tif);;All files (*)")

        if self.fileName is None or self.fileName == "":
            return
            
        if str.find(self.fileName[0],".tif") == -1 and str.find(self.fileName[0],".TIF") == -1:
            self.gridpoint_lineEdit.setText( self.fileName[0] + ".tif")
        else:
            self.gridpoint_lineEdit.setText( self.fileName[0])
       
        pathFile = on_Settings.setOneSetting('directory_last', 
            os.path.dirname(self.gridpoint_lineEdit.text()))

            
    def run(self):
               
        resolution = int(self.resolution_comboBox.currentText())
        overlay_layer = self.overlayLayer_ComboBox.currentLayer()
        overlay_layer_path = overlay_layer.source()
        raster_path = self.gridpoint_lineEdit.text()

        on_CreateGrid.creategrid(resolution, overlay_layer_path, raster_path)

        self.close()

