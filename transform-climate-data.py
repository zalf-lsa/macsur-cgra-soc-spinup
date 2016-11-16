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

import csv
import os
import datetime

def main():
    
  def transformClimate(pathToFile, pathToOutput):
    prevPeriodGcm = ("","")
    filename = os.path.split(pathToFile)[1]
    with open(pathToFile) as f:
      reader = csv.reader(f)
      reader.next()
      of = None

      csvHeader = ["iso-date", "tmin", "tavg", "tmax", "precip", "globrad", "wind", "relhumid"]
      for row in reader:
        period, gcm = period_gcmRcp = (row[0], row[1])
        
        line = [
          datetime.datetime.strptime(row[2], "%Y%m%d").date().isoformat()
          , float(row[4])
          , (float(row[3]) + float(row[4])) / 2
          , float(row[3])
          , float(row[7])
          , float(row[8])
          , float(row[6]) / 24 / 3.6
          , (float(row[9]) + float(row[10])) / 2
          ]

        if prevPeriodGcm != period_gcmRcp:
          if of != None:
            of.close()

          fullPathToOutputDir = os.path.join(pathToOutput, period, gcm, "")
          if not os.path.exists(fullPathToOutputDir):
            os.makedirs(fullPathToOutputDir)

          of = open(fullPathToOutputDir + filename, 'wb')
          writer = csv.writer(of, delimiter = ",")
          writer.writerow(csvHeader)
          prevPeriodGcm = period_gcmRcp
        
        writer.writerow(line)

      if of != None:
        of.close()		


  pathToClimateCSVs = "A:/macsur-eu-heat-stress/"
  pathToOutput = "A:/macsur-eu-heat-stress-3/"

  files = os.listdir(pathToClimateCSVs)
  print "read directory ..."
  for f in files:
    fullPath = os.path.join(pathToClimateCSVs, f)
    
    if os.path.isfile(fullPath):
      transformClimate(fullPath, pathToOutput)
      print "transformed ", f 

main()