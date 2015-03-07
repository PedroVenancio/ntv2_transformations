# -*- coding: utf-8 -*-

"""
***************************************************************************
    VectorGK3ETRS8932NDirInv.py
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

from processing.algs.gdal.OgrAlgorithm import OgrAlgorithm
from processing.algs.gdal.GdalUtils import GdalUtils


class VectorGK3ETRS8932NDirInv(OgrAlgorithm):

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    TRANSF = 'TRANSF'
    TRANSF_OPTIONS = ['Direct: Gauss-Kr�ger zone 3 [EPSG:31467] -> ETRS89/UTM Zone 32N [EPSG:25832]',
                      'Inverse: ETRS89/UTM Zone 32N [EPSG:25832] -> Gauss-Kr�ger zone 3 [EPSG:31467]']
    CRS = 'CRS'
    CRS_OPTIONS = ['Gauss-Kr�ger zone 3 [EPSG:31467]']
    GRID = 'GRID'
    GRID_OPTIONS = ['BETA2007']

    def getIcon(self):
        return  QIcon(os.path.dirname(__file__) + '/icons/de.png')

    def help(self):
        name = self.commandLineName().split(':')[1].lower()
        filename = os.path.join(os.path.dirname(inspect.getfile(self.__class__)), 'help', name + '.rst')
        try:
          html = getHtmlFromRstFile(filename)
          return True, html
        except:
          return False, None

    def defineCharacteristics(self):
        self.name = '[DE] Direct and inverse Vector tranformation'
        self.group = '[DE] Germany'
        self.addParameter(ParameterVector(self.INPUT, 'Input vector',
                          [ParameterVector.VECTOR_TYPE_ANY]))
        self.addParameter(ParameterSelection(self.TRANSF, 'Transformation',
                          self.TRANSF_OPTIONS))
        self.addParameter(ParameterSelection(self.CRS, 'Old Datum',
                          self.CRS_OPTIONS))
        self.addParameter(ParameterSelection(self.GRID, 'Ntv2 Grid',
                          self.GRID_OPTIONS))
        self.addOutput(OutputVector(self.OUTPUT, 'Output'))

    def processAlgorithm(self, progress):
        inLayer = self.getParameterValue(self.INPUT)
        conn = self.ogrConnectionString(inLayer)

        output = self.getOutputFromName(self.OUTPUT)
        outFile = output.value

        if self.getParameterValue(self.TRANSF) == 0:
            # Direct transformation
            arguments = ['-s_srs']
            if self.getParameterValue(self.CRS) == 0:
                # Gauss-Kr�ger zone 3
                if self.getParameterValue(self.GRID) == 0:
                    # BETA2007
                    arguments.append('+proj=tmerc +lat_0=0 +lon_0=9 +k=1 +x_0=3500000 +y_0=0 +ellps=bessel +nadgrids=' + os.path.dirname(__file__) + '/grids/BETA2007.gsb +wktext +units=m +no_defs')
            arguments.append('-t_srs')
            arguments.append('EPSG:25832')
        else:
            # Inverse transformation
            arguments = ['-s_srs']
            arguments.append('EPSG:25832')
            arguments.append('-t_srs')
            if self.getParameterValue(self.CRS) == 0:
                # Gauss-Kr�ger zone 3
                if self.getParameterValue(self.GRID) == 0:
                    # BETA2007
                    arguments.append('+proj=tmerc +lat_0=0 +lon_0=9 +k=1 +x_0=3500000 +y_0=0 +ellps=bessel +nadgrids=' + os.path.dirname(__file__) + '/grids/BETA2007.gsb +wktext +units=m +no_defs')

        arguments.append('-f')
        arguments.append('ESRI Shapefile')

        arguments.append(outFile)
        arguments.append(conn)

        commands = ['ogr2ogr', GdalUtils.escapeAndJoin(arguments)]
        GdalUtils.runGdal(commands, progress)
