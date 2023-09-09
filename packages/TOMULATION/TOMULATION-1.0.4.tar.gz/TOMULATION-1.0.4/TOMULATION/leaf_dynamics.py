# -*- coding: utf-8 -*-
#%%
# Naomichi Fujiuchi (naofujiuchi@gmail.com), April 2022
# This is a derivative work by Fujiuchi (GNU GPL license) from the original work PCSE by Allard de Wit (allard.dewit@wur.nl) (EUPL license).
from datetime import datetime as dt
from math import exp
from collections import deque
from array import array
from pcse.traitlets import Float, Int, Instance
from pcse.decorators import prepare_rates, prepare_states
from pcse.util import limit, AfgenTrait
from pcse.base import ParamTemplate, StatesTemplate, RatesTemplate, \
     SimulationObject
from pcse import signals
from pcse.fileinput import ExcelWeatherDataProvider,PCSEFileReader,CABOWeatherDataProvider
import copy
import os
import pandas as pd
#　datetimeをimportしたい
# from datetime import date
from datetime import datetime,timedelta
import numpy as np
import csv
#%%
class TOMGROSIM_Leaf_Dynamics(SimulationObject):

    class Parameters(ParamTemplate):
        PD  = Float(-99.)
        POLA = Float(-99.)
        POLB = Float(-99.)
        POLC = Float(-99.)
        FRPET = Float(-99.)
        SLAMAX = Float(-99)
        SLAMIN  = Float(-99.)
        BETAT  = Float(-99.)
        BETAC  = Float(-99.)
        LVI = Instance(list) # Initial leaf weights
        LAI = Instance(list) # Initial leafarea
        SLAI = Instance(list) # Initial specific leaf area (SLA)
        DOHLI = Instance(list)  # Initial data of day of harvest of leaves (removing lower leaves)


    class StateVariables(StatesTemplate):
        LV     = Instance(list)
        SLA    = Instance(list)
        LA = Instance(list)
        LAI    = Float(-99.) # Total leaf area of living leaves
        WLV    = Float(-99.) # Total leaf weight of living leaves
        DWLV   = Float(-99.) # Total weight of harvested leaves
        TWLV   = Float(-99.) # Total weight of all the leaves (including harvested leaves)
        DOHL = Instance(list) # Day of harvest of leaves (removing lower leaves)
        ACL = Instance(list) # Actual expantion rate of each leaf
        GRLV  = Instance(list)
        SSLA = Float(-99.) # Structrual SLA of each leaf
        POL = Instance(list) # Potential expansion rate of each leaf
        LVAGE  = Instance(list)
        PGRLV = Instance(list) # Potential growth rate of leaves
        MPGRLV = Instance(list) # Maximum potential growth rate of leaves (without any loss of growth)

    class RateVariables(RatesTemplate):
        pass

    def initialize(self, day, kiosk, parvalues,cropinitiallist):

        self.kiosk  = kiosk
        self.params = self.Parameters(parvalues)

        # CALCULATE INITIAL STATE VARIABLES
        params = self.params
        # # Initial leaf biomass, leaf area, and leaf age

        # Initial leaf biomass, leaf area, and leaf age
        LV = cropinitiallist["LVI"] # Dry weights of the leaves that have not generated yet are 0.
        LA = cropinitiallist["LAI"] # List of initial leaf area
        DOHL = cropinitiallist["DOHLI"]

        DOHL = [list(map(lambda x: x if type(x) == str else None, row)) for row in DOHL]
        LA = [list(map(lambda x: x if x >= 0  else None, row)) for row in LA]
        LV = [list(map(lambda x: x if x >= 0  else None, row)) for row in LV]
        WLV = 0.
        DWLV = 0.
        LAI = 0.
        for i in range(0, len(LV)):
            for j in range(0, len(LV[i])):
                if DOHL[i][j] != None: # Harvested = Dead
                    DWLV += float(LV[i][j])
                else: # Not harvested yet = living
                    if LV[i][j]== None:
                        pass
                    else:
                        WLV += float(LV[i][j])
                        LAI += float(LA[i][j])
        TWLV = WLV + DWLV


        # Initialize StateVariables object
        self.states = self.StateVariables(kiosk, publish=["LV","LA","SLA","LAI","TWLV","WLV","DWLV","DOHL","ACL","SSLA","LVAGE","GRLV"],
                                          LV=LV, LA=LA, SLA=params.SLAI,ACL=[],LVAGE=[],PGRLV=[],MPGRLV=[],POL=[],
                                          LAI=LAI, WLV=WLV, DWLV=DWLV, TWLV=TWLV,GRLV=[],SSLA=None,
                                          DOHL=DOHL)
        self.rates = self.RateVariables(kiosk)

    @prepare_rates
    def calc_potential(self, day, drv):
        r = self.rates
        p = self.params
        k = self.kiosk
        # List of harvested (0: harvested, 1: not yet harvested)
        LOH = copy.deepcopy(k.DOHL)
        for i in range(0, len(k.DOHL)):
            for j in range(0, len(k.DOHL[i])):
                if k.DOHL[i][j] == None:
                    LOH[i][j] = 1
                else:
                    LOH[i][j] = 0

        # Leaf age
        k.LVAGE = copy.deepcopy(k.DOEL)
        for i in range(0, len(k.DOEL)):
            for j in range(0, len(k.DOEL[i])):
                if k.DOEL[i][j] != None:
                    td = datetime.strptime(str(k.DOEL[i][j]),'%Y-%m-%d' )

                    td = td.date()
                    age_days = day - td
                    age_days = age_days/timedelta(days=1)
                    k.LVAGE[i][j] = age_days
                else:
                    k.LVAGE[i][j] = 0

        # List of potential leaf expansion rate of each leaf
        # The first derivative of a Gompertz function relating area of growing leaves to time from leaf appearance (Berin, 1993, Ph.D. thesis)
        # yields the potential area expansion rate of a leaf (Heuvelink and Bertin, 1994, J. Hort. Sci,)

        drv.TEMP = ((drv.TMAX + drv.TMIN)/2)
        if drv.TEMP <= 28:
            FTEMP = 1.0 + 0.0281 * (drv.TEMP - 28)
        else:
            FTEMP = 1.0 - 0.0455 * (drv.TEMP - 28)
        drv.CO2 = 400
        FCO2 = 1 + 0.003 * (drv.CO2 - 350)

        k.POL = [list(map(lambda x: p.PD * FTEMP * FCO2 * p.POLA * p.POLB * exp(-p.POLB * (x - p.POLC)) * exp(-exp(-p.POLB * (x - p.POLC))), row)) for row in k.LVAGE] # p.PD: plant density

        k.POL = [[a * b for a, b in zip(*rows)] for rows in zip(k.POL, LOH)] # Set POL of harvested leaves at 0.

        # Structural SLA (sSLA)
        # sSLA calculation of TOMGRO (Jones et al., 1991, Transaction of the ASAE). Parameter values of (Heuvelink and Bertin, 1994, J. Hort. Sci.) were used.
        #全日射(IRRAD)を光合成有効放射(PAR)に変換して使用
        drv.PAR = drv.IRRAD*1000*2.285*10**(-6)
        k.SSLA = (p.SLAMAX + (p.SLAMAX - p.SLAMIN) * exp(-0.471 * drv.PAR)) / (1 + p.BETAT * (24 - drv.TEMP)) / (1 + p.BETAC * (drv.CO2 - 350))

        # Potential growth rates of leaves (PGRLV) and fruits (PGRFR) that are not harvested yet.
        # Maximum potential growth rate of leaves (MPGRLV) is defined by the day's POL and SSLA
        # Potential growth rate of leaves (PGRLV) is MPGRLV * CAF.
        # The cumulative adaptation factor (CAF) is a state variable calculated in wofost.py
        k.MPGRLV = [list(map(lambda x: x / k.SSLA, row)) for row in k.POL]
        k.MPGRLV = [list(map(lambda x: (1 + p.FRPET) * x, row)) for row in k.MPGRLV] # Include petiole (partitioning ratio of dry matter, petiold:leaf = FRPET:1)
        k.PGRLV = [list(map(lambda x: k.CAF * x, row)) for row in k.MPGRLV]

    @prepare_rates
    def calc_rates(self, day, drv ):
        r = self.rates
        p = self.params
        k = self.kiosk
        # Growth rate leaves
        k.GRLV = [list(map(lambda x: k.DMI * x / k.TPGR, row)) for row in k.PGRLV] # List of dry mass partitioned to each leaf depending on its potential growth rate (PGRLV)
        # Actual leaf expansion rate
        k.ACL = [list(map(lambda x: x / (1 + p.FRPET), row)) for row in k.GRLV] # Exclude petiole from the growth rate of leaf
        k.ACL = [list(map(lambda x: x * k.SSLA, row)) for row in k.ACL] # Convert dry mass increase to leaf expansion

    @prepare_states
    def integrate(self, day, delt=1.0):

        p = self.params
        r = self.rates
        s = self.states
        k = self.kiosk
        def sum_(x):
            if x[0]==None or x[1]==None:
                pass
            else:
                return sum(x)
        # Update leaf biomass states
        k.LV = list(map(lambda l1, l2: [sum_(x) for x in zip(l1, l2)], k.LV, k.GRLV))

        # Update leaf area
        k.LA = list(map(lambda l1, l2: [sum_(x) for x in zip(l1, l2)], k.LA, k.ACL))

        # Update leaf SLA
        k.SLA = [[None if a==None or b==None else a / b for a, b in zip(*rows) ] for rows in zip(k.LA, k.LV)]


        # Update total leaf biomass
        k.WLV = 0.
        k.DWLV = 0.
        k.LAI = 0.



        for i in range(0, len(k.LV)):
            for j in range(0, len(k.LV[i])):
                if k.DOHL[i][j] != None: #already harvested (= dead), DOHL[i][j] == None: not harvested yet (= living).
                    if i >= 1 and j >= 3:
                        pass
                    else:
                        k.DWLV += k.LV[i][j]
                else:
                    if k.LV[i][j]== None:
                        pass
                    else:
                        k.WLV += k.LV[i][j]
                        k.LAI += k.LA[i][j]
        k.TWLV = k.WLV + k.DWLV
        # Harvest scheme for updating DOHL
        # DOHL ... If the development stage (DVSF) of the 1st fruit of the truss becomes over 0.8, then the leaves on the truss will be removed.
        for i in range(0, len(k.DOHL)):
            for j in range(0, len(k.DOHL[i])):
                if k.DVSF[i][0] == None :
                    pass
                elif k.DOHL[i][j] == None and k.DVSF[i][0] >= 0.8:
                    k.DOHL[i][j] = day
                else:
                    pass

# %%
