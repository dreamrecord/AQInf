# libs
import pandas as pd;
from collections import OrderedDict;

# functions
from AQInf import AQInf;
from minEntropyNodeInfer import minEntropyNodeInfer;
from matrixInit import stringIndexMatrixInit;

# Input:
# (a) [string list] the labeled node list
# (b) [string list] the unlabeled node list
# (c) [string list] the time stamp list
# (d) [pandas DataFrame] the AQI value of labeled node over time stamp
# (e) [int] the # of locations k to be selected for new stations
# Output:
# [string list] the set S of k recommended locations (|S| = k)

# haven't implemented:
# [optional] algo.2.12: sum finished, average
# labeledAQIDict: AQInf's para, the Pv matrix, feed input into it. 

def GEM(labeledList,
        unlabeledList,
        timeStampList,
        labeledAQITable,
        labeledFeatureDictListUponTimeStamp,
        unlabeledFeatureDictListUponTimeStamp,
        numToBeRecommend):
    
    # variables
    unlabeledListLen = len(unlabeledList);
    currentLabeledList = [];
    labeledAQIDict = OrderedDict();
    numOfFeatures = len(labeledFeatureDictListUponTimeStamp[ timeStampList[0] ]);
    
    # initialize the rankTable
    # unlabeled nodes -> time stamps
    rankTable = pd.DataFrame([ [-1] * unlabeledListLen ] * len(timeStampList),
                             index = timeStampList,
                             columns = unlabeledList);

    # combine the 2 node list with time stamp list
    labeledList = [ (node, timeStamp) for timeStamp in timeStampList for node in labeledList ];
    unlabeledList = [ (node, timeStamp) for timeStamp in timeStampList for node in unlabeledList ];

    # begin iteration 
    for currentTimeStamp in timeStampList:

        # update the 2 node list each time stamp
        leftUnlabeledList = [ element for element in unlabeledList if element[1] == currentTimeStamp ];
        tempLabeledList = [ element for element in labeledList if element[1] == currentTimeStamp ];
        currentLabeledList += tempLabeledList;

        # update the labeled AQI dict each time stamp
        tempLabeledAQIDict = OrderedDict( zip( tempLabeledList, 
                                               labeledAQITable[ currentTimeStamp : currentTimeStamp ].
                                               values.ravel().tolist() ) );
        labeledAQIDict.update(tempLabeledAQIDict);
        
        # for each unlabeled nodes: do GEM
        for currentRank in range(unlabeledListLen, 0, -1):

            unlabeledDistriMatrix = AQInf(currentLabeledList,
                                          leftUnlabeledList,
                                          currentTimeStamp,
                                          labeledAQIDict,
                                          labeledFeatureDictListUponTimeStamp,
                                          unlabeledFeatureDictListUponTimeStamp,
                                          numOfFeatures);

            # select the unlabedled node with the min entropy
            (minEntropyUnlabeled, minEntropyUnlabeledAQI) = minEntropyNodeInfer(unlabeledDistriMatrix);

            # give the rank value reversely
            rankTable[ minEntropyUnlabeled[0] ][currentTimeStamp] = currentRank;

            # turn unlabeled to labeled
            currentLabeledList.append(minEntropyUnlabeled);

            # update the labeled AQI dict
            labeledAQIDict[minEntropyUnlabeled] = minEntropyUnlabeledAQI;

            # exclude the labeled node from the unlabeled list
            unlabeledList.remove(minEntropyUnlabeled);

            # update the feature dict list
            currentLabeledFeatureDictList = labeledFeatureDictListUponTimeStamp[currentTimeStamp];
            currentUnlabeledFeatureDictList = unlabeledFeatureDictListUponTimeStamp[currentTimeStamp];

            for i in range(numOfFeatures):
                currentLabeledFeatureDictList[i][ minEntropyUnlabeled[0] ] = currentUnlabeledFeatureDictList[i][ minEntropyUnlabeled[0] ];
                del currentUnlabeledFeatureDictList[i][ minEntropyUnlabeled[0] ];

    # construct the recommend list
    # sort the rankList in descending order
    return list(pd.DataFrame(rankTable.sum()).sort(columns = 0, ascending = False).index);
