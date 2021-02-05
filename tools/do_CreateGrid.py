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

from . import on_CreateGrid , on_Settings


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

        
        paces = ['10','20','30','40','50']
        self.Pace_comboBox.clear()
        for pace in paces:
            self.Pace_comboBox.addItem(pace)

  
    def populate_layer( self ):

        self.layer_ComboBox.clear()
        self.layer_ComboBox.setFilters(QgsMapLayerProxyModel.VectorLayer) 
    

    def outputFile(self):

        self.gridpoint_lineEdit.clear()
        self.shapefileName = QFileDialog.getSaveFileName(
            None, 
            'Open file', 
            on_Settings.getOneSetting('directory_last') , 
            "Shapefile (*.shp);;All files (*)")

        if self.shapefileName is None or self.shapefileName == "":
            return
            
        if str.find(self.shapefileName[0],".shp") == -1 and str.find(self.shapefileName[0],".SHP") == -1:
            self.gridpoint_lineEdit.setText( self.shapefileName[0] + ".shp")
        else:
            self.gridpoint_lineEdit.setText( self.shapefileName[0])
       
        pathFile = on_Settings.setOneSetting('directory_last', 
            os.path.dirname(self.gridpoint_lineEdit.text()))

            
    def run(self):
               
        pace = int(self.Pace_comboBox.currentText())
        buildings_layer = self.layer_ComboBox.currentLayer()
        buildings_layer_path = buildings_layer.source()

        grid_point_path = self.gridpoint_lineEdit.text()
        # buildings_layer_path = buildings_layer.source()
        

        on_CreateGrid.creategrid(pace, buildings_layer_path, grid_point_path)


