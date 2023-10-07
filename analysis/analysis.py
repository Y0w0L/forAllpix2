import os
import os.path as path
from tqdm import tqdm
import ROOT
import cupy as cp
import argparse
from ROOT import gSystem

#rootfileから読み込むマクロ

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


# get data for muon stepLength from MCParticle
def getDistance():
    for i in tqdm(range(0, McParticle.GetEntries())):
        McParticle.GetEntry(i)
        McParticle_branch   = McParticle.GetBranch("mydetector")
        br_mc_partP         = getattr(McParticle, McParticle_branch.GetName())

        startPoint  = None
        endPoint    = None


        for mc_partP in br_mc_partP:
            if abs(mc_partP.getParticleID()) == 13:
                startPoint      = mc_partP.getLocalStartPoint()
                endPoint        = mc_partP.getLocalEndPoint()
                direction       = startPoint - endPoint
                xLength         = startPoint.x() - endPoint.x()
                yLength         = startPoint.y() - endPoint.y()
                zLength         = startPoint.z() - endPoint.z()
                distance        = cp.sqrt(xLength*xLength + yLength*yLength + zLength*zLength)
                print("distance = ", distance)
                h1.Fill(distance)

    print("end distance")
    return distance


# get data for muon energy deposit from MCTrack
def getEnergyDeposit():
    for i in tqdm(range(0, McTrack.GetEntries())):
        McTrack.GetEntry(i)
        McTrack_branch     = McTrack.GetBranch("global")
        br_mc_partT        = getattr(McTrack, McTrack_branch.GetName())

        startEnergy = None
        endEnergy   = None

        for mc_partT in br_mc_partT:
            if abs(mc_partT.getParticleID()) == 13:
                startEnergy     = mc_partT.getTotalEnergyInitial()
                endEnergy       = mc_partT.getTotalEnergyFinal()
                energyDeposit   = startEnergy - endEnergy
                print("energy deposition = ", energyDeposit)
                h2.Fill(energyDeposit)

    print("end energy")
    return energyDeposit




# make histogram for ROOT
gSystem.Load(lib_file_name)

rootFile    = ROOT.TFile("../output/data/data2.root")
outputFile  = ROOT.TFile.Open("../plot/plot.root", "RECREATE")
McParticle  = rootFile.Get('MCParticle')
McTrack     = rootFile.Get('MCTrack')

canvas      = ROOT.TCanvas("canvas")
#canvas.Divide(1,2)
h1          = ROOT.TH1D("data1","distance", 100, 0, 0.03)
h2          = ROOT.TH1D("data2","Energy deposit", 100, 0, 0.1)
getDistance()
getEnergyDeposit()

#canvas.cd(1)
#h1.Draw()

#canvas.cd(2)
h2.Draw()

canvas.Write()
canvas.Print("../plot/plot.pdf")
outputFile.Close()
 
