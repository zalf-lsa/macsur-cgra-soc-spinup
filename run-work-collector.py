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

import sys
sys.path.insert(0, "C:\\Users\\berg.ZALF-AD\\GitHub\\monica\\project-files\\Win32\\Release")
sys.path.insert(0, "C:\\Users\\berg.ZALF-AD\\GitHub\\monica\\src\\python")
print sys.path

import gc
import csv
import types
import os
from datetime import datetime
from collections import defaultdict

import zmq
#print zmq.pyzmq_version()
import monica_io
#print "path to monica_io: ", monica_io.__file__

#log = open("errors.txt", 'w')

#gc.enable()

def create_output(row, col, crop_id, co2_id, co2_value, period, gcm, trt_no, irrig, prod_case, result):
    "create crop output lines"

    out = []
    if len(result.get("data", [])) > 0 and len(result["data"][0].get("results", [])) > 0:
        for kkk in range(0, len(result["data"][0]["results"][0])):
            vals = {}

            for data in result.get("data", []):
                results = data.get("results", [])
                oids = data.get("outputIds", [])

                #skip empty results, e.g. when event condition haven't been met
                if len(results) == 0:
                    continue

                assert len(oids) == len(results)
                for iii in range(0, len(oids)):
                    oid = oids[iii]

                    name = oid["name"] if len(oid["displayName"]) == 0 else oid["displayName"]

                    if len(results[iii]) < kkk+1:
                        #log.write("(" + str(row) + "/" + str(col) + ")|" + crop_id 
                        #          + "|" + period + "|" + gcm + "|" + trt_no + "|" + irrig 
                        #          + "|" + prod_case + " oid: " + name + " -> only " + str(len(results[iii])) + " years available\n")
                        break

                    val = results[iii][kkk]

                    if isinstance(val, types.ListType):
                        for val_ in val:
                            vals[name] = val_
                    else:
                        vals[name] = val

            if crop_id == "WW" or vals.get("Year", 0) > 1980:
                out.append([
                    "MO",
                    str(row) + "_" + str(col),
                    "Maize" if crop_id == "GM" else "WW",
                    co2_id,
                    period,
                    gcm,
                    str(co2_value),
                    trt_no,
                    irrig,
                    prod_case,
                    vals.get("Year", "na"),
                    vals.get("Yield", "na"),
                    vals.get("AntDOY", "na"),
                    vals.get("MatDOY", "na"),
                    vals.get("GNumber", "na"),
                    vals.get("Biom-an", "na"),
                    vals.get("Biom-ma", "na"),
                    vals.get("MaxLAI", "na"),
                    vals.get("WDrain", "na"),
                    vals.get("CumET", "na"),
                    vals.get("SoilAvW", "na") * 100.0,
                    vals.get("Runoff", "na"),
                    vals["CumET"] - vals["Evap"] if "CumET" in vals and "Evap" in vals else "na",
                    vals.get("Evap", "na"),
                    vals.get("CroN-an", "na"),
                    vals.get("CroN-ma", "na"),
                    vals.get("GrainN", "na"),
                    vals.get("Eto", "na"),
                    vals.get("SowDOY", "na"),
                    vals.get("EmergDOY", "na"),
                    vals.get("TcMaxAve", "na"),
                    vals.get("TMAXAve", "na")
                ])

    return out


HEADER = "Model,row_col,Crop,ClimPerCO2_ID,period," \
         + "sce,CO2,TrtNo,Irrigation,ProductionCase," \
         + "Year,Yield,AntDOY,MatDOY,GNumber,Biom-an,Biom-ma," \
         + "MaxLAI,WDrain,CumET,SoilAvW,Runoff,Transp,Evap,CroN-an,CroN-ma," \
         + "GrainN,Eto,SowDOY,EmergDOY,TcMaxAve,TMAXAve" \
         + "\n"

def write_data(row, col, data):
    "write data"

    path_to_file = "out/EU_HS_MO_" + str(row) + "_" + str(col) + "_output.csv"

    if not os.path.isfile(path_to_file):
        with open(path_to_file, "w") as _:
            _.write(HEADER)

    with open(path_to_file, 'ab') as _:
        writer = csv.writer(_, delimiter=",")
        for row_ in data[(row, col)]:
            writer.writerow(row_)
        data[(row, col)] = []
        #gc.collect()


def collector():
    "collect data from workers"

    data = defaultdict(list)

    i = 0
    context = zmq.Context()
    socket = context.socket(zmq.PULL)
    socket.bind("tcp://*:7777")
    socket.RCVTIMEO = 1000
    leave = False
    write_normal_output_files = False
    start_writing_lines_threshold = 5880
    while not leave:

        try:
            #result = socket.recv_json()
            result = socket.recv_json(encoding="latin-1")
            #result = socket.recv_string(encoding="latin-1")
            #result = socket.recv_string()
            #print result
            #with open("out/out-latin1.csv", "w") as _:
            #    _.write(result)
            #continue
        except:
            for row, col in data.keys():
                if len(data[(row, col)]) > 0:
                    write_data(row, col, data)
            continue

        if result["type"] == "finish":
            print "received finish message"
            leave = True

        elif not write_normal_output_files:
            print "received work result ", i, " customId: ", result.get("customId", "")

            custom_id = result["customId"]
            ci_parts = custom_id.split("|")
            crop_id = ci_parts[0]
            row_, col_ = ci_parts[1][1:-1].split("/")
            row, col = (int(row_), int(col_))
            period = ci_parts[2]
            gcm = ci_parts[3]
            co2_id, co2_value_ = ci_parts[4][1:-1].split("/")
            co2_value = int(co2_value_)
            trt_no = ci_parts[5]
            irrig = ci_parts[6]
            prod_case = ci_parts[7]

            res = create_output(row, col, crop_id, co2_id, co2_value, period, gcm, trt_no, irrig, prod_case, result)
            data[(row, col)].extend(res)

            if len(data[(row, col)]) >= start_writing_lines_threshold:
                write_data(row, col, data)

            i = i + 1

        elif write_normal_output_files:
            print "received work result ", i, " customId: ", result.get("customId", "")

            with open("out/out-" + str(i) + ".csv", 'wb') as _:
                writer = csv.writer(_, delimiter=",")

                for data_ in result.get("data", []):
                    results = data_.get("results", [])
                    orig_spec = data_.get("origSpec", "")
                    output_ids = data_.get("outputIds", [])

                    if len(results) > 0:
                        writer.writerow([orig_spec.replace("\"", "")])
                        for row in monica_io.write_output_header_rows(output_ids,
                                                                      include_header_row=True,
                                                                      include_units_row=True,
                                                                      include_time_agg=False):
                            writer.writerow(row)

                        for row in monica_io.write_output(output_ids, results):
                            writer.writerow(row)

                    writer.writerow([])

            i = i + 1


collector()

#log.close()
