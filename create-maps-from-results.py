# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/. */

# Authors:
# Michael Berg-Mohnicke <michael.berg@zalf.de>
#
# Maintainers:
# Currently maintained by the authors.
#
# This file has been created at the Institute of
# Landscape Systems Analysis at the ZALF.
# Copyright (C: Leibniz Centre for Agricultural Landscape Research (ZALF)

import csv
import sys
#sys.path.insert(0, "C:\\Users\\berg.ZALF-AD\\GitHub\\monica\\project-files\\Win32\\Release")
#sys.path.insert(0, "C:\\Users\\berg.ZALF-AD\\GitHub\\monica\\project-files\\Win32\\Debug")
sys.path.insert(0, "C:\\Users\\berg.ZALF-AD\\GitHub\\monica\\src\\python")

FILES = [
    #"Short_Maize.csv",
    #"Short_WW.csv",
    #"Long_Maize.csv",
    #"Long_WW.csv",
    #"Long-Short_Maize.csv",
    #"Long-Short_WW.csv",
    
    #"SoilProperties.csv"
    
    "SummaryWeather2000-2010.csv"
]

HEADER = ""
ASC = []
with open("macsur-heat-stress-study-extent.asc") as file_:
    for _ in range(0, 6):
        HEADER = HEADER + file_.next()
    for line in file_:
        line_ = []
        for rowcol_str in line.strip().split(" "):
            line_.append(rowcol_str)
        ASC.append(line_)

OUTPUTS = [
    #"SOCtop", "SOCbottom", "DeltaSOCtop",
    #"DeltaSOCbottom", "Nmin", "NLeach",
    #"CO2emission", "Yield", "IniSOCtop", "IniSOCbottom",

    #"OC_topsoil", "Sand_topsoil", "Clay_topsoil", "Silt_topsoil"

    "Tmin", "Tavg", "Tmax", "Precip", "Globrad"
]

for filename in FILES:
    data = {}
    with open("results-for-maps/" + filename) as _:
        reader = csv.reader(_)
        reader.next()
        for line in reader:
            #row_, col_ = line[1].split("_")
            row_, col_ = line[0].split("_")
            row, col = (int(row_), int(col_))
            data[(row, col)] = [
                #float(line[4]), #"SOCtop"
                #float(line[5]), #"SOCbottom"
                #float(line[6]), #"DeltaSOCtop"
                #float(line[7]), #"DeltaSOCbottom"
                #float(line[8]), #"Nmin"
                #float(line[9]), #"NLeach"
                #float(line[10]), #"CO2emission"
                #float(line[11]), #"Yield"
                #float(line[12]), #"IniSOCtop"
                #float(line[13]) #"IniSOCbottom"

                #float(line[1]), #"OC_topsoil"
                #float(line[2]), #"Sand_topsoil"
                #float(line[3]), #"Clay_topsoil"
                #float(line[4]) #"Silt_topsoil"

                float(line[3]), #"Tmin"
                float(line[4]), #"Tavg"
                float(line[5]), #"Tmax"
                float(line[6]), #"Precip"
                float(line[7]), #"Globrad"
            ]

    files = []
    for output in OUTPUTS:
        files.append(open("results-for-maps/" + filename[:-4] + "-" + output + ".asc", "w"))

    for file_ in files:
        file_.write(HEADER)

    for row in ASC:
        line = []
        for col_no, rowcol_str in enumerate(row):
            row, col = (int(rowcol_str[:2]), int(rowcol_str[2:])) if len(rowcol_str) == 5 else (int(rowcol_str[:3]), int(rowcol_str[3:])) 
            for idx, file_ in enumerate(files):
                if rowcol_str == "-9999" or (row, col) not in data:
                    file_.write("-9999")
                else:
                    file_.write(str(data[(row, col)][idx]))

                if col_no == 133:
                    file_.write("\n")
                else:
                  file_.write(" ")

    for file_ in files:
        file_.close()

