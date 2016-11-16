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
sys.path.insert(0, "C:\\Users\\berg.ZALF-AD\\GitHub\\monica\\project-files\\Win32\\Release")
#sys.path.insert(0, "C:\\Users\\berg.ZALF-AD\\GitHub\\monica\\project-files\\Win32\\Debug")
sys.path.insert(0, "C:\\Users\\berg.ZALF-AD\\GitHub\\monica\\src\\python")
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
PATH_TO_CLIMATE_DATA_SERVER = "/archiv-daten/md/berg/macsur-eu-heat-stress-transformed/"
PATH_TO_CLIMATE_DATA = "B:/md/berg/macsur-eu-heat-stress-transformed/"

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
            k,v = arg.split("=")
            if k in config:
                config[k] = int(v) 

    socket.bind("tcp://*:" + str(config["port"]))

    with open("sim.json") as _:
        sim = json.load(_)

    with open("site.json") as _:
        site = json.load(_)

    with open("crop.json") as _:
        crop = json.load(_)

    with open("sims.json") as _:
        sims = json.load(_)

    sim["include-file-base-path"] = "C:/Users/berg.ZALF-AD/MONICA"

    period_gcm_co2s = [
        {"id": "C1", "period": "0", "gcm": "0_0", "co2_value": 360},
        {"id": "C2", "period": "2", "gcm": "GFDL-CM3_45", "co2_value": 360},
        {"id": "C3", "period": "3", "gcm": "GFDL-CM3_45", "co2_value": 360},
        {"id": "C4", "period": "2", "gcm": "GFDL-CM3_85", "co2_value": 360},
        {"id": "C5", "period": "3", "gcm": "GFDL-CM3_85", "co2_value": 360},
        {"id": "C6", "period": "2", "gcm": "GISS-E2-R_45", "co2_value": 360},
        {"id": "C7", "period": "3", "gcm": "GISS-E2-R_45", "co2_value": 360},
        {"id": "C8", "period": "2", "gcm": "GISS-E2-R_85", "co2_value": 360},
        {"id": "C9", "period": "3", "gcm": "GISS-E2-R_85", "co2_value": 360},
        {"id": "C10", "period": "2", "gcm": "HadGEM2-ES_26", "co2_value": 360},
        {"id": "C11", "period": "3", "gcm": "HadGEM2-ES_26", "co2_value": 360},
        {"id": "C12", "period": "2", "gcm": "HadGEM2-ES_45", "co2_value": 360},
        {"id": "C13", "period": "3", "gcm": "HadGEM2-ES_45", "co2_value": 360},
        {"id": "C14", "period": "2", "gcm": "HadGEM2-ES_85", "co2_value": 360},
        {"id": "C15", "period": "3", "gcm": "HadGEM2-ES_85", "co2_value": 360},
        {"id": "C16", "period": "2", "gcm": "MIROC5_45", "co2_value": 360},
        {"id": "C17", "period": "3", "gcm": "MIROC5_45", "co2_value": 360},
        {"id": "C18", "period": "2", "gcm": "MIROC5_85", "co2_value": 360},
        {"id": "C19", "period": "3", "gcm": "MIROC5_85", "co2_value": 360},
        {"id": "C20", "period": "2", "gcm": "MPI-ESM-MR_26", "co2_value": 360},
        {"id": "C21", "period": "3", "gcm": "MPI-ESM-MR_26", "co2_value": 360},
        {"id": "C22", "period": "2", "gcm": "MPI-ESM-MR_45", "co2_value": 360},
        {"id": "C23", "period": "3", "gcm": "MPI-ESM-MR_45", "co2_value": 360},
        {"id": "C24", "period": "2", "gcm": "MPI-ESM-MR_85", "co2_value": 360},
        {"id": "C25", "period": "3", "gcm": "MPI-ESM-MR_85", "co2_value": 360},
        {"id": "C26", "period": "2", "gcm": "GFDL-CM3_45", "co2_value": 499},
        {"id": "C27", "period": "3", "gcm": "GFDL-CM3_45", "co2_value": 532},
        {"id": "C28", "period": "2", "gcm": "GFDL-CM3_85", "co2_value": 571},
        {"id": "C29", "period": "3", "gcm": "GFDL-CM3_85", "co2_value": 801},
        {"id": "C30", "period": "2", "gcm": "GISS-E2-R_45", "co2_value": 499},
        {"id": "C31", "period": "3", "gcm": "GISS-E2-R_45", "co2_value": 532},
        {"id": "C32", "period": "2", "gcm": "GISS-E2-R_85", "co2_value": 571},
        {"id": "C33", "period": "3", "gcm": "GISS-E2-R_85", "co2_value": 801},
        {"id": "C34", "period": "2", "gcm": "HadGEM2-ES_26", "co2_value": 442},
        {"id": "C35", "period": "3", "gcm": "HadGEM2-ES_26", "co2_value": 429},
        {"id": "C36", "period": "2", "gcm": "HadGEM2-ES_45", "co2_value": 499},
        {"id": "C37", "period": "3", "gcm": "HadGEM2-ES_45", "co2_value": 532},
        {"id": "C38", "period": "2", "gcm": "HadGEM2-ES_85", "co2_value": 571},
        {"id": "C39", "period": "3", "gcm": "HadGEM2-ES_85", "co2_value": 801},
        {"id": "C40", "period": "2", "gcm": "MIROC5_45", "co2_value": 499},
        {"id": "C41", "period": "3", "gcm": "MIROC5_45", "co2_value": 532},
        {"id": "C42", "period": "2", "gcm": "MIROC5_85", "co2_value": 571},
        {"id": "C43", "period": "3", "gcm": "MIROC5_85", "co2_value": 801},
        {"id": "C44", "period": "2", "gcm": "MPI-ESM-MR_26", "co2_value": 442},
        {"id": "C45", "period": "3", "gcm": "MPI-ESM-MR_26", "co2_value": 429},
        {"id": "C46", "period": "2", "gcm": "MPI-ESM-MR_45", "co2_value": 499},
        {"id": "C47", "period": "3", "gcm": "MPI-ESM-MR_45", "co2_value": 532},
        {"id": "C48", "period": "2", "gcm": "MPI-ESM-MR_85", "co2_value": 571},
        {"id": "C49", "period": "3", "gcm": "MPI-ESM-MR_85", "co2_value": 801}
    ]

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

                ddd["BeginSensitivePhaseHeatStress"] = float(line[delta + 7])
                ddd["EndSensitivePhaseHeatStress"] = float(line[delta + 8])
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
        start_date = date(1980, 1, 1) + timedelta(days=ppp["sowing-doy"])
        sim["climate.csv-options"]["start-date"] = start_date.isoformat()
        end_date = date(2010, 1, 1) + timedelta(days=extended_harvest_doy)
        sim["climate.csv-options"]["end-date"] = end_date.isoformat()
        #sim["debug?"] = True

        pwp = sss["pwp"]
        fc_ = sss["fc"]
        sm_percent_fc = sss["sw-init"] / fc_ * 100.0

        is_wintercrop = ppp["sowing-doy"] > ppp["harvest-doy"]
        seeding_date = date(1980, 1, 1) + timedelta(days=ppp["sowing-doy"])
        crop["cropRotation"][0]["worksteps"][0]["date"] = seeding_date.strftime("0000-%m-%d")
        crop["cropRotation"][0]["worksteps"][0]["soilMoisturePercentFC"] = sm_percent_fc

        crop["cropRotation"][0]["worksteps"][1]["date"] = seeding_date.strftime("0000-%m-%d")
        crop["cropRotation"][0]["worksteps"][1]["crop"][2] = crop_id
        
        harvest_date = date(1980 + (1 if is_wintercrop else 0), 1, 1) + timedelta(days=extended_harvest_doy)
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

    def read_climate(path_to_file):
        "read climate data locally"

        def csv_to_string(data):
            sii = StringIO()
            cww = csv.writer(sii)
            cww.writerow(data)
            return sii.getvalue().strip('\r\n')

        #climate_csv_string = ""
        #last_in_section = False
        with open(path_to_file) as f:
            ccc = {}
            reader = csv.reader(f)
            reader.next()

            csv_header = csv_to_string(["iso-date", "tmin", "tavg", "tmax", "precip", "globrad", "wind", "relhumid"]) + "\n"
            prev = ("", "")
            for row in reader:
                period_gcm_rcp = (row[0], row[1])

                line = [
                    datetime.strptime(row[2], "%Y%m%d").date().isoformat(),
                    float(row[4]),
                    (float(row[3]) + float(row[4])) / 2,
                    float(row[3]),
                    float(row[7]),
                    float(row[8]),
                    float(row[6]) / 24 / 3.6,
                    (float(row[9]) + float(row[10])) / 2,
                ]
                if prev != period_gcm_rcp:
                    print period_gcm_rcp
                    prev = period_gcm_rcp

                ccc[period_gcm_rcp] = ccc.get(period_gcm_rcp, csv_header) + csv_to_string(line) + "\n"

            return ccc


    assert len(row_cols) == len(pheno["GM"].keys()) == len(pheno["WW"].keys())
    print "# of rowsCols = ", len(row_cols)

    read_climate_data_locally = False
    i = 0
    start_store = time.clock()
    start = config["start"] - 1
    end = config["end"] - 1
    row_cols_ = row_cols[start:end+1]
    print "running from ", start, "/", row_cols[start], " to ", end, "/", row_cols[end]
    for row, col in row_cols_:
        for crop_id in ["WW", "GM"]:
            update_soil_crop_dates(row, col, crop_id)
            env = monica_io.create_env_json_from_json_config({
                "crop": crop,
                "site": site,
                "sim": sim,
                "climate": ""
            })
            if not read_climate_data_locally:
                env["csvViaHeaderOptions"] = sim["climate.csv-options"]

            for pgc in period_gcm_co2s:
                co2_id = pgc["id"]
                co2_value = pgc["co2_value"]
                period = pgc["period"]
                gcm = pgc["gcm"]

                env["params"]["userEnvironmentParameters"]["AtmosphericCO2"] = co2_value

                climate_filename = "{}_{:03d}_v1.csv".format(row, col)
                #if not os.path.exists(path_to_climate_file):
                #    continue

                #read climate data on client and send them with the env
                if read_climate_data_locally:
                    path_to_climate_file = os.path.join(PATH_TO_CLIMATE_DATA, period, gcm, climate_filename)
                    with open(path_to_climate_file) as cf_:
                        climate_data = cf_.read()
                    monica_io.add_climate_data_to_env(env, sim, climate_data)
                else:
                    #read climate data on the server and send just the path to the climate data csv file
                    env["pathToClimateCSV"] = PATH_TO_CLIMATE_DATA_SERVER + period + "/" + gcm + "/" + climate_filename

                env["events"] = sims["output"][crop_id]

                for sim_ in sims["treatments"]:
                    env["params"]["simulationParameters"]["UseAutomaticIrrigation"] = sim_["UseAutomaticIrrigation"]
                    env["params"]["simulationParameters"]["AutoIrrigationParams"]["amount"] = sims["irrigation-amount"][crop_id]

                    cal = calib[crop_id][(row, col)]
                    cultivar = env["cropRotation"][0]["worksteps"][1]["crop"]["cropParams"]["cultivar"]
                    cultivar["CropSpecificMaxRootingDepth"] = 1.5
                    cultivar["StageTemperatureSum"] = cal["tsums"]
                    if "SensitivePhaseHeatStress" in sim_:
                        cultivar["BeginSensitivePhaseHeatStress"] = cal["BeginSensitivePhaseHeatStress"] if sim_["SensitivePhaseHeatStress"] else 0
                        cultivar["EndSensitivePhaseHeatStress"] = cal["EndSensitivePhaseHeatStress"] if sim_["SensitivePhaseHeatStress"] else 0
                    if crop_id == "GM":
                        cultivar["CriticalTemperatureHeatStress"] = cal["CriticalTemperatureHeatStress"]
                    if "HeatSumIrrigation" in sim_ and sim_["HeatSumIrrigation"]:
                        cultivar["HeatSumIrrigationStart"] = cal["HeatSumIrrigationStart"]
                        cultivar["HeatSumIrrigationEnd"] = cal["HeatSumIrrigationEnd"]

                    env["customId"] = crop_id \
                                        + "|(" + str(row) + "/" + str(col) + ")" \
                                        + "|" + period \
                                        + "|" + gcm \
                                        + "|(" + co2_id + "/" + str(co2_value) + ")" \
                                        + "|" + sim_["TrtNo"] \
                                        + "|" + sim_["Irrig"] \
                                        + "|" + sim_["ProdCase"]

                    socket.send_json(env)
                    print "sent env ", i, " customId: ", env["customId"]
                    i += 1
                    #break
                #break
            #break
        #break

    stop_store = time.clock()

    print "sending ", i, " envs took ", (stop_store - start_store), " seconds"
    print "ran from ", start, "/", row_cols[start], " to ", end, "/", row_cols[end]
    return


main()