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
#sys.path.insert(0, "C:\\Users\\stella\\Documents\\GitHub\\monica\\project-files\\Win32\\Release")
#sys.path.insert(0, "C:\\Users\\stella\\Documents\\GitHub\\monica\\src\\python")
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

def create_output(row, col, crop_id, result):
    "create crop output lines"

    out = []
    if len(result.get("data", [])) > 0 and len(result["data"][0].get("results", [])) > 0:
        prev_vals = {}
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

            out.append([
                str(row) + "_" + str(col),
                "Maize" if crop_id == "GM" else "WW",
                vals.get("Year", "na"),
                vals.get("SOCtop", "na"),
                vals.get("SOCbottom", "na"),
                (vals["SOCtop"] - prev_vals["SOCtop"]) / prev_vals["SOCtop"] if "SOCtop" in vals and "SOCtop" in prev_vals else "na",
                (vals["SOCbottom"] - prev_vals["SOCbottom"]) / prev_vals["SOCbottom"] if "SOCbottom" in vals and "SOCbottom" in prev_vals else "na",
                vals["NO3"] + vals["NH4"] if "NO3" in vals and "NH4" in vals else "na",                   
                vals.get("NLeach", "na"),
                vals.get("Rh", "na"),
                vals.get("NEP", "na"),
                vals.get("Yield", "na")
            ])
            
            #out.append([
            #    str(row) + "_" + str(col),
            #    "WW",
            #    vals.get("Year", "na"),
            #    vals.get("Tmin", "na"),
            #    vals.get("Tavg", "na"),
            #    vals.get("Tmax", "na"),
            #    vals.get("Precip", "na"),
            #    vals.get("Globrad", "na"),
            #])


            prev_vals = vals

    return out


HEADER = "row_col,Crop," \
         + "Year,SOCtop,SOCbottom,DeltaSOCtop,DeltaSOCbottom,Nmin,NLeach,Rh,NEP,Yield" \
         + "\n"
#+ "Year,Tmin,Tavg,Tmax,Precip,Globrad" \
         
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
    #socket.connect("tcp://localhost:7777")
    socket.connect("tcp://cluster2:7777")
    socket.RCVTIMEO = 1000
    leave = False
    write_normal_output_files = False
    start_writing_lines_threshold = 30
    while not leave:

        try:
            result = socket.recv_json(encoding="latin-1")
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

            res = create_output(row, col, crop_id, result)
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
