import os, csv
import pandas as pd
import numpy as np
path = '/Users/lstefanski/aeri_data/sgp-c1-errors/cxs/'
dates = os.listdir(path)

#create dict of all data files
#key = parent directory name (AEYYMMDD), value = list of all .cxs files in parent directory
all_files = {}
for i in range(0,len(dates)):
    all_files[dates[i]] = os.listdir('%s%s/'%(path,dates[i]))

scenes = ['H', 'A', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

for date,cxs in sorted(all_files.items()):
    for i in range(0,len(cxs)):
        currfile = cxs[i]
        print currfile
        #rad = get_complex_radiance_from_rnc('/Users/lstefanski/aeri_data/sgp-c1-errors/AE150301/150301F2.CXS')
                
        rad = get_complex_radiance_from_rnc('%s%s/%s'%(path,date,currfile))
        
        #trim radiance to first 500 values to speed up computation of interferogram
        radTrim = rad.T.iloc[:500]
        #apply hanning apodization function to make the resulting trimmed function more smoothly varying
        radTrimApodization = radTrim.T.mul(np.hanning(500))
        interferogram = get_interferogram_from_spectrum(radTrimApodization)
        
        #loop through every scene in interferogram
        for scene in scenes:
            try:
                spikeTimes = []
                #trim interferogram to curr scene
                interferogram_scene = interferogram.xs(scene, level='scene')
                hasSpike = [i for i in range(0,len(interferogram_scene))]
                for i in range(0,len(interferogram_scene)):
                    hasSpike[i] = False
                    for val in interferogram_scene.ix[i].iloc[-300:]:
                        #if any value is above or below 0.0025, a spike will be present
                        if val > -0.0025 and val < 0.0025:
                            continue
                        hasSpike[i] = True
                        spikeTimes.append([currfile, scene, interferogram_scene.index[i]])
                        break
                false = 0; true = 0
                for i in hasSpike:
                    if i is False:
                        false += 1
                    else: 
                        true += 1
                
                csvlist = [currfile, scene, true, false, false+true]

                with open('/Users/lstefanski/aeri_data/sgp-c1-errors/scene-data/%s-count.csv' % scene,'a') as f:
                    w = csv.writer(f)
                    w.writerow(csvlist)

                with open('/Users/lstefanski/aeri_data/sgp-c1-errors/scene-data/%s-times.csv' % scene,'a') as f:
                    w = csv.writer(f)
                    w.writerows(spikeTimes[:])
            except:
                print '%s does not have scene %s' % (currfile, scene)
