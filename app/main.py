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
