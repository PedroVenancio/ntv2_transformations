# -*- coding: utf-8 -*-

"""
***************************************************************************
    VectorIT_RER_ETRS89DirInv.py
    ---------------------
    Date                 : March 2015
    Copyright            : (C) 2015 by Giovanni Manghi
    Email                : giovanni dot manghi at naturalgis dot pt
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__author__ = 'Giovanni Manghi'
__date__ = 'March 2015'
__copyright__ = '(C) 2015, Giovanni Manghi'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import inspect
import os

from PyQt4.QtGui import *

from qgis.core import *

from processing.gui.Help2Html import getHtmlFromRstFile

try:
    from processing.parameters.ParameterVector import ParameterVector
    from processing.parameters.ParameterSelection import ParameterSelection
    from processing.outputs.OutputVector import OutputVector
except:
    from processing.core.parameters import ParameterVector
    from processing.core.parameters import ParameterSelection
    from processing.core.outputs import OutputVector

from processing.tools.system import *

from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.algs.gdal.GdalUtils import GdalUtils
from processing.tools.vector import ogrConnectionString, ogrLayerName


class VectorIT_RER_ETRS89DirInv(GeoAlgorithm):

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    TRANSF = 'TRANSF'
    TRANSF_OPTIONS = ['Direct: Old Data -> ETRS89 [EPSG:4258]',
                      'Inverse: ETRS89 [EPSG:4258] -> Old Data']
    CRS = 'CRS'
    CRS_OPTIONS = ['Monte Mario - GBO [EPSG:3003]',
                   'UTM - ED50 [EPSG:23032]']
    GRID = 'GRID'
    GRID_OPTIONS = ['Grigliati NTv2 RER 2013 la trasformazione di coordinate in Emilia-Romagna']

    def getIcon(self):
        return  QIcon(os.path.dirname(__file__) + '/icons/it.png')

    def help(self):
        name = self.commandLineName().split(':')[1].lower()
        filename = os.path.join(os.path.dirname(inspect.getfile(self.__class__)), 'help', name + '.rst')
        try:
          html = getHtmlFromRstFile(filename)
          return True, html
        except:
          return False, None

    def defineCharacteristics(self):
        self.name = '[IT] Direct and inverse Vector transformation'
        self.group = '[IT] Italy (Emilia-Romagna)'
        self.addParameter(ParameterVector(self.INPUT, 'Input vector',
                          [ParameterVector.VECTOR_TYPE_ANY]))
        self.addParameter(ParameterSelection(self.TRANSF, 'Transformation',
                          self.TRANSF_OPTIONS))
        self.addParameter(ParameterSelection(self.CRS, 'Old Datum',
                          self.CRS_OPTIONS))
        self.addParameter(ParameterSelection(self.GRID, 'NTv2 Grid',
                          self.GRID_OPTIONS))
        self.addOutput(OutputVector(self.OUTPUT, 'Output'))

    def processAlgorithm(self, progress):
        inLayer = self.getParameterValue(self.INPUT)
        conn = ogrConnectionString(inLayer)[1:-1]

        output = self.getOutputFromName(self.OUTPUT)
        outFile = output.value

        if self.getParameterValue(self.TRANSF) == 0:
            # Direct transformation
            arguments = ['-s_srs']
            if self.getParameterValue(self.CRS) == 0:
                # Monte Mario - GBO
                if self.getParameterValue(self.GRID) == 0:
                    # Grigliati NTv2 RER 2013 la trasformazione di coordinate in Emilia-Romagna
                    arguments.append('+proj=tmerc +lat_0=0 +lon_0=9 +k=0.9996 +x_0=1500000 +y_0=0 +ellps=intl +nadgrids=' + os.path.dirname(__file__) + '/grids/RER_AD400_MM_ETRS89_V1A.gsb +wktext +units=m +no_defs')
            else:
                # UTM - ED50
                if self.getParameterValue(self.GRID) == 0:
                    # Grigliati NTv2 RER 2013 la trasformazione di coordinate in Emilia-Romagna
                    arguments.append('+proj=utm +zone=32 +ellps=intl +nadgrids=' + os.path.dirname(__file__) + '/grids/RER_ED50_ETRS89_GPS7_K2.GSB +wktext +units=m +no_defs')
            arguments.append('-t_srs')
            arguments.append('EPSG:4258')

            arguments.append('-f')
            arguments.append('ESRI Shapefile')
        
            arguments.append(outFile)
            arguments.append(conn)       
            arguments.append(ogrLayerName(inLayer))

        else:
            # Inverse transformation
            arguments = ['-s_srs']
            arguments.append('EPSG:4258')
            arguments.append('-t_srs')
            if self.getParameterValue(self.CRS) == 0:
                # Monte Mario - GBO
                if self.getParameterValue(self.GRID) == 0:
                    # Grigliati NTv2 RER 2013 la trasformazione di coordinate in Emilia-Romagna
                    arguments.append('+proj=tmerc +lat_0=0 +lon_0=9 +k=0.9996 +x_0=1500000 +y_0=0 +ellps=intl +nadgrids=' + os.path.dirname(__file__) + '/grids/RER_AD400_MM_ETRS89_V1A.gsb +wktext +units=m +no_defs')
                arguments.append('-f')
                arguments.append('\"Geojson\"')
                arguments.append('/vsistdout/')
                arguments.append(conn)
                arguments.append(ogrLayerName(inLayer))
                arguments.append('-lco') 
                arguments.append('ENCODING=UTF-8')
                arguments.append('|')
                arguments.append('ogr2ogr')
                arguments.append('-f')               
                arguments.append('ESRI Shapefile') 
                arguments.append('-a_srs') 
                arguments.append('EPSG:3003') 
                arguments.append(outFile)    
                arguments.append('/vsistdin/')
            else:
                # UTM - ED50
                if self.getParameterValue(self.GRID) == 0:
                    # Grigliati NTv2 RER 2013 la trasformazione di coordinate in Emilia-Romagna
                    arguments.append('+proj=utm +zone=32 +ellps=intl +nadgrids=' + os.path.dirname(__file__) + '/grids/RER_ED50_ETRS89_GPS7_K2.GSB +wktext +units=m +no_defs')
                arguments.append('-f')
                arguments.append('\"Geojson\"')
                arguments.append('/vsistdout/')
                arguments.append(conn)
                arguments.append(ogrLayerName(inLayer))
                arguments.append('-lco') 
                arguments.append('ENCODING=UTF-8')
                arguments.append('|')
                arguments.append('ogr2ogr')
                arguments.append('-f')               
                arguments.append('ESRI Shapefile') 
                arguments.append('-a_srs') 
                arguments.append('EPSG:23032') 
                arguments.append(outFile)    
                arguments.append('/vsistdin/')

        arguments.append('-lco') 
        arguments.append('ENCODING=UTF-8')
        
        if os.path.isfile(os.path.dirname(__file__) + '/grids/RER_AD400_MM_ETRS89_V1A.gsb') is False:
           import urllib
           urllib.urlretrieve ("https://github.com/NaturalGIS/ntv2_transformations_grids_and_sample_data/raw/master/it_rer/RER_AD400_MM_ETRS89_V1A.gsb", os.path.dirname(__file__) + "/grids/RER_AD400_MM_ETRS89_V1A.gsb")
           urllib.urlretrieve ("https://github.com/NaturalGIS/ntv2_transformations_grids_and_sample_data/raw/master/it_rer/RER_ED50_ETRS89_GPS7_K2.GSB", os.path.dirname(__file__) + "/grids/RER_ED50_ETRS89_GPS7_K2.GSB")

        commands = ['ogr2ogr', GdalUtils.escapeAndJoin(arguments)]
        GdalUtils.runGdal(commands, progress)
