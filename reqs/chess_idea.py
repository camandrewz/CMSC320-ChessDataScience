#!/usr/bin/env python
# coding: utf-8

# **Upsetting Chess Data Analysis! (WARNING: SAD)**
# 
# **Cameron Andrews**

# **Introduction:**
# 
# This aim of this project is to explore an interesting phenomenon within the world of chess, yet it will not focus on any human chess players. Instead this project will focus on chess matches between two opposing chess engines, of different and randomly selected ELO ratings.
# 
# At first you may believe that the chess engine with a higher ELO rating would always win, simply because chess is known to be a game of perfect information, and therefore the more skilled engine should win against a lesser skilled engine every time. However, by simulating thousands of games under these circumstances, it is noticeable that this is not the case, and that even when there is a large discrepancy amongst the two ELOs, an upset is still possible. This project will aim to analyze the occurrence of upsets between chess engines, and determine whether there may be telling signs of when an upset is possible, and perhaps even train a model to become the upset master.
# 
# But first, we must gather the data!

# **Data Creation:**
# 
# This project will utilize a famous chess engine called "Stockfish", and in the process we will create two different engines; one to play the white pieces, and one for the black pieces. At the beginning of each simulation we will randomly select an ELO rating between 200 and 2500 for each engine. For reference, the highest ranked human chess player in the world, Magnus Carlsen, currently has an ELO floating around 2800.
# 
# First, in order to run this script you will need to have access to the Stockfish executable (Downloadable from their website @ https://stockfishchess.org/download). After downloading, you will need to specify the executable path as seen in the code below.
# 
# After that you should be able to run this script and generate your own chess data to analyze. However, this script takes several hours to run, and therefore the script will first check to see whether this data has already been created as a CSV file, and use that instead.

# In[1]:


import chess
import pandas
import numpy as np
from os.path import exists
from stockfish import Stockfish
from io import StringIO

if not exists("chess_moves.csv"):

    # Set the number of simulations to run.
    NUM_SIMS = 100
    chess_df = pandas.DataFrame(columns=["FEN", "MOVES_DF", "NUM_MOVE_PAIRS", "RESULT", "WINNER", "WHITE_ELO", "BLACK_ELO", "UPSET"])

    for i in range(NUM_SIMS):

        # Configure Two StockFish Chess Engines of unique ELO ratings that will fight eachother
        white_stockfish = Stockfish("stockfish_14.1_win_x64_avx2/stockfish_14.1_win_x64_avx2.exe")
        white_elo = int(np.random.uniform(200, 2500))
        white_stockfish.set_elo_rating(white_elo)

        black_stockfish = Stockfish("stockfish_14.1_win_x64_avx2/stockfish_14.1_win_x64_avx2.exe")
        black_elo = int(np.random.uniform(200, 2500))
        black_stockfish.set_elo_rating(black_elo)

        # Initializing a new chess board
        board = chess.Board()

        # Creating a new DataFrame to Keep track of all moves in the game
        moves_df = pandas.DataFrame( columns=["FEN_BEFORE_MOVE", "MOVE_MADE", "TURN"])

        # Making moves until the game ends
        while not board.is_game_over():
            white_stockfish.set_fen_position(board.fen())
            white_next_move = white_stockfish.get_best_move()

            # Appending the current move to a separate DataFrame that tracks all moves made throughout a game
            moves_df = moves_df.append({"FEN_BEFORE_MOVE": board.fen(), "TURN": "WHITE", "MOVE_MADE": white_next_move}, ignore_index=True)
            board.push_uci(white_stockfish.get_best_move())

            black_stockfish.set_fen_position(board.fen())
            black_next_move = black_stockfish.get_best_move()

            # Must check if the game is already over before proceeding
            if black_next_move is not None:
                # Appending the current move to a separate DataFrame that tracks all moves made throughout a game
                moves_df = moves_df.append({"FEN_BEFORE_MOVE": board.fen(), "TURN": "BLACK", "MOVE_MADE": black_next_move}, ignore_index=True)
                board.push_uci(black_next_move)

        # Cleaning the string containing the game's outcome
        result = str(board.outcome(claim_draw=True).termination).replace("Termination.", "")

        # Checks the results of the game and sets a few different variables accordingly
        if result == "CHECKMATE":

            upset = False

            if board.outcome(claim_draw=True).winner == True:
                winner = "WHITE"

                if white_elo < black_elo:
                    upset = True
            else:
                winner = "BLACK"

                if black_elo < white_elo:
                    upset = True
        else:
            winner = None
            upset = "N/A"

        # Adds the game data to the main chess_df DataFrame
        chess_df = chess_df.append(
            {"FEN": board.fen(), "MOVES_DF": moves_df.to_csv(), "NUM_MOVE_PAIRS": board.fullmove_number, "RESULT": result,
             "WINNER": winner, "WHITE_ELO": white_elo, "BLACK_ELO": black_elo, "UPSET": upset}, ignore_index=True)

    # Writes the DataFrame to a CSV file
    chess_df.to_csv("chess_moves.csv")

else:
    # Reading preexisting moves generated from an earlier simulation
    chess_df = pandas.read_csv("chess_moves.csv")

    # Dropping the index column as it is repetitive
    chess_df = chess_df.iloc[:, 1:]

new_moves_column = []

# A little extra work has to be done to restore the moves of each game as a separate DataFrame per row
for fen, moves, num_move_pairs, result, winner, white_elo, black_elo, upset in chess_df.values:
    csv_string = StringIO(moves)
    moves_df = pandas.read_csv(csv_string, sep=",")
    moves_df = moves_df.iloc[:, 1:]
    new_moves_column.append(moves_df)

# Replacing old column continaing CSV strings with new column containing Pandas DataFrames
chess_df["MOVES_DF"] = new_moves_column

# Outputting the DataFrame
chess_df


# **What Now?**
# 
# So now that we have a Pandas DataFrame containing the results of our simulation, we can begin to explore the data and determine whether there are any common traits amongst games that ended in an upset.
# 
# But first, we must determine whether there are any upsets at all, and what percentage of matches ended in an upset.

# In[2]:


print("Ratio of Total Games that Ended in an Upset:")
print("Ended in Upset:", chess_df["UPSET"].value_counts()[True])
print("Didn't End in Upset:", chess_df["UPSET"].value_counts()[False], "\n")
percentage = round((chess_df["UPSET"].value_counts()[
                   True] / len(chess_df)) * 100, 3)
print(f"Percentage of Total Games that Ended in Upset: {percentage} %")


# Clearly it appears that a fairly significant number of games end up in an upset, even when it is essentially two computers battling it out.

# In[3]:


fen, moves, num_move_pairs, result, winner, white_elo, black_elo, upset = chess_df.values[0]

moves

