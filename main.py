import json
import os
import random
import bottle

from api import ping_response, start_response, move_response, end_response


# GLOBAL VARIABLES ####
globGrid = []
# in grid:
# x = empty
# h = our head
# b = our body
# t = our tail
# e = bad head
# f = bad body
# g = bad tail

test_dir = 'right'
ourOldHead = [-1,-1]
ourOldTail = [-1,-1] # will track our tail

badOldHeads = [] # Might be useless
badOldTails = [] # will track other tails
# END GLOBAL VARIABLES ####

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
    
    # Similar setup as a move
    width = data['board']['width']
    height = data['board']['height']
    baddies = data['board']['snakes']
    head = data['you']['body'][0]
    
    def createGrid():
        global globGrid
        global ourOldTail
        global badOldTails
        #creates a 2d grid
        for y in range(height):
            globGrid.append([])
            for x in range(width):
                globGrid[y].append('x')
        
        # this block populates the grid
        #first, our own head
        globGrid[head['y']][head['x']] = 'h'
        # set our old head as head location
        ourOldHead[0] = head['x']
        ourOldHead[1] = head['x']
        #then set our old tail as the head location
        ourOldTail[0] = head['x']
        ourOldTail[1] = head['y']
        # NOTICE! location is accessed [y][x]

        # now, the other snake heads

        for badSnake in baddies:
            badHead = badSnake['body'][0]
            badOldTails.append([badHead['x'],badHead['y']]) 
            badOldHeads.append([badHead['x'],badHead['y']])
            globGrid[badHead['y']][badHead['x']] = 'a'
    
    createGrid()
    """
    TODO: If you intend to have a stateful snake AI,
            initialize your snake state here using the
            request's data if necessary.
    """
    print(json.dumps(data))

    color = "#00FF09"

    return start_response(color)


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
    body = data['you']['body']
    tail = data['you']['body'][-1]

    def foodClosest():
        minDistance = [0,0,width+height]
        for a in food:
            fooditemx = a["x"]
            fooditemy = a["y"]

            snakex = head["x"]
            snakey = head["y"]

            diffx = fooditemx - snakex
            diffy = fooditemy - snakey

            currDistance = abs(diffx)+abs(diffy)

            if currDistance < (minDistance[2]):
                minDistance[2] = currDistance
                minDistance[0] = diffx
                minDistance[1] = diffy

        return minDistance

    def foodDirection(x,y):
        if abs(x) >= abs(y):
            if x > 0:
                return "right"
            else:
                return "left"
        else:
            if y > 0:
                return "down"
            else:
                return	"up"
    
    def bodyCrash(currentMove):
        #right is minus x
        #left is plus x
        #up is plus y
        #down is minus y
        move = currentMove
        for a in body:
            if currentMove == "right":
                if head["x"]+1 == a["x"] and head["y"] == a["y"]:
                    move = "down"
            if currentMove == "left":
                if head["x"]-1 == a["x"] and head["y"] == a["y"]:
                    move = "up"
            if currentMove == "up":
                if head["y"]-1 == a["y"] and head["x"] == a["x"]:
                    move = "right"
            if currentMove == "down":
                if head["y"]+1 == a["y"] and head["x"] == a["x"]:
                    move = "left"
        return move

    def wallCrash(currentMove):
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
        for snake in data['board']['snakes']:
            for a in snake['body']:
                if currentMove == "right":
                    if head["x"]+1 == a["x"] and head["y"] == a["y"]:
                        move = "down"
                if currentMove == "left":
                    if head["x"]-1 == a["x"] and head["y"] == a["y"]:
                        move = "up"
                if currentMove == "up":
                    if head["y"]-1 == a["y"] and head["x"] == a["x"]:
                        move = "right"
                if currentMove == "down":
                    if head["y"]+1 == a["y"] and head["x"] == a["x"]:
                        move = "left"
        return move

# NEW FUNCTION
    def updateGrid():
        global globGrid
        global ourOldHead
        global badOldHeads
        global badOldTails

        #update our position on the bord
        globGrid[head['y']][head['x']] = 'h'
        globGrid[ourOldHead[1]][ourOldHead[0]] = 'b'
        #Clean up our old tail
        globGrid[ourOldTail[1]][ourOldTail[0]] = 'x'
        #if new tail is in same position will reset the value
        globGrid[tail['y']][tail['x']] = 't'

        #Now Update the baddies
        for i in range(len(baddies)):
            snake = baddies[i]['body']

            #these are meant to remove old heads and tails, didn't work

            #while snake[1]['x']!=badOldHeads[i][0] and snake[1]['y']!=badOldHeads[i][1]:
                #del badOldHeads[i]
            #while snake[-1]['x']!=badOldTails[i][0] and snake[-1]['y']!=badOldTails[i][1]:
                #del badOldTails[i]

            #fill the body
            for j in range(0,len(snake)):
                snakeBody = snake[j]
                globGrid[snakeBody['y']][snakeBody['x']] = 'f'
            
            #place the head
            snakeHead = snake[0]
            globGrid[snakeHead['y']][snakeHead['x']] = 'e'
            
            #place the tail
            snakeTail = snake[-1]
            oldTail = badOldTails[i]
            if globGrid[oldTail[1]][oldTail[0]] == 'g':
                globGrid[oldTail[1]][oldTail[0]] = 'x'
            globGrid[snakeTail['y']][snakeTail['x']] = 'g'


        
    directions = ['up','left','down','right']
    direction = directions[cur_turn %4]

    if (health < 50):
        arr = foodClosest()
        direction = foodDirection(arr[0],arr[1])

    direction = bodyCrash(direction)
    direction = bodyCrash(direction)
    direction = bodyCrash(direction)
    direction = bodyCrash(direction)

    direction = avoidSnakes(direction)
    direction = avoidSnakes(direction)
    direction = avoidSnakes(direction)
    direction = avoidSnakes(direction)


    direction = wallCrash(direction)
    direction = wallCrash(direction)
    direction = wallCrash(direction)
    direction = wallCrash(direction)
    
    updateGrid()
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
