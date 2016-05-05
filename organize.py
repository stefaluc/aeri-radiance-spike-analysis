#!/usr/bin/env python

import os, glob, tarfile

tars = glob.glob("*.tar.v0")

for tarstring in tars:
    yymmdd = tarstring[15:21]
    print '\nProcessing %s'%tarstring
    newdir = 'AE%s' %yymmdd
    print 'Creating new directory %s/' %newdir
    os.mkdir(newdir)
    print 'Extracting %s to %s/' %(tarstring,newdir)
    print '---------------------------------------------------------------'
    tar = tarfile.open(tarstring)
    files_to_extract = ['B1.CXS', 'B2.CXS', 'F1.CXS', 'F2.CXS', '.PAR', 'B1.UVS', 'B2.UVS',
                        'F1.UVS', 'F2.UVS']
    for files in files_to_extract:
        namefull = tar.getmembers()[0].name
        namepart = namefull[:len(namefull)-4]
        print 'Extracting %s%s' %(namepart,files)
        tar.extract('%s%s'%(namepart,files), '%s/'%newdir)
    print '\nRenaming files'
    print '---------------------------------------------------------------'
    for extracted in glob.glob('./%s/*'%newdir):
        #for PAR files
        if len(extracted) == 54:
            os.rename('%s' % extracted, './%s/%s' % (newdir, extracted[-10:]))
            print 'Renaming %s to %s' % (extracted, extracted[-10:])
        else:
            os.rename('%s' % extracted, './%s/%s' % (newdir, extracted[-12:]))
            print 'Renaming %s to %s' % (extracted, extracted[-12:])
