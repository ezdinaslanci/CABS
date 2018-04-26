#!/usr/bin/python

# Copyright 2016, Gurobi Optimization, Inc.
from shutil import copyfile
from gurobipy import *

def runModel(CAB, allowedTime, CABID):
    status = ['ERROR', 'LOADED', 'OPTIMAL', 'INFEASIBLE', 'INF_OR_UNBD', 'UNBOUNDED', 'CUTOFF', 'ITERATION_LIMIT', 'NODE_LIMIT', 'TIME_LIMIT', 'SOLUTION_LIMIT', 'INTERRUPTED', 'NUMERIC', 'SUBOPTIMAL', 'INPROGRESS', 'USER_OBJ_LIMIT']
    try:
        # Create a new model
        model = Model("My Model")
        model.setParam('TimeLimit', allowedTime)

        # Create price(p) values for each bid with j index
        p = dict()
        for j in range(CAB.numberOfBids):
            p[str(j)] = CAB.bidList[j].priceOfBid


        # Create u values for each item with i index which represent number of avaiable units for item i
        u = dict()
        for i in range(CAB.numberOfItems):
            u[str(i)] = CAB.itemList[i].numberOfUnits

        # Create cost(c) values for each item with i index
        c = dict()
        for i in range(CAB.numberOfItems):
            c[str(i)] = CAB.itemList[i].costOfItem

        # Create quantity values for each subbid of bids with j, k index
        q = dict()
        for j in range(CAB.numberOfBids):
            for k in range(CAB.bidList[j].numberOfSubBids):
                q[str(j) + "_" + str(k)] = CAB.bidList[j].listOfSubBids[k].quantity

        # Create x variables with j index
        # x is binary that represent whether x(j) bid satisfied(1) or not(0)
        x = dict()
        for j in range(CAB.numberOfBids):
            x[str(j)] = model.addVar(vtype=GRB.BINARY, name="x"+str(j))


        # Create y variables with i, j, k indexes
        # y is a natural number that represent how many units of item i are taken by k'th subbid of ...
        #... bid j if it is satisfied
        y = dict()
        for i in range(CAB.numberOfItems):
            for j in range(CAB.numberOfBids):
                for k in range(CAB.bidList[j].numberOfSubBids):
                    varIndex = str(i) + "_" + str(j) + "_" + str(k)
                    y[varIndex] = model.addVar(vtype=GRB.INTEGER, lb=0, name="y" + varIndex)

        model.update()

        #objective function first part sum of (price of bid*is bid accepted)
        obj = LinExpr(None)
        for j in range(CAB.numberOfBids):
            obj.addTerms(p[str(j)], x[str(j)])

        # objective function second part sum of (cost of each item*is bid accepted and it is in subbid)
        for i in range(CAB.numberOfItems):
            for j in range(CAB.numberOfBids):
                for k in range(CAB.bidList[j].numberOfSubBids):
                    if i in CAB.bidList[j].listOfSubBids[k].listOfItems:
                        varIndex = str(i) + "_" + str(j) + "_" + str(k)
                        obj.addTerms(-1*c[str(i)], y[varIndex])

        # Set objective
        model.setObjective(obj, GRB.MAXIMIZE)

        #constrains the sum of the requested quantity of item i by all subbids with the number of available units of item i.
        for i in range(CAB.numberOfItems):
            dummyExp = LinExpr(None)
            for j in range(CAB.numberOfBids):
                for k in range(CAB.bidList[j].numberOfSubBids):
                    if i in CAB.bidList[j].listOfSubBids[k].listOfItems:
                        varIndex = str(i) + "_" + str(j) + "_" + str(k)
                        dummyExp.addTerms(1, y[varIndex])
            model.addConstr(dummyExp.__le__(u[str(i)]), "c1"+str(i))

        #constrains the sum of the quantities for each item inside a subbid to be equal to the requested ...
        #... quantity in that subbid if bid j is satisfied, otherwise y(i, j, k) values are cleared to 0.
        for j in range(CAB.numberOfBids):
            for k in range(CAB.bidList[j].numberOfSubBids):
                dummyExp = LinExpr(None)
                for i in range(CAB.numberOfItems):
                    if i in CAB.bidList[j].listOfSubBids[k].listOfItems:
                        varIndex = str(i) + "_" + str(j) + "_" + str(k)
                        dummyExp.addTerms(1, y[varIndex])

                dummyExp.addTerms(-1*q[str(j)+"_"+str(k)], x[str(j)])
                model.addConstr(dummyExp.__eq__(0), "c2" + str(j) + "_" + str(k))

        # constraints y(i, j, k) value is set to 0 if item i is not requested by the kth subbid of the jth bid.
        for i in range(CAB.numberOfItems):
            for j in range(CAB.numberOfBids):
                for k in range(CAB.bidList[j].numberOfSubBids):
                    if i not in CAB.bidList[j].listOfSubBids[k].listOfItems:
                        dummyExp = LinExpr(None)
                        varIndex = str(i) + "_" + str(j) + "_" + str(k)
                        dummyExp.addTerms(1, y[varIndex])
                        model.addConstr(dummyExp.__eq__(0), "c3" + varIndex)

        open('gurobi.log', 'w')
        model.optimize()
        objVal = model.objVal
        runTime = model.Runtime
        statusCode = model.Status
        gap = model.MIPGap
        copyfile('gurobi.log', 'log/CAB_' + str(CABID) + '.log')
        model.write('sol/CAB_' + str(CABID) + '.sol')
        model.write('lp/CAB_' + str(CABID) + '.lp')
        model.write('mst/CAB_' + str(CABID) + '.mst')
        model.write('mps/CAB_' + str(CABID) + '.mps')
        return objVal, runTime, status[statusCode], gap


    except GurobiError as e:
        print('Error code ' + str(e.errno) + ": " + str(e))

    except AttributeError:
        print('Encountered an attribute error ')
