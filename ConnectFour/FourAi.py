import gym
import random
import requests
import numpy as np
import argparse
import sys
import time
from gym_connect_four import ConnectFourEnv

env: ConnectFourEnv = gym.make("ConnectFour-v0")

#SERVER_ADRESS = "http://localhost:8000/"
SERVER_ADRESS = "https://vilde.cs.lth.se/edap01-4inarow/"
API_KEY = 'nyckel'
STIL_ID = ["lo0016ol-s", "da22test-s2"] # TODO: fill this list with your stil-id's

def call_server(move):
   res = requests.post(SERVER_ADRESS + "move",
                       data={
                           "stil_id": STIL_ID,
                           "move": move, # -1 signals the system to start a new game. any running game is counted as a loss
                           "api_key": API_KEY,
                       })
   # For safety some respose checking is done here
   if res.status_code != 200:
      print("Server gave a bad response, error code={}".format(res.status_code))
      exit()
   if not res.json()['status']:
      print("Server returned a bad status. Return message: ")
      print(res.json()['msg'])
      exit()
   return res

def check_stats():
   res = requests.post(SERVER_ADRESS + "stats",
                       data={
                           "stil_id": STIL_ID,
                           "api_key": API_KEY,
                       })

   stats = res.json()
   return stats

"""
You can make your code work against this simple random agent
before playing against the server.
It returns a move 0-6 or -1 if it could not make a move.
To check your code for better performance, change this code to
use your own algorithm for selecting actions too
"""
def opponents_move(env):
   env.change_player() # change to oppoent
   avmoves = env.available_moves()
   if not avmoves:
      env.change_player() # change back to student before returning
      return -1

   # TODO: Optional? change this to select actions with your policy too
   # that way you get way more interesting games, and you can see if starting
   # is enough to guarrantee a win
   action = random.choice(list(avmoves))

   state, reward, done, _ = env.step(action)
   if done:
      if reward == 1: # reward is always in current players view
         reward = -1
   env.change_player() # change back to student before returning
   return state, reward, done

def student_move():
   """
   TODO: Implement your min-max alpha-beta pruning algorithm here.
   Give it whatever input arguments you think are necessary
   (and change where it is called).
   The function should return a move from 0-6
   """
   
   boardc = env.board.copy()
   
   
   prev_time = time.time()
   #move = find_best_move(boardc)  #no minmax 
   move, min_score = minimax(boardc,7,True,-np.Inf,np.Inf) # with minmax
   print (time.time()-prev_time)
   #tree_build(boardc,3,True,-np.Inf,np.Inf)
   #print(min_score)
   return move


def position_eval(boardc):#evaluates horisontal and vertical and diagonal positions
   ##horisontal  
   eval=0

   center = [int(i) for i in list(boardc[:,3])]
   center_count = center.count(1)
   eval += center_count*4

   for row in range(6):
     row_ar = [int(i) for i in list(boardc[row,:])]
     for col in range(4):
         four =  row_ar[col:col+4]
         #print(four)
         #print(col)
         eval += eval_four(four)
         #print("horisontell")
        # print(eval)
         

   ##vertical
   for col in range(7):
     col_ar = [int(i) for i in list(boardc[:,col])]
     for row in range(3):
         four =  col_ar[row:row+4]
         #print(four)
         #print(col)
         eval += eval_four(four)
         #print("vertikal")
         #print(eval)
   

   #diagonal left to right decending correct
   for row in range(3):
      for col in range(4):
       four = [boardc[row+i][col+i] for i in range(4)]
       eval += eval_four(four)
   
   #diagonal left to right upward correct
   for row in range(3):
      for col in range(4):
       four = [boardc[5-row-i][col+i] for i in range(4)]
       eval += eval_four(four)
   #print(eval)
   return eval

def eval_four(four):    #evaluation need to be tuned but the algorithm theory works
   eval  = 0
   if four.count(1) == 4:     #win        FIXED
      eval += 1000000
   elif four.count(1) == 3 and four.count(0) == 1:     # win in 2 moves
      eval += 100
   elif four.count(1) == 2 and four.count(0) == 2: # win in 3 moves
      eval += 3
   elif four.count(1) == 1 and four.count(0) == 3:
     eval+=1
   elif four.count(-1) == 3 and four.count(1)==1:
      eval+=150
   #elif four.count(-1) == 2 and four.count(1) == 1:
   #   eval+=9

   if four.count(-1) == 4:  #prevent loss
      eval -= 1000000
   elif four.count(-1) == 3 and four.count(0) == 1:
      eval -= 150
   #elif four.count(-1) == 2 and four.count(0) == 2:
   #   eval -= 7
   #elif four.count(-1) == 2 and four.count(0) == 2:
    #  eval -= 1
        

   return eval

#def find_best_move(boardc):
#   avmoves = list(env.available_moves())  #implement where to drop piece
#   best_eval = -10000
#   eval = 0
#   best_col = random.choice(avmoves)

#   for col in avmoves:
#      row = get_row(boardc,col)
#      temp = boardc.copy()
#      temp[row][col] = 1
#      eval = position_eval(temp)
#     # print("eval")
#     # print(eval)
#      if eval > best_eval:
#         best_eval = eval
#        # print("best eval")
#        # print(best_eval)
#         best_col = col
#         #print("best col")
#         #print(best_col)
#      #print(best_col)
#      #print(best_eval)
#   return best_col
      
def legal_moves(board):
   legal_col = [0,1,2,3,4,5,6]
   for col in range(7):
      if board[0][col] == 1 or board[0][col] == -1:
         legal_col.remove(col)
   return legal_col

def get_row(board, col): # checks in what row a piece can be dropped for the column
	for row in range(6):
		if board[5-row][col] == 0:
			return 5-row

def is_term_node(board):
   return len(legal_moves(board))==0 or is_player_win(board) or is_bot_win(board)

def is_player_win(board):
   return position_eval(board) >= 10000

def is_bot_win(board):     
   
   return position_eval(board) <= -8000



def minimax(boardc, depth, player, alpha, beta): #fix bad minmax algorithm, endless loop fixed
   #print(player)
   #print(depth)
   avmoves = legal_moves(boardc)

   #print(depth)
   if depth == 0 or is_term_node(boardc):
      #print("depth=0")
      if is_term_node(boardc):
         if is_player_win(boardc): #win
            #print("win")
            return(None, 100000000000000)
            #return (None, 100000000000000)
         elif is_bot_win(boardc): #loss 
            #print("loss")
            return(None, -100000000000000)
         else: #draw
            return(None, 0)
      else: #depth = 0 and no win or draw evaluate position made
         #print("eval time")
         return(None, position_eval(boardc))
   
   if player:        #calculate maximizing player score do for every possible move, create new node recursively 
      #print("hej")        
      value = -np.Inf
      col = random.choice(avmoves)
      for column in avmoves: 
         row = get_row(boardc,column)
         temp = boardc.copy()
         temp[row][column] = 1
         score = minimax(temp, depth-1,alpha,beta,False)[1]
         if score > value:
            value = score
            col = column
         alpha = max(alpha,value)
         if alpha >=beta:
            #print("break")
            break 
      #print(col)
      #print("max")
      #print(value)   
      return col,value
   else:
     # print("hejhej")
      value = np.Inf
      col = random.choice(avmoves)
      for column in avmoves:
         row = get_row(boardc,column)
         temp = boardc.copy()
         #print("temp")
         #print(temp)
         temp[row][column] = -1
         score =minimax(temp, depth-1,alpha,beta,True)[1]
         if score < value:
            value = score
            col = column
         beta = min(beta,value)
         if alpha >=beta:
            break 
         #print("min")
         #print(value)        
      return col,value

   

def play_game(vs_server = False):
   """
   The reward for a game is as follows. You get a
   botaction = random.choice(list(avmoves)) reward from the
   server after each move, but it is 0 while the game is running
   loss = -1
   win = +1
   draw = +0.5
   error = -10 (you get this if you try to play in a full column)
   Currently the player always makes the first move
   """

   # default state
   state = np.zeros((6, 7), dtype=int)

   # setup new game
   if vs_server:
      # Start a new game
      res = call_server(-1) # -1 signals the system to start a new game. any running game is counted as a loss

      # This should tell you if you or the bot starts
      print(res.json()['msg'])
      botmove = res.json()['botmove']
      state = np.array(res.json()['state'])
      env.reset(board=state)
   else:
      # reset game to starting state
      env.reset(board=None)
      # determine first player
      student_gets_move = random.choice([True, False])
      if student_gets_move:
         print('You start!')
         print()
      else:
         print('Bot starts!')
         print()

   # Print current gamestate
   print("Current state (1 are student discs, -1 are servers, 0 is empty): ")
   print(state)
   print()

   done = False
   while not done:
      # Select your move
      stmove = student_move() # TODO: change input here

      # make both student and bot/server moves
      if vs_server:
         # Send your move to server and get response
         res = call_server(stmove)
         print(res.json()['msg'])

         # Extract response values
         result = res.json()['result']
         botmove = res.json()['botmove']
         state = np.array(res.json()['state'])
         env.reset(board=state)
      else:
         if student_gets_move:
            # Execute your move
            avmoves = env.available_moves()
            if stmove not in avmoves:
               print("You tied to make an illegal move! You have lost the game.")
               break
            state, result, done, _ = env.step(stmove)

         student_gets_move = True # student only skips move first turn if bot starts

         # print or render state here if you like

         # select and make a move for the opponent, returned reward from students view
         if not done:
            state, result, done = opponents_move(env)

      # Check if the game is over
      if result != 0:
         done = True
         if not vs_server:
            print("Game over. ", end="")
         if result == 1:
            print("You won!")
         elif result == 0.5:
            print("It's a draw!")
         elif result == -1:
            print("You lost!")
         elif result == -10:
            print("You made an illegal move and have lost!")
         else:
            print("Unexpected result result={}".format(result))
         if not vs_server:
            print("Final state (1 are student discs, -1 are servers, 0 is empty): ")
      else:
         print("Current state (1 are student discs, -1 are servers, 0 is empty): ")

      # Print current gamestate
      print(state)
      print()

def main():
   # Parse command line arguments
   parser = argparse.ArgumentParser()
   group = parser.add_mutually_exclusive_group()
   group.add_argument("-l", "--local", help = "Play locally", action="store_true")
   group.add_argument("-o", "--online", help = "Play online vs server", action="store_true")
   parser.add_argument("-s", "--stats", help = "Show your current online stats", action="store_true")
   args = parser.parse_args()

   # Print usage info if no arguments are given
   if len(sys.argv)==1:
      parser.print_help(sys.stderr)
      sys.exit(1)

   if args.local:
      play_game(vs_server = False)
   elif args.online:
      play_game(vs_server = True)

   if args.stats:
      stats = check_stats()
      print(stats)

   # TODO: Run program with "--online" when you are ready to play against the server
   # the results of your games there will be logged
   # you can check your stats bu running the program with "--stats"

if __name__ == "__main__":
    main()


