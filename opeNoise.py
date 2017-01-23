# -*- coding: utf-8 -*-
"""
/***************************************************************************
 opeNoise

 opeNoise allows to compute the noise level generated by point source or 
 by road source at fixed receiver points and buildings.

                             -------------------
        begin                : March 2014
        copyright            : (C) 2014 by Arpa Piemonte
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
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
import os.path, sys

# Set up current path, so that we know where to look for mudules
currentPath = os.path.dirname(__file__)
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/tools'))

import do_PointSourceCalculation,do_CreateReceiverPoints,do_RoadSourceCalculation,do_AssignLevelsToBuildings,do_ApplyNoiseSymbology,do_Informations

class opeNoise:

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value("locale/userLocale")[0:2]
        localePath = os.path.join(self.plugin_dir, 'i18n', 'opeNoise_{}.qm'.format(locale))

        if os.path.exists(localePath):
            self.translator = QTranslator()
            self.translator.load(localePath)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)
        
    def initGui(self):
        
        # opeNoise         
        self.opeNoise_menu = QMenu(QCoreApplication.translate("opeNoise", "&opeNoise"))
        self.opeNoise_menu.setIcon(QIcon(":/plugins/opeNoise/icons/icon_opeNoise.png"))
        
        
       
        # CreateReceiverPoints
        self.CreateReceiverPoints_item = QAction(QIcon(":/plugins/opeNoise/icons/icon_CreateReceiverPoints.png"),
                                        QCoreApplication.translate("opeNoise", "Create Receiver Points"), self.iface.mainWindow())
        self.CreateReceiverPoints_item.triggered.connect(self.CreateReceiverPoints_show)
        
        # Calculation Menu
        self.Calculation_menu = QMenu(QCoreApplication.translate("opeNoise", "Calculate Noise Levels"))
        self.Calculation_menu.setIcon(QIcon(":/plugins/opeNoise/icons/icon_CalculateNoiseLevels.png"))

        # Point Source
        self.PointSourceCalculation_item = QAction(QIcon(":/plugins/opeNoise/icons/icon_PointSourceCalculation.png"),
                                        QCoreApplication.translate("opeNoise", "Point Source"), self.iface.mainWindow())
        self.PointSourceCalculation_item.triggered.connect(self.PointSourceCalculation_show)
        
        # CalculateNoiseLevels
        self.RoadSourceCalculation_item = QAction(QIcon(":/plugins/opeNoise/icons/icon_RoadSourceCalculation.png"),
                                        QCoreApplication.translate("opeNoise", "Road Source"), self.iface.mainWindow())
        self.RoadSourceCalculation_item.triggered.connect(self.RoadSourceCalculation_show)

        # AssignLevelsToBuildings
        self.AssignLevelsToBuildings_item = QAction(QIcon(":/plugins/opeNoise/icons/icon_AssignLevelsToBuildings.png"),
                                        QCoreApplication.translate("opeNoise", "Assign Levels To Buildings"), self.iface.mainWindow())
        self.AssignLevelsToBuildings_item.triggered.connect(self.AssignLevelsToBuildings_show)
        
        # AssignLevelsToBuildings
        self.ApplyNoiseSymbology_item = QAction(QIcon(":/plugins/opeNoise/icons/icon_ApplyNoiseSymbology.png"),
                                        QCoreApplication.translate("opeNoise", "Apply Noise Symbology"), self.iface.mainWindow())
        self.ApplyNoiseSymbology_item.triggered.connect(self.ApplyNoiseSymbology_show)
        
        
        # Information
        self.Informations_item = QAction(QIcon(":/plugins/opeNoise/icons/icon_Informations.png"),
                                        QCoreApplication.translate("opeNoise", "Informations"), self.iface.mainWindow())
        self.Informations_item.triggered.connect(self.Informations_show)  
        
        # add items
        self.opeNoise_menu.addActions([self.CreateReceiverPoints_item])
        self.Calculation_menu.addActions([self.PointSourceCalculation_item, self.RoadSourceCalculation_item])
        self.opeNoise_menu.addMenu( self.Calculation_menu ) 
        self.opeNoise_menu.addActions([self.AssignLevelsToBuildings_item, self.ApplyNoiseSymbology_item, self.Informations_item])
        
        self.menu = self.iface.pluginMenu()
        self.menu.addMenu( self.opeNoise_menu )       
            
        
    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu("&opeNoise", self.CreateReceiverPoints_item)
        self.iface.removePluginMenu("&opeNoise", self.PointSourceCalculation_item)
        self.iface.removePluginMenu("&opeNoise", self.RoadSourceCalculation_item)
        self.iface.removePluginMenu("&opeNoise", self.AssignLevelsToBuildings_item)     
        self.iface.removePluginMenu("&opeNoise", self.ApplyNoiseSymbology_item)     
        self.iface.removePluginMenu("&opeNoise", self.Informations_item)
       
    def PointSourceCalculation_show(self):
        d = do_PointSourceCalculation.Dialog(self.iface)
        d.show()
        d.exec_()  
        
    def CreateReceiverPoints_show(self):
        d = do_CreateReceiverPoints.Dialog(self.iface)
        d.show()
        d.exec_()    

    def RoadSourceCalculation_show(self):
        d = do_RoadSourceCalculation.Dialog(self.iface)
        d.show()
        d.exec_()   

    def AssignLevelsToBuildings_show(self):
        d = do_AssignLevelsToBuildings.Dialog(self.iface)
        d.show()
        d.exec_()   

    def ApplyNoiseSymbology_show(self):
        d = do_ApplyNoiseSymbology.Dialog(self.iface)
        d.show()
        d.exec_()   
        
    def Informations_show(self):
        d = do_Informations.Dialog_info(self.iface)
        d.show()
        d.exec_()   
        
