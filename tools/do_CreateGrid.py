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

from qgis.core import QgsProject, QgsMapLayerProxyModel
import processing
from qgis.PyQt import QtCore
from PyQt5 import QtGui, uic
from PyQt5.QtWidgets import QDialog, QApplication

import os
import sys

from . import on_CreateGrid 


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
        self.run_pushButton.clicked.connect(self.run)

        
        horizontal_pace = ['10','20','30','40','50']
        self.horizontalPace_comboBox.clear()
        for pace in horizontal_pace:
            self.horizontalPace_comboBox.addItem(pace)

        vertical_pace = ['10','20','30','40','50']
        self.verticalPace_comboBox.clear()
        for pace in vertical_pace:
            self.verticalPace_comboBox.addItem(pace)


  
    def populate_layer( self ):

        self.layer_ComboBox.clear()
        self.layer_ComboBox.setFilters(QgsMapLayerProxyModel.VectorLayer ) 
    

    def run(self):
        
        layer = self.layer_ComboBox.currentLayer()
        hpace = int(self.horizontalPace_comboBox.currentText())
        vpace = int(self.verticalPace_comboBox.currentText())
        

        on_CreateGrid.creategrid(layer, hpace, vpace)


