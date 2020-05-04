from geventwebsocket.handler import WebSocketHandler
from gevent.pywsgi import WSGIServer
from flask import Flask, request, render_template
from flask import Flask, render_template, request
from pprint import pprint
import json
from random import randint
from action import Action
from vector import Vector
from team import Team
from field import Field
from player import Player
from ball import Ball
import math
import time

app = Flask(__name__)

# constant values: player speed with and without ball, ball speed. Unit: pixel per second
speed_w_ball = 150/1.414
speed_wo_ball = 180/1.414
speed_of_ball = 360/1.414

p1 = Player("Yiduo", (550, 550), (0, 0, speed_w_ball), Team.left, True)
ball = Ball((555, 550), (0, 0, speed_w_ball), p1)
field = Field(0, 0, 1050, 680, 30)

# TODO: change the name of current state later
current_state = [p1]

def parse_one_player_coors(player):
    (x,y) = player.get_coordinate()
    return {'x':x, 'y':y}
   
# what happens immediately after the player takes a certain action (with ball)
def player_act_balled(player, act, ball):

    if act == Action.shoot:
        (x, y) = player.coordinate
        # vx and vy are both less than 1, representing the direction normal vector
        if player.team == Team.left:
            (goal_x, goal_y) = field.right_down_goal_tip
            (vx, vy) = (goal_x - x, goal_y - y)
        else:
            (goal_x, goal_y) = field.left_down_goal_tip
            (vx, vy) = (goal_x - x, goal_y - y)
        # normalize the direction vector
        vx = vx / math.sqrt(vx**2.0 + vy**2.0)
        vy = vy / math.sqrt(vx**2.0 + vy**2.0)
        # change speed vector of the ball 
        ball.set_ball_vec(vx, vy, speed_of_ball)
        # ball has no owner now after it's shooted
        ball.set_owner(None)
        # update the balls coordinate for the next second
        (ball_x, ball_y) = ball.get_coordinate()
        ball.set_coordinate(ball_x + vx * speed_of_ball, ball_y + vy * speed_of_ball)
        player.set_balled()

    elif act == Action.run:
        (x, y) = player.get_coordinate()
        if player.team == Team.left:
            (goal_x, goal_y) = field.right_down_goal_tip
            (vx, vy) = (goal_x - x, goal_y - y)
        else:
            (goal_x, goal_y) = field.left_down_goal_tip
            (vx, vy) = (goal_x - x, goal_y - y)
        # normalize the direction vector
        vx = vx / math.sqrt(vx**2.0 + vy**2.0)
        vy = vy / math.sqrt(vx**2.0 + vy**2.0)
        # change the player's vector to make him running towards the goal
        player.set_vector(vx, vy, speed_w_ball)
        # update the player's coordinate for the next second
        player.set_coordinate(x + vx * speed_w_ball, y + vy * speed_w_ball )
        # make ball run with the player
        ball.set_coordinate(x + vx * speed_w_ball, y + vy * speed_w_ball)
        ball.set_ball_vec(vx, vy, speed_w_ball)

    else: 
        pass


# what happens immediately after the player takes a certain action (without ball)
def player_act_unballed(p1, p2, act, ball):
    if act == Action.intercept:
        p = random.random()
        # with 0.5 possibility, the intercepting player gets the ball
        if p >= 0.5:
            p1.set_balled()
            p2.set_balled()
            ball.set_owner(p1)
        else:
            pass
    elif act == Action.run:
        (ball_x, ball_y) = ball.get_coordinate()
        # the unballed player runs towards the ball
        (vx, vy) = (ball_x, ball_y) - p1.get_coordinate()
        # normalize the direction vector
        vx = vx / math.sqrt(vx**2.0 + vy**2.0)
        vy = vy / math.sqrt(vx**2.0 + vy**2.0)
        p1.set_vector(vx, vy, speed_wo_ball)
        #update the coordinate of the player for the next second
        (x, y) = p1.get_coordinate()
        p1.set_coordinate(x + vx * speed_wo_ball, y + vy * speed_wo_ball)

@app.route('/', methods = ['POST','GET'])
def root():
    # package all info of the game into an array
    return render_template("football.html")

act_lst = [Action.run, Action.shoot, Action.run]

@app.route('/api')
def api():
    if request.environ.get('wsgi.websocket'):
        ws = request.environ['wsgi.websocket']
        while True:
            message = ws.receive()
            print(message)
            coors = [randint(80,1130),randint(50,730),randint(80,1130),randint(50,730),randint(80,1130),randint(50,730),randint(80,1130),randint(50,730)]
            ws.send(json.dumps(coors)[1:-1]) # getting rid of the [ and ] from the array
    return

if __name__== "__main__":
    http_server = WSGIServer(('',5000), app, handler_class=WebSocketHandler)
    http_server.serve_forever()
    
    app.debug = True
    app.run()
