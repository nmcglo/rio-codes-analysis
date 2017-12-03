import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import json
import numpy as np
import collections

np.set_printoptions(suppress=True)

jfile = open('output.txt')
jtext = jfile.read()

simDict = json.JSONDecoder(object_pairs_hook=collections.OrderedDict).decode(jtext)


baselineRuntimeArray = np.zeros((len(simDict['baseline']),2))
checkpointRuntimeArray = np.zeros((len(simDict['checkpoint']),2))
restartRuntimeArray = np.zeros((len(simDict['restart']),2))


for i,rank in enumerate(simDict['baseline']):
    baselineRuntimeArray[i,0] = rank
    baselineRuntimeArray[i,1] = simDict['baseline'][rank]['Running Time']

for i,rank in enumerate(simDict['checkpoint']):
    checkpointRuntimeArray[i,0] = rank
    checkpointRuntimeArray[i,1] = simDict['checkpoint'][rank]['Running Time']

for i,rank in enumerate(simDict['restart']):
    restartRuntimeArray[i,0] = rank
    restartRuntimeArray[i,1] = simDict['restart'][rank]['Running Time']

crRuntimeArray = np.zeros((len(simDict['checkpoint']),2))
for i,rank in enumerate(simDict['checkpoint']):
    crRuntimeArray[i,0] = rank
    crRuntimeArray[i,1] = checkpointRuntimeArray[i,1] + restartRuntimeArray[i,1]


RED = (214/255., 39/255., 40/255.)
GREEN = (44/255., 160/255., 44/255.)
BLUE = (31/255., 119/255., 180/255.)

fig, ax = plt.subplots()

for y in np.arange(0,.09,.01):
    ax.plot(np.arange(0,34,1), [y] * len(np.arange(0,34,1)), "--", lw=0.5, color="black",alpha=0.3)
plt.ylim(0,.08)
plt.xlim(0,34)

ax.plot(baselineRuntimeArray[:,0], baselineRuntimeArray[:,1],'o-',color=BLUE,label="Baseline")
ax.plot(crRuntimeArray[:,0], crRuntimeArray[:,1],'o-',color=RED,label="With RIO")

ax.set_title("Runtime with Increasing Number of Ranks")
ax.set_xlabel("Number of Ranks")
ax.set_ylabel("Simulation Runtime (s)")
plt.xticks(baselineRuntimeArray[:,0], baselineRuntimeArray[:,0].astype(int))
ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%0.2f'))

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

plt.legend(loc='upper right')


plt.show()