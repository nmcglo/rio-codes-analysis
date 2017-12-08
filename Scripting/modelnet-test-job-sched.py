import shlex
import re
import subprocess
import json
import collections


#PARAMS
SYNCH = 3
MAX_POWER_OF_RANKS = 5

BINARY_PATH = "/home/mcglon/RossDev/codes/build/tests/modelnet-test"
MAPPING_PATH = "/home/mcglon/RossDev/codes/build/tests/conf/modelnet-test-neil.conf"
NKP = 2
OFFICIAL_END = 1000

METRICS_MONITORED = ["Total Nodes", "Total LPs", "Efficiency", "Net Events Processed", "Running Time"]
METRICS_EXCLUDED = ["Total Time"] #put metrics here that you don't want that are falsely triggered by the regex search
#ENDPARAMS

ranksToRun = [2**x for x in range(MAX_POWER_OF_RANKS+1)]
simDict = collections.OrderedDict()

def initDicts():
    simDict["baseline"] = collections.OrderedDict()
    simDict["checkpoint"] = collections.OrderedDict()
    simDict["restart"] = collections.OrderedDict()

    for key in simDict:
        for numRanks in ranksToRun:
            simDict[key][numRanks] = collections.OrderedDict()

def buildCommand(numRanks, binPath, synch, mapPath, iostore, nkp, endtime):
    command = "mpirun -n %d %s --synch=%d --mapping-conf=%s --io-store=%d --nkp=%d --end=%d --io-evt-ts-mode=1 --extramem=2000000" % (numRanks, binPath, synch, mapPath, iostore, nkp, endtime)
    return command

def runSim(numRanks, binPath, synch, mapPath, iostore, nkp, endtime, metricDict):
    command = buildCommand(numRanks, binPath, synch, mapPath, iostore, nkp, endtime)
    print("Executing: " + command)
    args = shlex.split(command)

    proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    out, err = proc.communicate()

    for line in out.splitlines():
        line = re.sub('[=:%]|(seconds)', '', line)
        line = line.strip()

        for metric in METRICS_MONITORED:
            if re.search(metric, line):
                excluded_found = False
                for excluded_metric in METRICS_EXCLUDED:
                    if re.search(excluded_metric, line):
                        excluded_found = True
                if not excluded_found:
                    pair = re.split('^(%s)'% metric, line)
                    pair.pop(0)
                    pair[-1] = pair[-1].strip()
                    metricDict[pair[0]] = float(pair[1])
                    print(pair)
    print("-----------\n")

def exportDicts(filename):
    with open(filename, "w") as f:
        f.write(json.dumps(simDict,indent=4))



def main():
    initDicts();

    print("***** BASELINE STATS ********************************\n")

    for i,numRanks in enumerate(ranksToRun):
        runSim(numRanks, BINARY_PATH, SYNCH, MAPPING_PATH, 2, NKP, OFFICIAL_END,simDict["baseline"][numRanks])

    print("***** WITH RIO CHECKPOINT/RESTART ********************************\n")

    for i,numRanks in enumerate(ranksToRun):
        print("--CHECKPOINT RUN--")
        runSim(numRanks, BINARY_PATH, SYNCH, MAPPING_PATH, 1, NKP, OFFICIAL_END/2,simDict["checkpoint"][numRanks])

        print("--RESTART RUN--")
        runSim(numRanks, BINARY_PATH, SYNCH, MAPPING_PATH, 0, NKP, OFFICIAL_END,simDict["restart"][numRanks])

        totalNetEvents = int(simDict["checkpoint"][numRanks]["Net Events Processed"] + simDict["restart"][numRanks]["Net Events Processed"])

        if (totalNetEvents != int(simDict["baseline"][numRanks]["Net Events Processed"])):
            print("####################################################################")
            print("Net Events Mismatched Between RIO/Non-RIO Runs!!!")
            print("####################################################################")

    exportDicts("OUTPUT.txt")


if __name__ == '__main__':
    main()


