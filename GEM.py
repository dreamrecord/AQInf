# Input:
# (a) [string list] a set of locations V with existing measurement stations;
# (b) [string list] a set of candidate locations C without stations;
# (c) [string list] the time stamps T = t1, t2,...,tm;
# (d) [int] the number of locations k to be selected for new stations;
# Output:
# [string list] the set S of k recommended locations (|S| = k);

###########################
# haven't implemented:
# [optional] algo.2.12: sum finished, average
# AQInf para: the Pv matrix, should be updated every AQInf call
###########################

# 2D Ordered Dict
import collections;
from AQInf import AQInf;
from minEntropyNodeInfer import minEntropyNodeInfer;

def GEM(labeledList, unlabeledList, timeStampList, numToBeRecommend):
    
    # variables
    unlabeledListLen = len(unlabeledList);
    rankTable = collections.OrderedDict();
    rankList = collections.OrderedDict();
    recommendList = [];
    
    # initialize the rankTable
    # unlabeled nodes -> time stamps
    for unlabeled in unlabeledList:
        rankTable[unlabeled] = collections.OrderedDict();
        for currentTimeStamp in timeStampList:
            rankTable[unlabeled][currentTimeStamp] = -1;

    # for each time stamps: do GEM
    for currentTimeStamp in timeStampList:

        leftUnlabeledList = unlabeledList;
        
        # for each unlabeled nodes: do GEM
        for currentRank in range(unlabeledListLen, 0, -1):

            unlabeledDistriMatrix = AQInf(labeledList, leftUnlabeledList, currentTimeStamp);

            # select the unlabedled node with the min entropy
            minEntropyUnlabeled = minEntropyNodeInfer(unlabeledDistriMatrix);

            # give the rank value reversely
            rankTable[minEntropyUnlabeled][currentTimeStamp] = currentRank;

            # turn unlabeled to labeled
            labeledList.append(minEntropyUnlabeled);

            # exclude the labeled node from the unlabeled list
            unlabeledList.remove(minEntropyUnlabeled);

    # for each node: sum the rank value
    for unlabeled in unlabeledList:
        rankList[unlabeled] = sum(rankTable[unlabeled].values());
            
    # sort the rankList in descending order
    # and add to the recommend list
    # sorted::key: key which is comparison based on 
    # reverse = True flag: descending order
    for (key, value) in sorted(rankList.iteritems(), key = lambda (k,v): (v,k), reverse = True):
        recommendList.append(key);

    return recommendList;