import json
import os
import random
import bottle


from api import ping_response, start_response, move_response, end_response

@bottle.route('/')
def index():
    return '''
    Battlesnake documentation can be found at
       <a href="https://docs.battlesnake.io">https://docs.battlesnake.io</a>.
    '''

@bottle.route('/static/<path:path>')
def static(path):
    """
    Given a path, return the static file located relative
    to the static folder.

    This can be used to return the snake head URL in an API response.
    """
    return bottle.static_file(path, root='static/')

@bottle.post('/ping')
def ping():
    """
    A keep-alive endpoint used to prevent cloud application platforms,
    such as Heroku, from sleeping the application instance.
    """
    return ping_response()

@bottle.post('/start')
def start():
    data = bottle.request.json

    """
    TODO: If you intend to have a stateful snake AI,
            initialize your snake state here using the
            request's data if necessary.
    """
    #print(json.dumps(data))

    #color = "#00FF09"
    #headType = "beluga"
    #tailType = "curled"
    status = 200
    header = {"Content-Type":"application/json"}


    color= "#48f404"
    headType= "beluga"
    tailType= "fat-rattle"
       
    return start_response(color, headType, tailType)

    #return start_response(startSnake)


@bottle.post('/move')
def move():
    data = bottle.request.json

    """
    TODO: Using the data from the endpoint request object, your
            snake AI must choose a direction to move in.
    """
    cur_turn = data['turn']
    width = data['board']['width']
    height = data['board']['height']
    food = data['board']['food']
    baddies = data['board']['snakes']
    health = data['you']['health']
    head = data['you']['body'][0]
    tail = data['you']['body'][-1]
    body = data['you']['body']

    def foodClosest():
        #find distance to closest piece of food
        minDistanceToFood = [0,0,width+height]
        for piece in food:
            foodPieceX = piece["x"]
            foodPieceY = piece["y"]

            snakeHeadX = head["x"]
            snakeHeadY = head["y"]

            distanceToFoodX = foodPieceX - snakeHeadX
            distanceToFoodY = foodPieceY - snakeHeadY

            currDistance = abs(distanceToFoodX)+abs(distanceToFoodX)

            if currDistance < (minDistanceToFood[2]):
                minDistanceToFood[0] = distanceToFoodX
                minDistanceToFood[1] = distanceToFoodY
                minDistanceToFood[2] = currDistance

        return minDistanceToFood

    def foodDirection(foodPieceX,foodPieceY):
        #find directions to closest piece of food
        if abs(foodPieceX) >= abs(foodPieceY):
            if foodPieceX > 0:
                return "right"
            else:
                return "left"
        else:
            if foodPieceY > 0:
                return "down"
            else:
                return	"up"
    
    def bodyCrash(currentMove):
        #right is minus x
        #left is plus x
        #up is plus y
        #down is minus y
        move = currentMove
        for snakePiece in body:
            if currentMove == "right":
                if head["x"]+1 == snakePiece["x"] and head["y"] == snakePiece["y"]:
                    move = "down"
            if currentMove == "left":
                if head["x"]-1 == snakePiece["x"] and head["y"] == snakePiece["y"]:
                    move = "up"
            if currentMove == "up":
                if head["y"]-1 == snakePiece["y"] and head["x"] == snakePiece["x"]:
                    move = "right"
            if currentMove == "down":
                if head["y"]+1 == snakePiece["y"] and head["x"] == snakePiece["x"]:
                    move = "left"
        return move

    def wallCrash(currentMove):
        #turn if youre gonna hit a wall
        move = currentMove
        if currentMove == "right":
            if head["x"] == width-1:
                move = "down"

        if currentMove == "left":
            if head["x"] == 0:
                move = "up"

        if currentMove == "up":
            if head["y"] == 0:
                move = "right"

        if currentMove == "down":
            if head["y"] == height-1:
                move = "left"
        return move
    
    def avoidSnakes(currentMove):
        move = currentMove
        #find all snakes in board
        for snake in data['board']['snakes']:
            #map out each segment of a snake on the board
            for segment in range(0, len(snake['body'])-1):
                badSnakeBody = snake['body'][segment]
                #turn of your gonna hit a snake
                if currentMove == "right":
                    if head["x"]+1 == badSnakeBody["x"] and head["y"] == badSnakeBody["y"]:
                        move = "down"
                if currentMove == "left":
                    if head["x"]-1 == badSnakeBody["x"] and head["y"] == badSnakeBody["y"]:
                        move = "up"
                if currentMove == "up":
                    if head["y"]-1 == badSnakeBody["y"] and head["x"] == badSnakeBody["x"]:
                        move = "right"
                if currentMove == "down":
                    if head["y"]+1 == badSnakeBody["y"] and head["x"] == badSnakeBody["x"]:
                        move = "left"
        return move

    def safeMove():
        safeMoves = []
        possibleMoves = ['up','left','down','right']
        for move in possibleMoves:
            move1 = bodyCrash(move)

            move2 = wallCrash(move)

            move3 = avoidSnakes(move)


            if move1 == move2 and move1 == move3:
                safeMoves.append(move1)
        return safeMoves        
    
    def cornerCrash(currentMove):
        #numbers refer to clock position of corner on board
        move = currentMove
        #4 oclock
        if head['x']== width-1 and head['y']== height-2:
                if body[1]['x'] == head['x'] and body[1]['y'] == head['y']-1:
                   move = 'left'
                if body[1]['x'] == head['x']-1 and body[1]['y'] == head['y']:
                    move = 'up'
        # 5 oclock            
        if head['x']== width-2 and head['y']== height-1:
                if body[1]['x'] == head['x'] and body[1]['y'] == head['y']-1:
                   move = 'left'
                if body[1]['x'] == head['x']-1 and body[1]['y'] == head['y']:
                    move = 'up'
        #7 oclock            
        if head['x']== 1 and head['y']== height-1:
                if body[1]['x'] == head['x']+1 and body[1]['y'] == head['y']:
                   move = 'up'
                if body[1]['x'] == head['x'] and body[1]['y'] == head['y']-1:
                    move = 'right'

        #8 oclock            
        if head['x']== 0 and head['y']== height-2:
                if body[1]['x'] == head['x'] and body[1]['y'] == head['y']+1:
                   move = 'up'
                if body[1]['x'] == head['x']-1 and body[1]['y'] == head['y']:
                    move = 'right'  
        # 10 oclock            
        if head['x']== 0 and head['y']== 1:
                if body[1]['x'] == head['x'] and body[1]['y'] == head['y']-1:
                   move = 'right'
                if body[1]['x'] == head['x']+1 and body[1]['y'] == head['y']:
                    move = 'down'   
        # 11
        if head['x']== 1 and head['y']== 0:
                if body[1]['x'] == head['x'] and body[1]['y'] == head['y']+1:
                   move = 'right'
                if body[1]['x'] == head['x']+1 and body[1]['y'] == head['y']:
                    move = 'down'
        #1
        if head['x']== width-2 and head['y']== 0:
                if body[1]['x'] == head['x']-1 and body[1]['y'] == head['y']:
                   move = 'down'
                if body[1]['x'] == head['x'] and body[1]['y'] == head['y']+1:
                    move = 'left'
        #2
        if head['x']== width-1 and head['y']== 1:
                if body[1]['x'] == head['x']-1 and body[1]['y'] == head['y']:
                   move = 'down'
                if body[1]['x'] == head['x'] and body[1]['y'] == head['y']+1:
                    move = 'left'                                                                                       
   
        knownSafeMoves = safeMove()
        for moves in knownSafeMoves:
            if moves == move:
                return move   
        move = currentMove

        
        return move


    def generateSafeCoords():
        moveSafe = safeMove()
        safeCoords = []
        for move in moveSafe:
            if move == 'left':
                safeCoords.append([head['x']-1, head['y'],'left'])
            if move == 'right':
                safeCoords.append([head['x']+1, head['y'],'right'])
            if move == 'down':
                safeCoords.append([head['x'], head['y']+1,'down'])
            if move == 'up':
                safeCoords.append([head['x'], head['y']-1,'up'])  

        return safeCoords

    def prefferdMoves():
        prefferdMoves = []
        coords = generateSafeCoords() 
        for coord in coords:
            safe = True
            for badguy in baddies:
                badHead = badguy['body'][0]
                if data['you']['id'] != badguy['id']:
                    if (((abs(badHead['y'] - coord[1])) + (abs(badHead['x'] - coord[0]))) <=2) and  (len(badguy['body']) >= len(body)):
                        safe = False
            if safe == True:
                prefferdMoves.append(coord[2])
        return prefferdMoves 

    def timeToKill():
        for snake in baddies:
            if len(snake) > len(body):
                return False
            else:
                return True                             


    def headDirections():
        for badguy in baddies:
                badHead = badguy['body'][0]
                if head['x']>badHead['x']:
                    move = 'right'
                if head['x']<badHead['x']:
                    move = 'left'
                if head['y']>badHead['y']:
                    move = 'down'
                if head['x']>badHead['x']:
                    move = 'up'  
        return move  
    def tailClosest():
        minDistanceToTail = [0,0,width+height]
        snakeTailX = tail["x"]
        snakeTailY = tail["y"]

        snakeHeadX = head["x"]
        snakeHeadY = head["y"]

        distanceToTailX = snakeTailX - snakeHeadX
        distanceToTailY = snakeTailY - snakeHeadY

        currDistance = abs(distanceToTailX)+abs(distanceToTailY)

        if currDistance < (minDistanceToTail[2]):
            minDistanceToTail[0] = distanceToTailX
            minDistanceToTail[1] = distanceToTailY
            minDistanceToTail[2] = currDistance
        return minDistanceToTail

    def chaseTail(x,y):
        #find directions to closest piece of food
        if abs(x) >= abs(y):
            if x > 0:
                return "right"
            else:
                return "left"
        else:
            if y > 0:
                return "down"
            else:
                return  "up"            


    directionIsSafe = False
    
    

    directions = ['up','left','down','right']
    direction = directions[cur_turn %4]

    

    #direction = directions[cur_turn %4]
    safeMoves = prefferdMoves()
    
    if (health < 30):
        arr = foodClosest()
        direction = foodDirection(arr[0],arr[1])
    else:
        arr = tailClosest()
        direction = chaseTail(arr[0],arr[1])    
    

    if not safeMoves:
        lastResort = safeMove()
        safeMoves = lastResort

    for move in safeMoves:
        if direction == move:
            directionIsSafe = True


    if directionIsSafe == False:
        direction = safeMoves[0]

    direction = cornerCrash(direction)
    print str(direction+"final actual really move")
    print str(data['you']['id'])
    return move_response(direction)

@bottle.post('/end')
def end():
    data = bottle.request.json

    """
    TODO: If your snake AI was stateful,
        clean up any stateful objects here.
    """
    print(json.dumps(data))

    return end_response()

# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '0.0.0.0'),
        port=os.getenv('PORT', '8080'),
        debug=os.getenv('DEBUG', True)
    )
