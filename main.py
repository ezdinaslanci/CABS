from Model import *
from EPS import *
import time


class CAB:
    def __init__(self):
        self.numberOfItems = 0
        self.numberOfBids = 0
        self.itemList = []
        self.bidList = []

class Item:
    def __init__(self):
        self.numberOfUnits = 0
        self.costOfItem = 0

class Bid:
    def __init__(self):
        self.numberOfSubBids = 0
        self.listOfSubBids = []
        self.priceOfBid = 0

class SubBid:
    def __init__(self):
        self.quantity = 0
        self.listOfItems = []

#getCABSData retuns data for each CAB without string and blank lines
def getCABSData(dir):
    cabs = []
    dummyCab = []
    with open(dir, 'r') as f:
        for line in f:
            if line[0:6] == '# CABS':
                cabs.append(dummyCab)
                dummyCab = []
            if line[0].isdigit():
                dummyCab.append(float(line))
        cabs.append(dummyCab)
    del cabs[0]
    return cabs

def createCABListFromData(CABDataList):
    numberOfCABS = len(CABDataList)

    CABList = []  # cab objets
    for i in range(numberOfCABS):
        dummyCAB = CAB()
        targetLine = 0
        numberOfItems = int(CABDataList[i][targetLine])
        dummyCAB.numberOfItems = numberOfItems
        targetLine = targetLine + 1

        for j in range(numberOfItems):
            dummyItem = Item()
            dummyItem.numberOfUnits = int(CABDataList[i][targetLine])
            dummyItem.costOfItem = CABDataList[i][targetLine + numberOfItems]
            dummyCAB.itemList.append(dummyItem)
            targetLine = targetLine + 1

        targetLine = targetLine + numberOfItems  # skip cost line, go to bids

        numberOfBids = int(CABDataList[i][targetLine])
        dummyCAB.numberOfBids = numberOfBids
        targetLine = targetLine + 1

        for j in range(numberOfBids):
            dummyBid = Bid()
            numberOfSubbids = int(CABDataList[i][targetLine])
            dummyBid.numberOfSubBids = numberOfSubbids
            targetLine = targetLine + 1

            for k in range(numberOfSubbids):
                dummySubbid = SubBid()
                numberOfItemsRequested = int(CABDataList[i][targetLine])
                targetLine = targetLine + 1

                for l in range(numberOfItemsRequested):
                    dummySubbid.listOfItems.append(int(CABDataList[i][targetLine]))
                    targetLine = targetLine + 1

                dummySubbid.quantity = int(CABDataList[i][targetLine])
                targetLine = targetLine + 1
                dummyBid.listOfSubBids.append(dummySubbid)
            dummyBid.priceOfBid = CABDataList[i][targetLine]
            dummyCAB.bidList.append(dummyBid)
            targetLine = targetLine + 1

        CABList.append(dummyCAB)

    return CABList


def main():
    global time
    fileName = 'cabs-testcases.txt'
    # fileName = 'demo-case.txt'
    CABDataList = getCABSData(fileName)
    CABList = createCABListFromData(CABDataList)
    print("CAB Lists are created")
    #
    gurobiSolver = False
    heuristicSolver = True

    if gurobiSolver:
        exps = open('experiments.txt', 'w')
        exps.writelines('CABS\t\tStatus\t\tGap\t\t\t\tObjVAl\t\t\tTime\n')
        exps.close()

        for i in range(0, 48):
            objVal, time, status, gap = runModel(CABList[i], 3600, i)
            line = str(i) + '\t\t\t' + status + '\t\t' + "{:.6f}".format(gap) + '\t\t' + "{:.3f}".format(objVal) + '\t\t' + "{:.3f}".format(time) + '\n'
            exps = open('experiments.txt', 'a')
            exps.writelines(line)
            exps.close()

    startTime = time.time()
    if heuristicSolver:
        exps = open('experimentsHeuristic.txt', 'w')
        exps.writelines('CABS\t\tMaxVal\t\t\t\tTime\n')
        exps.close()

        for i in range(0, 1):
            startTime = time.time()
            eps = EPS(CABList[i])
            endTime = time.time()
            executionTime = (endTime - startTime)
            line = str(i) + '\t\t\t' + "{:.3f}".format(eps.maxValue) + '\t\t\t' + "{:.3f}".format(executionTime) + '\n'
            exps = open('experimentsHeuristic.txt', 'a')
            exps.writelines(line)
            exps.close()
            print("CABS " + str(i) + ": " + str(eps.maxValue))



if __name__ == '__main__':
    main()








