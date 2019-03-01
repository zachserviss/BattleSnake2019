    ########### NEW COLTON CODE
    
    # Makes the grid, called every turn
    def makeGrid():
        grid = []
        for y in range(0, height):
            grid.append([])
            for x in range(0, height):
                grid[y].append(-1)
        return grid
    
    # adds self to the grid
    def addYouToGrid(grid):
        for seg in body:
            grid[seg['y']][seg['x']] = 1 ## mark the body
        
        # snakes "uncoil" these ifs prevent an elongating tail
        #   from looking like a moving tail
        if len(body) > 1: 
           if tail['y'] != body[-2]['y'] or tail['x'] != body[-2]['x']:
               grid[tail['y']][tail['x']] = 2
        grid[head['y']][head['x']] = 0
    
    def addBaddiesToGrid(grid):
        badSnakes = []
        # find the bad snakes who aren't you
        for baddy in baddies:
            if baddy['id'] != data['you']['id']:
                badSnakes.append(baddy['body'])
        # draw the bad snakes on the grid

        snakeCount = 0 # shows different snakes
        for badBod in badSnakes:
            snakeCount += 1
            badHead = badBod[0]
            badTail = badBod[-1]
            for badSeg in badBod:
                grid[badSeg['y']][badSeg['x']] = snakeCount * 3 + 1 ## place the bad body
            if len(badBod) > 1:
                if badTail['y'] != badBod[-2]['y'] or badBod[-2]['x']:
                    grid[badTail['y']][badTail['x']] = snakeCount * 3 + 2
            grid[badHead['y']][badHead['x']] = snakeCount * 3

        snakeLengths = []
        snakeLengths.append(len(body))
        for bad in badSnakes:
            snakeLengths.append(len(bad))
        return snakeLengths
    def addFoodToGrid(grid):
        for piece in food:
            grid[piece['y']][piece['x']] = -2
            # Maybe not best symbol for food?
            # but does keep a negative value as a safe path, which might be useful 

    grid = makeGrid() # Makes grid
    addFoodToGrid(grid) # MIGHT BE USELESS
    addYouToGrid(grid) # add you
    lengths = addBaddiesToGrid(grid) # add baddies and return lengths of YOU & BADDIES snakes 
    
    # #   GRID DESCRIPTION   #  #
    #
    # 0 is our head
    # 1 is our body
    # 2 is our tail
    # 
    # any value greater than or equal to 3 is part of another snake 
    # 
    # value % 3 = 0 is a head
    # value % 3 = 1 is a body segment
    # value % 3 = 2 is a tail
    #
    # if stored properly, like in the array "lengths"
    # value // 3 = a snake's index in that array (That is integer division)
    #
    # any negative value is "safe"
    # 
    # -1 is empty
    # -2 is food - this one might be useless?
    # 
    ###

    # Generate A grid Report - RAISES AN EXCEPTION - 
    # Will print the grid somewhat nicely formatted 
    if random.randint(1,100) == 1:
        report = " \n***** ***** **** **** \n  TURN: " +  str(cur_turn) + " REPORT : \nSnake Lengths: ";
        for i in range(0, len(lengths)):
            report += "  " + str(i) + " : " + str(lengths[i])
        report += "\n"
        rowCount = 0
        colCount = 0
        for y in grid:
            for x in y:
                colCount += 1
                if x > -1:
                    report += " "
                report += str(x) + " "
                if colCount % 5 == 0 :
                    report += "   " 
            report += "\n"
            rowCount += 1
            if rowCount % 5 == 0:
                report += "\n"
        raise Exception(report)

    ################# END NEW COLTON CODE
