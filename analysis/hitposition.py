import os
import os.path as path
from tqdm import tqdm
import ROOT
import cupy as cp
import argparse
from ROOT import gSystem

# argument parser
parser = argparse.ArgumentParser()
parser.add_argument("-l", metavar='libAllpixObjects', required=False,
                    help="specify path to the libAllpixObjects library (generally in allpix-squared/lib/)) ")
args = parser.parse_args()

if args.l is not None:  # Try to find Allpix Library
    lib_file_name = (str(args.l))
else:  # Look in LD_LIBRARY_PATH
    libraryPaths = os.environ['LD_LIBRARY_PATH'].split(':')
    for p in libraryPaths:
        if path.isfile(path.join(p, "libAllpixObjects.so")):
            lib_file_name = path.join(p, "libAllpixObjects.so")
            break

if (not os.path.isfile(lib_file_name)):
    print("WARNING: ", lib_file_name, " does not exist, exiting")
    exit(1)

def getPixelHit():

    pixelHit = rootFile.Get('PixelHit')

    for i in tqdm(range(0, pixelHit.GetEntries())):
        pixelHit.GetEntry(i)
        pixelHit_branch = pixelHit.GetBranch("mydetector")
        br_pixel_hit = getattr(pixelHit, pixelHit_branch.GetName())
        
        signal = None
        pixel = None
        localTime = None
        globalTime = None

        for pixel_hit in br_pixel_hit:
            signal = pixel_hit.getSignal()
            pixel = pixel_hit.getPixel()#多分どのピクセルに当たったかの情報が入っていると思う
            localTime = pixel_hit.getLocalTime()
            globalTime = pixel_hit.getGlobalTime()
            h1.Fill(signal)

    return signal,pixel,localTime,globalTime

def getPixelCharge():

    pixelCharge = rootFile.Get('PixelCharge')

    for i in tqdm(range(0, pixelCharge.GetEntries())):
        pixelCharge.GetEntry(i)
        pixelCharge_branch = pixelCharge.GetBranch("mydetector")
        br_pixel_charge = getattr(pixelCharge, pixelCharge_branch.GetName())

        localTime = None
        globalTime = None

        for pixel_charge in br_pixel_charge:
            localTime = pixel_charge.getLocalTime()
            globalTime = pixel_charge.getGlobalTime()
            print("local global time = ", localTime," : ", globalTime)

    return localTime, globalTime

def getPulse():
    
    pulse_dir = rootFile.Get('Pulse')

    for i in tqdm(range(0, pulse_dir.GetEntries())):
        pulse_dir.GetEntry(i)
        pulse_branch = pulse_dir.GetBranch("mydetector")
        br_pulse_data = getattr(pulse_dir, pulse_branch.GetName())

        binning = None

        for pulse_data in br_pulse_data:
            binning = pulse_data.getBinning()
            print("binning time = ", binning)

    return binning

    
# make histogram for ROOT
gSystem.Load(lib_file_name)

rootFile    = ROOT.TFile("../output/data/data2.root")

canvas = ROOT.TCanvas("canvas")

h1 = ROOT.TH1D("data", "signal", 5000, 0, 5000)
getPixelHit()
h1.Draw()

h2 = ROOT.TH1D("data", "time", 100, 0, 100)
getPixelCharge()

getPulse()

outputFile  = ROOT.TFile.Open("../plot/plot2.root", "RECREATE")
canvas.Write()
outputFile.Close()
