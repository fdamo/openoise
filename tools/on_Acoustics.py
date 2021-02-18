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

from builtins import object
from math import sqrt,log10,pi,tanh,atan,exp

from . import on_Acoustics_CNOSSOS
from . import on_Acoustics_NMPB

def GlobalToOctaveBands(model,level_input):
    '''
    the output is a dict:
    - pink noise: with keys [63, 125, 250, 500, 1000 , 2000, 4000, 8000] and value the levels in bands
    - ISO traffic road: with {125 : -10.2, 250 : -10.2, 500 : -7.2, 1000 : -3.9, 2000 : -6.4, 4000 : -11.4}
    '''
    level_output = {}

    bands = [63, 125, 250, 500, 1000, 2000, 4000, 8000]

    if level_input > 0:

        # ISO 1793-3
        if model == 'ISO_traffic_road':
            levels_to_subctract_bands = {125 : -10.2, 250 : -10.2, 500 : -7.2, 1000 : -3.9, 2000 : -6.4, 4000 : -11.4}

            for band in list(levels_to_subctract_bands.keys()):
                level_output[band] = round(level_input + levels_to_subctract_bands[band],1)

        # pink noise
        if model == 'pink':
            level_band_linear = float(10**(level_input/10.)) / float(len(bands))
            level_band = 10 * log10(level_band_linear)

            for band in bands:
                level_output[band] = round(level_band,1)

    else:
        for band in bands:
            level_output[band] = round(0,1)

    return level_output


def OctaveBandsToGlobal(level_input):
    '''
    level_input: has to be a dict with keys [63, 125, 250, 500, 1000 , 2000, 4000, 8000] and value the levels in bands
    '''

    level_output = 0

    for band in level_input:
        level_output = level_output + 10**(level_input[band]/10.)


    if level_output > 0:
        level_output = round(10*log10(level_output),1)

    return level_output


def OctaveBandsToGlobalA(level_input):
    '''
    level_input: has to be a dict with keys [63, 125, 250, 500, 1000 , 2000, 4000, 8000] and value the levels in bands
    '''
    #print("OctaveBandsToGlobalA")
    level_output = 0
    weightA = {63: -26.2, 125 : -16.1, 250 : -8.6, 500 : -3.2, 1000 : 0, 2000 : 1.2, 4000 : 1, 8000: -1.1}

    for band in level_input:
        #print(band,level_input[band],weightA[band])
        level_output = level_output + 10**((level_input[band] + weightA[band])/10.)


    if level_output > 0:
        level_output = round(10*log10(level_output),1)

    return level_output


def DiffBands(dict1,dict2):
    output = {}
    for key in dict1:
        output[key] = round(dict1[key] - dict2[key],1)

    return output

def Lden(Lday,Leve,Lnig,day_hours,eve_hours,nig_hours,day_penalty,eve_penalty,nig_penalty):

    if Lday > 0:
        day_part = 10**(float(Lday + day_penalty)/ float(10))
    else:
        day_part = 0
    if Leve > 0:
        eve_part = 10**(float(Leve + eve_penalty)/ float(10))
    else:
        eve_part = 0
    if Lnig > 0:
        nig_part = 10**(float(Lnig + nig_penalty)/ float(10))
    else:
        nig_part = 0

    if day_part > 0 and eve_part > 0 and eve_part > 0:
        Lden = round(10*log10(1/24.0*(float(day_hours)*day_part + float(eve_hours)*eve_part + float(nig_hours)*nig_part)),1)
    else:
        Lden = -99

    return round(Lden,1)

def Lden_ITA(Lday,Leve,Lnig):

    if Lday > 0:
        day_part = 10**(float(Lday + 0)/ float(10))
    else:
        day_part = 0
    if Leve > 0:
        eve_part = 10**(float(Leve + 5)/ float(10))
    else:
        eve_part = 0
    if Lnig > 0:
        nig_part = 10**(float(Lnig + 10)/ float(10))
    else:
        nig_part = 0

    if day_part > 0 or eve_part > 0 or eve_part > 0:
        round(10*log10(1/24.0*(float(14)*day_part + float(2)*eve_part + float(8)*nig_part)),1)
    else:
        Lden = 0

    return round(Lden,1)


def GeometricalAttenuation(source_type,distance):

    if source_type == 'spherical':
        attenuation = 20 * log10(distance) + 11

    elif source_type == 'cylindrical':
        attenuation = 10 * log10(distance) + 8

    if attenuation < 0:
        attenuation = 0

    return round(attenuation,1)

class AtmosphericAbsorption(object):

    def __init__(self,distance,temp,rel_humidity,level_input):
        self.level_input = level_input
        self.distance = distance
        self.temp = temp
        self.rel_humidity = rel_humidity

    def level(self):
        level_atm = {}
        attenuation = self.attenuation()

        for band in self.level_input:
            level_atm[band] = round(self.level_input[band] - attenuation[band],1)
        return level_atm


    def attenuation(self):

        if self.temp == -20:
            if self.rel_humidity == 10:
                alfa = {63: 0.8, 125: 1.2, 250: 1.4, 500: 1.5, 1000: 1.6, 2000: 2.1, 4000: 3.9, 8000: 10.9}
            if self.rel_humidity == 20:
                alfa = {63: 0.6, 125: 1.5, 250: 2.4, 500: 2.9, 1000: 3.1, 2000: 3.6, 4000: 5.4, 8000: 12.4}
            if self.rel_humidity == 30:
                alfa = {63: 0.4, 125: 1.3, 250: 2.9, 500: 4.4, 1000: 5.1, 2000: 5.7, 4000: 7.4, 8000: 14.6}
            if self.rel_humidity == 40:
                alfa = {63: 0.3, 125: 1, 250: 2.8, 500: 5.4, 1000: 7.2, 2000: 8.2, 4000: 10.2, 8000: 17.2}
            if self.rel_humidity == 50:
                alfa = {63: 0.2, 125: 0.8, 250: 2.5, 500: 5.9, 1000: 9.1, 2000: 11, 4000: 13.2, 8000: 20.3}
            if self.rel_humidity == 60:
                alfa = {63: 0.2, 125: 0.6, 250: 2, 500: 5.7, 1000: 10.6, 2000: 13.9, 4000: 16.6, 8000: 23.9}
            if self.rel_humidity == 70:
                alfa = {63: 0.2, 125: 0.5, 250: 1.7, 500: 5.2, 1000: 11.5, 2000: 16.6, 4000: 20.2, 8000: 27.8}
            if self.rel_humidity == 80:
                alfa = {63: 0.2, 125: 0.4, 250: 1.5, 500: 4.8, 1000: 11.7, 2000: 19, 4000: 24, 8000: 32}
            if self.rel_humidity == 90:
                alfa = {63: 0.1, 125: 0.4, 250: 1.2, 500: 4.2, 1000: 11.6, 2000: 21, 4000: 27.8, 8000: 36.5}
            if self.rel_humidity == 100:
                alfa = {63: 0.1, 125: 0.3, 250: 1, 500: 3.8, 1000: 11.1, 2000: 22.4, 4000: 31.4, 8000: 41.1}

        if self.temp == -15:
            if self.rel_humidity == 10:
                alfa = {63: 0.8, 125: 1.6, 250: 2.2, 500: 2.5, 1000: 2.6, 2000: 3.1, 4000: 4.9, 8000: 12}
            if self.rel_humidity == 20:
                alfa = {63: 0.5, 125: 1.4, 250: 3.3, 500: 5, 1000: 5.9, 2000: 6.5, 4000: 8.3, 8000: 15.5}
            if self.rel_humidity == 30:
                alfa = {63: 0.3, 125: 1, 250: 3, 500: 6.5, 1000: 9.4, 2000: 11, 4000: 13.1, 8000: 20.3}
            if self.rel_humidity == 40:
                alfa = {63: 0.2, 125: 0.7, 250: 2.3, 500: 6.4, 1000: 12.1, 2000: 15.9, 4000: 18.9, 8000: 26.3}
            if self.rel_humidity == 50:
                alfa = {63: 0.2, 125: 0.5, 250: 1.8, 500: 5.6, 1000: 13.2, 2000: 20.5, 4000: 25.2, 8000: 33.2}
            if self.rel_humidity == 60:
                alfa = {63: 0.2, 125: 0.4, 250: 1.4, 500: 4.7, 1000: 13, 2000: 23.9, 4000: 31.8, 8000: 40.9}
            if self.rel_humidity == 70:
                alfa = {63: 0.1, 125: 0.4, 250: 1.1, 500: 3.9, 1000: 12.1, 2000: 26, 4000: 37.9, 8000: 49}
            if self.rel_humidity == 80:
                alfa = {63: 0.1, 125: 0.3, 250: 1, 500: 3.3, 1000: 10.9, 2000: 26.7, 4000: 43.4, 8000: 57.4}
            if self.rel_humidity == 90:
                alfa = {63: 0.1, 125: 0.3, 250: 0.8, 500: 2.8, 1000: 9.7, 2000: 26.4, 4000: 47.8, 8000: 65.8}
            if self.rel_humidity == 100:
                alfa = {63: 0.1, 125: 0.3, 250: 0.8, 500: 2.5, 1000: 8.6, 2000: 25.4, 4000: 51.1, 8000: 73.9}
        
        if self.temp == -10:
            if self.rel_humidity == 10:
                alfa = {63: 0.7, 125: 1.86, 250: 3.36, 500: 4.24, 1000: 4.65, 2000: 5.18, 4000: 7, 8000: 14.2}
            if self.rel_humidity == 20:
                alfa = {63: 0.35, 125: 1.11, 250: 3.35, 500: 7.32, 1000: 10.6, 2000: 12.3, 4000: 14.5, 8000: 21.7}
            if self.rel_humidity == 30:
                alfa = {63: 0.23, 125: 0.68, 250: 2.27, 500: 6.82, 1000: 14.4, 2000: 20.5, 4000: 24.4, 8000: 32.2}
            if self.rel_humidity == 40:
                alfa = {63: 0.19, 125: 0.5, 250: 1.58, 500: 5.3, 1000: 14.6, 2000: 26.8, 4000: 35.4, 8000: 44.8}
            if self.rel_humidity == 50:
                alfa = {63: 0.17, 125: 0.4, 250: 1.2, 500: 4, 1000: 12.9, 2000: 29.7, 4000: 45.5, 8000: 58.6}
            if self.rel_humidity == 60:
                alfa = {63: 0.16, 125: 0.36, 250: 0.96, 500: 4, 1000: 10.9, 2000: 29.6, 4000: 53.5, 8000: 72.7}
            if self.rel_humidity == 70:
                alfa = {63: 0.15, 125: 0.33, 250: 0.82, 500: 2.65, 1000: 9.19, 2000: 27.8, 4000: 58.5, 8000: 86.2}
            if self.rel_humidity == 80:
                alfa = {63: 0.14, 125: 0.31, 250: 0.73, 500: 2.24, 1000: 7.82, 2000: 25.4, 4000: 60.7, 8000: 98.2}
            if self.rel_humidity == 90:
                alfa = {63: 0.13, 125: 0.3, 250: 0.67, 500: 1.95, 1000: 6.75, 2000: 22.9, 4000: 60.6, 8000: 108}
            if self.rel_humidity == 100:
                alfa = {63: 0.13, 125: 0.29, 250: 0.62, 500: 1.73, 1000: 5.91, 2000: 20.6, 4000: 59, 8000: 116}

        if self.temp == -5:
            if self.rel_humidity == 10:
                alfa = {63: 0.54, 125: 1.69, 250: 4.2, 500: 6.87, 1000: 8.29, 2000: 9.16, 4000: 11.1, 8000: 18.3}
            if self.rel_humidity == 20:
                alfa = {63: 0.27, 125: 0.79, 250: 2.6, 500: 7.72, 1000: 16, 2000: 22.4, 4000: 26.4, 8000: 34.4}
            if self.rel_humidity == 30:
                alfa = {63: 0.21, 125: 0.52, 250: 1.58, 500: 5.31, 1000: 15.7, 2000: 31.8, 4000: 44.2, 8000: 55.4}
            if self.rel_humidity == 40:
                alfa = {63: 0.19, 125: 0.42, 250: 1.12, 500: 3.71, 1000: 12.4, 2000: 33.2, 4000: 58.7, 8000: 78.6}
            if self.rel_humidity == 50:
                alfa = {63: 0.17, 125: 0.38, 250: 0.9, 500: 2.8, 1000: 9.68, 2000: 30.1, 4000: 66.4, 8000: 100}
            if self.rel_humidity == 60:
                alfa = {63: 0.16, 125: 0.36, 250: 0.78, 500: 2.25, 1000: 7.74, 2000: 26, 4000: 67.7, 8000: 118}
            if self.rel_humidity == 70:
                alfa = {63: 0.15, 125: 0.35, 250: 0.72, 500: 1.9, 1000: 6.38, 2000: 22.2, 4000: 65, 8000: 131}
            if self.rel_humidity == 80:
                alfa = {63: 0.14, 125: 0.34, 250: 0.68, 500: 1.68, 1000: 5.42, 2000: 19.1, 4000: 60.5, 8000: 138}
            if self.rel_humidity == 90:
                alfa = {63: 0.13, 125: 0.33, 250: 0.66, 500: 1.52, 1000: 4.72, 2000: 16.7, 4000: 55.5, 8000: 140}
            if self.rel_humidity == 100:
                alfa = {63: 0.12, 125: 0.33, 250: 0.65, 500: 1.42, 1000: 4.2, 2000: 14.8, 4000: 50.7, 8000: 139}

        if self.temp == 0:
            if self.rel_humidity == 10:
                alfa = {63: 0.42, 125: 1.3, 250: 40, 500: 9.25, 1000: 14, 2000: 16.6, 4000: 19, 8000: 26.4}
            if self.rel_humidity == 20:
                alfa = {63: 0.25, 125: 0.61, 250: 1.85, 500: 6.16, 1000: 17.7, 2000: 34.6, 4000: 47, 8000: 58.1}
            if self.rel_humidity == 30:
                alfa = {63: 0.21, 125: 0.46, 250: 1.17, 500: 3.73, 1000: 12.7, 2000: 36, 4000: 69, 8000: 95.2}
            if self.rel_humidity == 40:
                alfa = {63: 0.19, 125: 0.42, 250: 0.92, 500: 2.63, 1000: 9, 2000: 29.8, 4000: 75.2, 8000: 127}
            if self.rel_humidity == 50:
                alfa = {63: 0.18, 125: 0.41, 250: 0.82, 500: 2.08, 1000: 6.83, 2000: 23.8, 4000: 71, 8000: 147}
            if self.rel_humidity == 60:
                alfa = {63: 0.16, 125: 0.4, 250: 0.77, 500: 1.78, 1000: 5.5, 2000: 19.3, 4000: 63.3, 8000: 154}
            if self.rel_humidity == 70:
                alfa = {63: 0.15, 125: 0.39, 250: 0.76, 500: 1.61, 1000: 4.64, 2000: 16.1, 4000: 55.5, 8000: 153}
            if self.rel_humidity == 80:
                alfa = {63: 0.13, 125: 0.37, 250: 0.75, 500: 1.51, 1000: 4.06, 2000: 13.8, 4000: 48.8, 8000: 147}
            if self.rel_humidity == 90:
                alfa = {63: 0.12, 125: 0.36, 250: 0.76, 500: 1.45, 1000: 3.66, 2000: 12.1, 4000: 43.2, 8000: 129}
            if self.rel_humidity == 100:
                alfa = {63: 0.18, 125: 0.35, 250: 0.76, 500: 1.42, 1000: 3.37, 2000: 10.8, 4000: 28.6, 8000: 129}

        if self.temp == 5:
            if self.rel_humidity == 10:
                alfa = {63: 0.35, 125: 0.97, 250: 3.11, 500: 9.34, 1000: 20, 2000: 28.5, 4000: 33.5, 8000: 41.8}
            if self.rel_humidity == 20:
                alfa = {63: 0.26, 125: 0.55, 250: 1.38, 500: 4.42, 1000: 14.8, 2000: 40.5, 4000: 73.7, 8000: 98.7}
            if self.rel_humidity == 30:
                alfa = {63: 0.22, 125: 0.49, 250: 1.38, 500: 2.74, 1000: 9.18, 2000: 30.9, 4000: 82.6, 8000: 147}
            if self.rel_humidity == 40:
                alfa = {63: 0.19, 125: 0.47, 250: 0.91, 500: 2.1, 1000: 6.48, 2000: 22.7, 4000: 72.5, 8000: 169}
            if self.rel_humidity == 50:
                alfa = {63: 0.17, 125: 0.45, 250: 0.89, 500: 1.82, 1000: 5.08, 2000: 17.5, 4000: 60.2, 8000: 168}
            if self.rel_humidity == 60:
                alfa = {63: 0.15, 125: 0.43, 250: 0.89, 500: 1.69, 1000: 4.29, 2000: 14.2, 4000: 50.2, 8000: 156}
            if self.rel_humidity == 70:
                alfa = {63: 0.13, 125: 0.41, 250: 0.89, 500: 1.64, 1000: 3.8, 2000: 12, 4000: 42.7, 8000: 142}
            if self.rel_humidity == 80:
                alfa = {63: 0.12, 125: 0.39, 250: 0.89, 500: 1.63, 1000: 3.5, 2000: 10.5, 4000: 37, 8000: 128}
            if self.rel_humidity == 90:
                alfa = {63: 0.11, 125: 0.37, 250: 0.89, 500: 1.64, 1000: 3.31, 2000: 9.39, 4000: 32.7, 8000: 116}
            if self.rel_humidity == 100:
                alfa = {63: 0.1, 125: 0.34, 250: 0.88, 500: 1.66, 1000: 3.2, 2000: 8.58, 4000: 29.4, 8000: 105}

        attenuation_atm = {}
        for band in self.level_input:
           attenuation_atm[band] = (alfa[band] * self.distance)/1000.

        return attenuation_atm

class Diffraction(object):
    '''
    CLASS TO CALCULATE DIFFRACTION
    Input data:
    - model: KURZEANDERSON, STEPHENSON, MAEKAWA1, MAEKAWA2, CNOSSOS
    - level_input: has to be a dict with keys [63, 125, 250, 500, 1000 , 2000, 4000, 8000] and value the levels in bands
    - d_diffTOsource: distance in meters from diffraction point to source point
    - d_recTOsource: distance in meters from receiver point to source point
    - d_recTOdiff: distance in meters from receiver point to diffraction point

    The output is dict:
    - function finale_level: initial level - attenuation
    - attenuation: only the attenuation
    '''

    def __init__(self, model,level_input,d_diffTOsource,d_recTOsource,d_recTOdiff):

        self.model = model
        self.level_input = level_input
        self.d_diffTOsource = d_diffTOsource
        self.d_recTOsource = d_recTOsource
        self.d_recTOdiff = d_recTOdiff

        self.sound_speed = 343.  # Expressed in m/s
        self.delta =  float (d_recTOdiff + d_diffTOsource - d_recTOsource)


    def level(self):

        level_diff = {}

        attenuation = self.attenuation()

        for band in self.level_input:
            level_diff[band] = round(self.level_input[band] - GeometricalAttenuation('spherical',self.d_recTOsource) - attenuation[band],1)

        return level_diff

    def attenuation(self):

        if self.model == 'KURZEANDERSON':
            attenuation = self.KURZEANDERSON()
        elif self.model == 'STEPHENSON':
            attenuation = self.STEPHENSON()
        elif self.model == 'MAEKAWA1':
            attenuation = self.MAEKAWA1()
        elif self.model == 'MAEKAWA2':
            attenuation = self.MAEKAWA2()
        elif self.model == 'CNOSSOS':
            attenuation = self.CNOSSOS()

        return attenuation

    def fresnel_number(self):
        N ={}               # Fresnel Number Dict
        for band in self.level_input:
            wave_length = self.sound_speed / float(band)
#            print 'delta ', self.delta
            N[band]= 2 * self.delta / wave_length
        return N

    def KURZEANDERSON(self):
        N = self.fresnel_number()
        KA = {}
        for band in self.level_input:
#            print 'xxxxxxxxxxxxxxxxxxxxxxx'
#            print N[band]
#            print tanh(sqrt(2*pi*abs(N[band])))
            KurzeAnderson = 5 + 20* log10((sqrt(2*pi*abs(N[band])))/(tanh(sqrt(2*pi*abs(N[band])))))  # Kurze-Anderson formula
            KA[band] = round(KurzeAnderson,1)

        return KA

    def STEPHENSON(self):
        N = self.fresnel_number()
        Step = {}
        for band in self.level_input:
            Stephensons = 10* log10 (.5 - (atan((1./sqrt(3.))+6*abs(N[band])*(1+exp(-3.*abs(N[band]))))/pi)) # Stephenson formula
            Step[band] = round(-1*Stephensons,2)

        return Step

    def MAEKAWA1(self):
        N = self.fresnel_number()
        Maek1 = {}
        for band in self.level_input:
            Maekawa1 = 10* log10(20*abs(N[band])) # Maekawa Correction formula
            Maek1[band] = round(Maekawa1,2)

        return Maek1

    def MAEKAWA2(self):
        N = self.fresnel_number()
        Maek2 = {}
        for band in self.level_input:
            Maekawa2 = 10.* log10(2. + 5.5*abs(N[band])) # Maekawa formula
            Maek2[band] = round(Maekawa2,2)

        return Maek2

    def CNOSSOS(self):

        Semi_Perim = (self.d_diffTOsource + self.d_recTOsource + self.d_recTOdiff)/2
        h = round((2./self.d_recTOsource) * sqrt(Semi_Perim*(Semi_Perim - self.d_diffTOsource)*(Semi_Perim - self.d_recTOsource)*(Semi_Perim - self.d_recTOdiff)),2)
        Ch = {}
        Att_dic = {}

        for band in self.level_input:
            wave_length = self.sound_speed/float(band)
            if self.delta < -wave_length/20:
                Att = 0
                Att_dic[band] = Att
            else:
                Ch[band] = min(band*h/250.,1)
                if (40/wave_length)*self.delta >= -2:
                    Att = 10*Ch[band]*log10(3+(40/wave_length)*self.delta)
                    Att_dic[band] = round(Att,2)
                else:
                    Att = 0
                    Att_dic[band] = round(Att,2)

        return Att_dic


class CNOSSOS(object):

    def __init__(self, input_dict):
        self.input_dict = input_dict

    def bands(self):
        return on_Acoustics_CNOSSOS.CNOSSOS(self.input_dict).bands()

    def overall(self):
        return on_Acoustics_CNOSSOS.CNOSSOS(self.input_dict).bands().overall()


class NMPB(object):

    def __init__(self, input_dict):
        self.input_dict = input_dict

    def bands(self):
        return on_Acoustics_NMPB.NMPB(self.input_dict).bands()

    def overall(self):
        return on_Acoustics_NMPB.NMPB(self.input_dict).overall()






#
#level_emi_bands = GlobalToOctaveBands('ISO_traffic_road',70)
#print level_emi_bands
#d_diffTOsource = 35.8
#d_recTOsource = 31.96
#d_recTOdiff = 13.84
#print 'deltaaaa' , d_recTOdiff + d_diffTOsource - d_recTOsource
#band = Diffraction('KURZEANDERSON',level_emi_bands,d_diffTOsource,d_recTOsource,d_recTOdiff).level()
#print band
#print OctaveBandsToGlobal(band)


################################################################################################



#ii = {4000: 67.5, 8000: 59.4, 1000: 77.9, 2000: 74.9, 500: 73.5, 250: 71.9, 125: 72.6, 63: 77.9}
#a = AtmosphericAbsorption((6.37+31.62),20,70,ii).level()
#c = Diffraction('CNOSSOS',ii ,31.62,33.69,6.37).attenuation()
#d = DiffBands(a,c)
#b = GeometricalAttenuation('spherical',33.69)
#
#
#print OctaveBandsToGlobal(d)




#gg =AtmosphericAbsorption((6.37+31.62),20,70,ii).attenuation()
#
#print gg

################################################################################################




#print NMPB(10,10,10,10,'continuos','smooth','flat').bands()

#print CNOSSOS(10,10,0,
#        0,0,
#        0,0,
#        0,0,
#        0,0,
#        0,0,
#        0,'k=1',100,20,0).overall()
##
#
#

#print level
#print OctaveBandsToGlobal(level)
#print Diffraction('CNOSSOS',level,10,8,11).level()
#print Diffraction('MAEKAWA2',level,10,8,11).level()
#print OctaveBandsToGlobal(Diffraction('KURZEANDERSON',level,10,8,11).level())

#level_ini = GlobalToOctaveBands('CNOSSOS',100)
#print level_ini
#
#l =  Diffraction('KURZEANDERSON',level_ini,42.35,43.92,6.37).level()
#a = Diffraction('KURZEANDERSON',level_ini,42.35,43.92,6.37).attenuation()
#print 'level',l
#print 'att', a
#
#print 'level global',OctaveBandsToGlobal(l)
#print 'att global', OctaveBandsToGlobal(a)
#print 20 * log10(43.92) + 11
