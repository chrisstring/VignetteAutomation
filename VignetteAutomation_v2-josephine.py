#!/usr/bin/env python2.7

# Date created      : 09-20-2016
# File name         : VignetteAutomation_v2.py
# Author            : Topher Null, Post-Production, Turn5 Inc
# Python Version    : 2.7
# Description       : This python script creates vignette files (.vnt) using the Scene7 Image Authoring - Vignette Authoring Tool
# Prerequisites     :   1. Folder "InputFiles" should exist in the same folder as this python file
#                       2. The InputFiles folder should contain two types of files - for example:
#                           a) J104707_alt4.psd         : This is the base image file in *.psd format.
#                           b) J104707_alt4-mask.png    : This is the mask file in *.png format, to be applied to the base file.
#                                                         This file must have the same filename as the base file in (a) appended with the "-mask" suffix.
# Output            : The "OutputFiles" folder is re-created on every run. For each qualifying pair of the input files, an output file
#                     with the same filename with .vnt extension is created. (eg. J104707_alt4.vnt).
#                     Log.txt file will contain logs for each file in the "InputFiles" folder.
#
# History       
# Version   Date          Modifer             Comment
# 1.0       09-20-2016    Dixant Rai          Created
# 1.1       10-14-2016    Dixant Rai          Adjusted script so that main image file without "_alt" are also be processed.

import datetime
import time
import os
import shutil
import fnmatch
from os.path import splitext
from s7vampy import *

# set working dir to the location of this python file
dir_path = os.path.dirname(os.path.realpath('__file__'))
log_path = os.path.join(dir_path,'log.txt')

def writetolog(textfile,text):
    f = open(textfile,'a')
    ts = time.time()
    timestamp = str(datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S'))
    f.write(timestamp + '\t' + text + '\n')
    f.close()

def ignore_patterns(*patterns):
    """Function that can be used as copytree() ignore parameter.
    Patterns is a sequence of glob-style patterns
    that are used to exclude files"""
    def _ignore_patterns(path, names):
        ignored_names = []
        for pattern in patterns:
            ignored_names.extend(fnmatch.filter(names, pattern))
        return set(ignored_names)
    return _ignore_patterns

def copyDirectory(src, dest):
    # delete destination path if it exist
    if os.path.exists(dest):
        shutil.rmtree(dest)
        
    try:
        shutil.copytree(src, dest,ignore=ignore_patterns('*.*'))
    # Directories are the same
    except shutil.Error as e:
        writetolog(log_path,'Directory not copied. Error: %s' % e)
    # Any error saying that the directory doesn't exist
    except OSError as e:
        writetolog(log_path,'Directory not copied. Error: %s' % e)

def createVignette(parent_file,mask_file,group_name,nontexturable_obj_name,log_path):
    vignette_file = parent_file.replace('.psd','.vnt')
    vignette_file = vignette_file.replace('InputFiles','OutputFiles')
    v = create_vignette(open_image(parent_file))
    v.view.illum[0] = open_image(parent_file)
    group = v.objects.add_group(group_name)
    obj = group.add_nontexturable_object(nontexturable_obj_name, open_image(mask_file)) 
    try:
        v.save(vignette_file)
    except OSError as e:
        writetolog(log_path,'\t Error: %s' % e)

def main():   
    # set working dir to the location of this python file
    dir_path = os.path.dirname(os.path.realpath('__file__'))

    # set source, destination and log file paths
    source_path = os.path.join(dir_path, 'InputFilesJosephine')
    dest_path = os.path.join(dir_path, 'OutputFilesJosephine')
    log_path = os.path.join(dir_path,'josephinelog.txt')

    # replicated directory structure from source to destination
    copyDirectory(source_path, dest_path)

    writetolog(log_path,'****Begin Process***')

    # traverse source_path to find base *.psd images
    for dirName, subdirList, fileList in os.walk(source_path):
        subdir = subdirList or '*Root*'
        writetolog(log_path,'Directory: %s' % subdir)
        for fname in fileList:
            # only process *.psd files
            if (splitext(fname)[1].lower() == '.psd'):
                # only process images for which a corresponding '*-mask.png' file exists
                if os.path.exists(os.path.join(dirName, fname.replace('.psd','-mask.png'))):
                    parent = os.path.join(dirName, fname)
                    mask = os.path.join(dirName, fname.replace('.psd','-mask.png'))
                    createVignette(parent,mask,'car','color',log_path)
                    print("processing "+fname)
                    writetolog(log_path,'\t{0:50} : Successfully processed'.format(fname))
                else:
                    # writetolog(log_path,'\t%s' % fname + ' : Not Processed - corresponding file %s does not exist' % fname.replace('.psd','-mask.png'))
                    writetolog(log_path,'\t{0:50} : Not Processed - corresponding file [%s] does not exist'.format(fname) % fname.replace('.psd','-mask.png'))
                    print '\t{0:50} : Not Processed - corresponding file [%s] does not exist'.format(fname)
    writetolog(log_path,'****End Process***' + '\n')

if __name__ == '__main__':
   main()
