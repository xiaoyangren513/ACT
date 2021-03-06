#
# Copyright (c) 2020 Avalanche Studios. All rights reserved.
# Licensed under the MIT License.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE
#
#--------------------------------------------------------------------------------------
# File: RenderFromACameraSwitcher.py
#
# The script has a project/pipeline specified functions, the legacy realization of them are listened in public_common.py. 
# Please see "How to Use" section for more information.
#
# NOTE: The script is created to work with 60 fps scene files!
#
# This is an action script.
#  The script will switch to camera switcher and render scene into a file
# Features:
# * It will use *.mov format and x264 codec
# * If you have p4 (perforce) module installed, you can add renderer file into a new change list
# * in public_common.py you can find general pipeline function for sanitize relative path to your project
#      and a function to add render files to your version control system
#  Customize public_common functions depends on your needs.
#-------------------------------------------------------------------------------------

import os
from pyfbsdk import *

from project_common import GetSanitizedRelPath, AddFileToChangeList

g_System = FBSystem()
g_App = FBApplication()

g_TimeStep = 1 # for 60 fps animation file, put 2 here to have 30 fps output video
g_RenderAudio = True

# DONE: Render camera switcher
def RenderTake(file_name):
    
    options = FBVideoGrabber().GetOptions()
                  
    # Set VideoCodec Option:
    VideoManager = FBVideoCodecManager()
    VideoManager.VideoCodecMode = FBVideoCodecMode.FBVideoCodecStored
    
    codeclist = FBStringList()
    codeclist = VideoManager.GetCodecIdList('MOV')

    for item in codeclist:
        if item.find('x264') >= 0: 
            VideoManager.SetDefaultCodec('MOV', item)
    VideoManager.SetDefaultCodec('MOV', 'x264')
        
    # DONE: take a scene filename, otherwise ask user for a file path

    options.OutputFileName = file_name
    options.CameraResolution = FBCameraResolutionMode.kFBResolutionFullScreen
    options.AntiAliasing = True
    options.ShowTimeCode = True
    options.ShowCameraLabel = True
    # for 60 fps lets white video in half frame rate
    options.TimeSpan = FBTimeSpan(FBTime(0,0,0,0), FBTime(0,0,0,0))
    options.TimeSteps = FBTime(0,0,0, g_TimeStep) 
    
    # Audio
    options.RenderAudio = g_RenderAudio
    
    if g_RenderAudio:

        lNewFormat  = FBAudioFmt_ConvertBitDepthMode( FBAudioBitDepthMode.kFBAudioBitDepthMode_16 )
        lNewFormat |= FBAudioFmt_ConvertRateMode( FBAudioRateMode.kFBAudioRateMode_48000 )
        lNewFormat |= FBAudioFmt_ConvertChannelMode( FBAudioChannelMode.kFBAudioChannelModeStereo )
        options.AudioRenderFormat = lNewFormat
        
    # On Mac OSX, QuickTime renders need to be in 32 bits.

    lRenderFileFormat = '.mov'
    # Only windows supports mov.
    if lRenderFileFormat == '.mov' and os.name != 'nt':
        options.BitsPerPixel = FBVideoRenderDepth.FBVideoRender32Bits
    
    # Do the render. This will always be done in uncompressed mode.
    g_App.FileRender( options )
    
#
#

file_name = g_App.FBXFileName
if len(file_name) == 0:
    FBMessageBox('Render Scene', "Sorry, the current scene doesn't have a name", "Ok")
else:
    export_path = BuildAnExportPath(file_name)
    
    # switch to a camera switcher on a current pane
    index = g_System.Renderer.GetSelectedPaneIndex()
    if g_System.Renderer.IsCameraSwitcherInPane(index) == False:
        g_System.Renderer.SetCameraSwitcherInPane(index, True)    
    
    RenderTake(export_path)
    rel_path = GetSanitizedRelPath(export_path)
    AddFileToChangeList(file_name=export_path, description="Motionbuilder Export from <{}>".format(str(rel_path)))
