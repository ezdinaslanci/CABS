from heapq import heappush, heappop
import networkx as nx
class EPS:
    def __init__(self, cab):
        self.winningBids = []
        self.solution = None
        self.maxValue = 0
        self.cab = cab
        self.cost = 0
        self.solveEPS()


    def checkFeasible(self):
        G = nx.DiGraph()
        totalQuantity = 0
        totalPrice = 0
        for bid in self.winningBids:
            bidName = 'b'+str(bid[1])
            G.add_edge('s', bidName)
            totalPrice += self.cab.bidList[bid[1]].priceOfBid
            for s in range(len(self.cab.bidList[bid[1]].listOfSubBids)):
                subbidName = bidName + 's' + str(s)
                quantity = self.cab.bidList[bid[1]].listOfSubBids[s].quantity
                totalQuantity += quantity
                G.add_edge(bidName, subbidName, capacity=quantity)
                for i in self.cab.bidList[bid[1]].listOfSubBids[s].listOfItems:
                    itemName = 'r' + str(i)
                    unitOfItem = self.cab.itemList[i].numberOfUnits
                    G.add_edge(subbidName, itemName)
                    G.add_edge(itemName, 't', capacity=unitOfItem)

        G.add_node('s', demand=-totalQuantity)
        G.add_node('t', demand=totalQuantity)
        try:
            flowDict = nx.min_cost_flow(G)
            self.maxValue = [self.maxValue, totalPrice][self.maxValue < totalPrice]
            return flowDict
        except:
            return False

    def solveEPS(self):
        orderedBids = []
        #Ranking Phase
        i = 0
        for bid in self.cab.bidList:
            qSum = 0
            cost = 0
            for subbid in bid.listOfSubBids:
                numberOfItems = len(subbid.listOfItems)
                qSum += subbid.quantity/numberOfItems
                costDummy = 0
                for item in subbid.listOfItems:
                    costDummy += self.cab.itemList[item].costOfItem
                cost += costDummy/numberOfItems
            h = (bid.priceOfBid - cost)/qSum
            heappush(orderedBids, (1/h, i, bid.priceOfBid - cost))
            i += 1

        #Allocation Phase
        while orderedBids:
            self.winningBids.append(heappop(orderedBids))

            result = self.checkFeasible()
            if not result:
                del self.winningBids[len(self.winningBids) - 1]

            else:
                self.solution = result

        for r in self.solution:
            if r[0] == 'r':
                self.cost += self.solution[r]['t']*self.cab.itemList[int(r[1:])].costOfItem

        self.maxValue -= self.cost






