#!/usr/bin/python
# -*- coding: UTF-8

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

import time
import os
import json
import csv
#import copy
from StringIO import StringIO
from datetime import date, datetime, timedelta
from collections import defaultdict
#import types
import sys
#sys.path.insert(0, "C:\\Users\\berg.ZALF-AD\\GitHub\\monica\\project-files\\Win32\\Release")
#sys.path.insert(0, "C:\\Users\\berg.ZALF-AD\\GitHub\\monica\\project-files\\Win32\\Debug")
#sys.path.insert(0, "C:\\Users\\berg.ZALF-AD\\GitHub\\monica\\src\\python")
print sys.path
#sys.path.append('C:/Users/berg.ZALF-AD/GitHub/util/soil')
#from soil_conversion import *
#import monica_python
import zmq
import monica_io
#print "path to monica_io: ", monica_io.__file__

#print "pyzmq version: ", zmq.pyzmq_version()
#print "sys.path: ", sys.path
#print "sys.version: ", sys.version

#PATH_TO_CLIMATE_DATA = "A:/macsur-eu-heat-stress-transformed/"
START_YEAR = 1900
PATH_TO_CLIMATE_DATA_SERVER = "/archiv-daten/md/projects/macsur-cgra-soc-spinup/climate-data/0/0_0_1890_2010/"
#PATH_TO_CLIMATE_DATA = "B:/md/berg/macsur-eu-heat-stress-transformed/"

def main():
    "main"

    context = zmq.Context()
    socket = context.socket(zmq.PUSH)
    #port = 6666 if len(sys.argv) == 1 else sys.argv[1]
    config = {
        "port": 6666,
        "start": 1,
        "end": 8157
    }
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            kkk, vvv = arg.split("=")
            if kkk in config:
                config[kkk] = int(vvv)

    #socket.bind("tcp://*:" + str(config["port"]))
    #socket.connect("tcp://localhost:" + str(config["port"]))
    socket.connect("tcp://cluster2:" + str(config["port"]))

    with open("sim.json") as _:
        sim = json.load(_)

    with open("site.json") as _:
        site = json.load(_)

    with open("crop.json") as _:
        crop = json.load(_)

    with open("sims.json") as _:
        sims = json.load(_)

    sim["include-file-base-path"] = "C:/Users/berg.ZALF-AD/MONICA"

    def read_pheno(path_to_file):
        "read phenology data"
        with open(path_to_file) as _:
            ppp = {}
            reader = csv.reader(_)
            reader.next()
            for row in reader:
                ppp[(int(row[0]), int(row[1]))] = {
                    "sowing-doy": int(row[6]),
                    "flowering-doy": int(row[7]),
                    "harvest-doy": int(row[8])
                }
            return ppp

    pheno = {
        "GM": read_pheno("Maize_pheno_v3.csv"),
        "WW": read_pheno("WW_pheno_v3.csv")
    }

    soil = {}
    row_cols = []
    with open("JRC_soil_macsur_v3.csv") as _:
        reader = csv.reader(_)
        reader.next()
        for row in reader:
            row_col = (int(row[1]), int(row[0]))
            row_cols.append(row_col)
            soil[row_col] = {
                "elevation": float(row[4]),
                "latitude": float(row[5]),
                "depth": float(row[6]),
                "pwp": float(row[7]),
                "fc": float(row[8]),
                "sat": float(row[9]),
                "sw-init": float(row[10]),
                "oc-topsoil": float(row[11]),
                "oc-subsoil": float(row[12]),
                "bd-topsoil": float(row[13]),
                "bd-subsoil": float(row[14]),
                "sand-topsoil": float(row[15]),
                "sand-subsoil": float(row[18]),
                "clay-topsoil": float(row[16]),
                "clay-subsoil": float(row[19]),
            }

    def read_calibrated_tsums(path_to_file, crop_id):
        "read calibrated tsums into dict"
        with open(path_to_file) as _:
            rrr = {}
            reader = csv.reader(_)
            reader.next()
            for line in reader:
                ddd = {}

                row_, col_ = line[0].split("_")
                row, col = (int(row_), int(col_))
                ddd["tsums"] = [
                    int(line[1]),
                    int(line[2]),
                    int(line[3]),
                    int(line[4]),
                    int(line[5]),
                    int(line[6])
                ]
                delta = 0
                if crop_id == "GM":
                    delta = 1
                    ddd["tsums"].append(int(line[7]))
                    ddd["CriticalTemperatureHeatStress"] = float(line[10])

                ddd["BeginSensitivePhaseHeatStress"] = 0
                ddd["EndSensitivePhaseHeatStress"] = 0
                ddd["HeatSumIrrigationStart"] = float(line[delta + delta + 9])
                ddd["HeatSumIrrigationEnd"] = float(line[delta + delta + 10])

                rrr[(row, col)] = ddd

            return rrr

    calib = {
        "GM": read_calibrated_tsums("Calibrated_TSUM_Maize.csv", "GM"),
        "WW": read_calibrated_tsums("Calibrated_TSUM_WW.csv", "WW")
    }

    def update_soil_crop_dates(row, col, crop_id):
        "update function"
        sss = soil[(row, col)]
        ppp = pheno[crop_id][(row, col)]

        extended_harvest_doy = ppp["harvest-doy"] + 10
        start_date = date(START_YEAR, 1, 1)
        sim["climate.csv-options"]["start-date"] = start_date.isoformat()
        end_date = date(2010, 12, 31)
        sim["climate.csv-options"]["end-date"] = end_date.isoformat()
        #sim["debug?"] = True

        pwp = sss["pwp"]
        fc_ = sss["fc"]
        sm_percent_fc = sss["sw-init"] / fc_ * 100.0

        is_wintercrop = ppp["sowing-doy"] > ppp["harvest-doy"]
        seeding_date = date(START_YEAR, 1, 1) + timedelta(days=ppp["sowing-doy"])
        crop["cropRotation"][0]["worksteps"][0]["date"] = seeding_date.strftime("0000-%m-%d")
        crop["cropRotation"][0]["worksteps"][0]["soilMoisturePercentFC"] = sm_percent_fc

        crop["cropRotation"][0]["worksteps"][1]["date"] = seeding_date.strftime("0000-%m-%d")
        crop["cropRotation"][0]["worksteps"][1]["crop"][2] = crop_id

        harvest_date = date(START_YEAR + (1 if is_wintercrop else 0), 1, 1) + timedelta(days=extended_harvest_doy)
        #harvest_date = date(1980, 12, 31) if crop_id == "GM" else date(1980 + (1 if is_wintercrop else 0), 1, 1) + timedelta(days=ppp["harvest-doy"])
        crop["cropRotation"][0]["worksteps"][2]["date"] = harvest_date.strftime("000" + ("1" if is_wintercrop else "0") + "-%m-%d")

        site["Latitude"] = sss["latitude"]
        top = {
            "Thickness": [0.3, "m"],
            "SoilOrganicCarbon": [sss["oc-topsoil"], "%"],
            "SoilBulkDensity": [sss["bd-topsoil"] * 1000, "kg m-3"],
            "FieldCapacity": [fc_, "m3 m-3"],
            "PermanentWiltingPoint": [pwp, "m3 m-3"],
            "PoreVolume": [sss["sat"], "m3 m-3"],
            "SoilMoisturePercentFC": [sm_percent_fc, "% [0-100]"],
            "Sand": sss["sand-topsoil"] / 100.0,
            "Clay": sss["clay-topsoil"] / 100.0
            }
        sub = {
            "Thickness": [1.7, "m"],
            "SoilOrganicCarbon": [sss["oc-subsoil"], "%"],
            "SoilBulkDensity": [sss["bd-subsoil"] * 1000, "kg m-3"],
            "FieldCapacity": [fc_, "m3 m-3"],
            "PermanentWiltingPoint": [pwp, "m3 m-3"],
            "PoreVolume": [sss["sat"], "m3 m-3"],
            "SoilMoisturePercentFC": [sm_percent_fc, "% [0-100]"],
            "Sand": sss["sand-subsoil"] / 100.0,
            "Clay": sss["clay-subsoil"] / 100.0
        }

        site["SiteParameters"]["SoilProfileParameters"] = [top, sub]
        #print site["SiteParameters"]["SoilProfileParameters"]

    print "# of rowsCols = ", len(row_cols)

    i = 0
    start_store = time.clock()
    start = config["start"] - 1
    end = config["end"] - 1
    row_cols_ = row_cols[start:end+1]
    print "running from ", start, "/", row_cols[start], " to ", end, "/", row_cols[end]
    for row, col in row_cols_:
        if soil[(row, col)]["bd-topsoil"] < 0.6: #avoid to simulate peat soils
            continue

        for crop_id in ["WW", "GM"]:
            update_soil_crop_dates(row, col, crop_id)
            env = monica_io.create_env_json_from_json_config({
                "crop": crop,
                "site": site,
                "sim": sim,
                "climate": ""
            })

            env["csvViaHeaderOptions"] = sim["climate.csv-options"]

            env["params"]["userEnvironmentParameters"]["AtmosphericCO2"] = 360

            climate_filename = "{}_{:03d}_v1.csv".format(row, col)

            #read climate data on the server and send just the path to the climate data csv file
            env["pathToClimateCSV"] = PATH_TO_CLIMATE_DATA_SERVER + climate_filename

            cal = calib[crop_id][(row, col)]
            cultivar = env["cropRotation"][0]["worksteps"][1]["crop"]["cropParams"]["cultivar"]
            cultivar["CropSpecificMaxRootingDepth"] = 1.5
            cultivar["StageTemperatureSum"] = cal["tsums"]
            cultivar["BeginSensitivePhaseHeatStress"] = 0
            cultivar["EndSensitivePhaseHeatStress"] = 0
            cultivar["HeatSumIrrigationStart"] = cal["HeatSumIrrigationStart"]
            cultivar["HeatSumIrrigationEnd"] = cal["HeatSumIrrigationEnd"]

            env["customId"] = crop_id + "|(" + str(row) + "/" + str(col) + ")"

            socket.send_json(env)
            print "sent env ", i, " customId: ", env["customId"]
            i += 1

            #break
        #break

    stop_store = time.clock()

    print "sending ", i, " envs took ", (stop_store - start_store), " seconds"
    print "ran from ", start, "/", row_cols[start], " to ", end, "/", row_cols[end]
    return


main()