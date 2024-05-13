import os

class HalmaBoard:
    def __init__(self):
        self.size = 16
        self.board = [[0 for i in range(self.size)] for j in range(self.size)] #creating a 16x16 empty board
        self.bestMove = []

        for col in range(5):
            self.board[0][col] = 1
        
        for row in range(1, 5):
            for col in range(6 - row):
                self.board[row][col] = 1
        
        for col in range(5):
            self.board[self.size - 1][self.size - 1 - col] = 2

        for row in range(1, 5):
            for col in range(6 - row):
                self.board[self.size - 1 - row][self.size - 1 - col] = 2

    def checkValidMoves(self, x, y, comingFromX, comingFromY,playerTurn, playAgain):
        possibleMoves = []

        if self.board[y][x] != playerTurn:
            return possibleMoves
        #print("Entering check")
        if y >= 0 and y < self.size and x >= 0 and x < self.size:
            if self.board[y][x] == playerTurn:
                for r in [-1, 0, 1]:
                    for c in [-1, 0, 1]:
                        if y + r > -1 and y + r < self.size and x + c > -1 and x + c < self.size:
                            if self.board[y+r][x+c] == 0 and not(playAgain):
                                possibleMoves.append([y, x, y+r, x+c]) #Adding y and x in order to keep track of previous position
                                #self.board[y+r][x+c] = 5
                                playAgain = False
                            elif self.board[y+r][x+c] == 1 or self.board[y+r][x+c] == 2:
                                if y + 2*r >= 0 and y + 2*r < self.size and x + 2*c >= 0 and x + 2*c < self.size:
                                    if self.board[y+2*r][x+2*c] == 0:
                                        playAgain = True
                                        if y+2*r == comingFromY and x + 2*c == comingFromX:
                                            continue
                                        possibleMoves.append([y, x, y+2*r, x+2*c]) #Same as above
                                        #self.board[y+2*r][x+2*c] = 5
                                        self.makeMove(y, x, y+2*r, x+2*c, playerTurn)
                                        newMoves = self.checkValidMoves(x+2*c, y+2*r, x, y, playerTurn, True)
                                        self.unmakeMove(y, x, y+2*r, x+2*c, playerTurn)
                                        if playAgain:
                                            for move in newMoves:
                                                move[0] = y
                                                move[1] = x
                                            possibleMoves.extend(newMoves)
        
        return possibleMoves, playAgain

    
    #maybe modify generate legal moves to play again if leapping

    def generateLegalMoves(self, turn):
        legalMoves = []
        for r in range(self.size):
            for c in range(self.size):
                if self.board[r][c] == turn:
                    moves = self.checkValidMoves(c, r, -1, -1, turn, False)
                    legalMoves.extend(moves)
        return legalMoves


    def heuristics(self, maximizingPlayer):
        score = 0

        campRatioWeight = 10
        distanceWeight = 10
        inEnemyCampWeight = 100

        #The closer most pawns are to the enemy camp the bigger the score gets
        distSum = 0
        meanDistance = 0
        for r in range(self.size):
            for c in range(self.size):
                if self.board[r][c] == maximizingPlayer:
                    distSum += self.distance(r, c, maximizingPlayer)

        meanDistance = distSum / 19

        score += (1 / meanDistance) * distanceWeight

        #If the opponent has more pawns out and the player has pawns in, then the opponent cannot fill the camp, 
        #so I consider it a good to have pawns in when the opponent has a lot out
        if maximizingPlayer == 1:
            if self.getBlackInBlackCamp() > 0:
                score += campRatioWeight * (self.getWhiteInWhiteCamp() / self.getBlackInBlackCamp())
            score += inEnemyCampWeight * self.getWhiteInBlackCamp() #Big score for collecting pawns in the enemie's camp
        else:
            if self.getWhiteInWhiteCamp() > 0:
                score += campRatioWeight * (self.getBlackInBlackCamp() / self.getWhiteInWhiteCamp())
            score += inEnemyCampWeight * self.getBlackInWhiteCamp()


        return score

    def minimax(self, depth, maximizingPlayer, maximizingTurn):
        if maximizingPlayer == 1 and self.getWhiteInBlackCamp() == 19:
            return self.heuristics(maximizingPlayer)
        elif maximizingPlayer == 2 and self.getBlackInWhiteCamp() == 19:
            return self.heuristics(maximizingPlayer)

        if depth == 0:
            return self.heuristics(maximizingPlayer)
        
        moves = self.generateLegalMoves(maximizingPlayer)

        if maximizingTurn:
            maxEva = float('-inf') 
            for move in moves:
                self.makeMove(move[0], move[1], move[2], move[3], maximizingPlayer)
                eva = self.minimax(depth - 1, maximizingPlayer % 2 + 1, False)
                self.unmakeMove(move[0], move[1], move[2], move[3], maximizingPlayer)
                if eva > maxEva:
                    maxEva = eva
            return maxEva
        
        else:
            minEva = float('+inf')
            for move in moves:
                self.makeMove(move[0], move[1], move[2], move[3], maximizingPlayer)
                eva = self.minimax(depth - 1, maximizingPlayer % 2 + 1, True)
                self.unmakeMove(move[0], move[1], move[2], move[3], maximizingPlayer)
                if eva < minEva:
                    minEva = eva
            return minEva

    def alphabeta(self, depth, alpha, beta, maximizingPlayer, maximizingTurn):
        if depth == 0 or self.end():
            return self.heuristics(maximizingPlayer)
        
        moves = self.generateLegalMoves(maximizingPlayer)

        if maximizingTurn:
            maxEva = float('-inf')
            for move in moves:
                self.makeMove(move[0], move[1], move[2], move[3], maximizingPlayer)
                eva = self.alphabeta(depth - 1, alpha, beta, maximizingPlayer % 2 + 1, False)
                self.unmakeMove(move[0], move[1], move[2], move[3], maximizingPlayer)
                if eva > maxEva:
                    maxEva = eva
                if maxEva > alpha:
                    alpha = maxEva
                if beta <= alpha:
                    break
                
            return maxEva
        
        else:
            minEva = float('+inf')
            for move in moves:
                self.makeMove(move[0], move[1], move[2], move[3], maximizingPlayer)
                eva = self.alphabeta(depth - 1, alpha, beta, maximizingPlayer % 2 + 1, True)
                self.unmakeMove(move[0], move[1], move[2], move[3], maximizingPlayer)
                if eva < minEva:
                    minEva = eva
                if minEva < beta:
                    beta = minEva
                if beta <= alpha:
                    break

            return minEva

    def getWhiteInWhiteCamp(self):
        count = 0

        for col in range(5):
            if self.board[0][col] == 1:
                count += 1

        for row in range(1, 5):
            for col in range(6 - row):
                if self.board[row][col] == 1:
                    count += 1
        return count

    def getBlackInBlackCamp(self):
        count = 0

        for col in range(5):
            if self.board[self.size - 1][self.size - 1 - col] == 2:
                count += 1

        for row in range(1, 5):
            for col in range(6 - row):
                if self.board[self.size - 1 - row][self.size - 1 - col] == 2:
                    count += 1
        return count

    def getWhiteInBlackCamp(self):
        count = 0

        for col in range(5):
            if self.board[self.size - 1][self.size - 1 - col] == 1:
                count += 1

        for row in range(1, 5):
            for col in range(6 - row):
                if self.board[self.size - 1 - row][self.size - 1 - col] == 1:
                    count += 1
        return count

    def getBlackInWhiteCamp(self):
        count = 0

        for col in range(5):
            if self.board[0][col] == 2:
                count += 1

        for row in range(1, 5):
            for col in range(6 - row):
                if self.board[row][col] == 2:
                    count += 1
        return count


    def distance(self, row, column, maximizingPlayer):
        if maximizingPlayer == 1:
            return (16 - row) ^ 2 + (16 - column) ^ 2
        else:
            return (row + 1) ^ 2 + (column + 1) ^ 2


    def makeMove(self, fromY, fromX, toY, toX, turn):
        self.board[fromY][fromX] = 0
        self.board[toY][toX] = turn

    def unmakeMove(self, fromY, fromX, toY, toX, turn):
        self.board[fromY][fromX] = turn
        self.board[toY][toX] = 0

    def moveGeneration(self, depth, turn):
        if depth == 0:
            return 1
        
        moves = self.generateLegalMoves(turn)
        numPositions = 0
        temp = turn
        if temp == 1: 
            temp = 2
        else:
            temp = 1
        for move in moves:
            self.makeMove(move[0], move[1], move[2], move[3], turn)
            numPositions += self.moveGeneration(depth - 1, temp)
            self.unmakeMove(move[0], move[1], move[2], move[3], turn)
        return numPositions

    def move(self, turn):
        curPos = []
        nextPos = []
        validMoves = []
        print(str(turn) + "'s turn")
        print("Choose what you are moving: (row, column, starting from zero)")
        curPos = list(map(int, input().strip().split(',')))
        if self.board[curPos[0]][curPos[1]] == turn:
            validMoves = self.checkValidMoves(curPos[1], curPos[0], -1, -1, turn, False)
            print(validMoves)
            self.printBoard()
            print("Where do you want to move?")
            nextPos = list(map(int, input().strip().split(',')))
            checkPos = curPos + nextPos
            print(checkPos)
            if checkPos in validMoves:
                self.makeMove(checkPos[0], checkPos[1], checkPos[2], checkPos[3], turn)
            else:
                print("Invalid move")

    def end(self):
        return self.getBlackInWhiteCamp == 19 or self.getWhiteInBlackCamp == 19

    def printBoard(self):
        for row in self.board:
            print(' '.join(map(str, row)))


moves = []
halmaBoard = HalmaBoard()
halmaBoard.printBoard()
#moves = halmaBoard.checkValidMoves(3, 2, 1)
print()
halmaBoard.printBoard()
#evaluationScore = halmaBoard.alphabeta(4, float('-inf'), float('inf'), 1, True)
evaluationScore = halmaBoard.moveGeneration(1, 1)

print(evaluationScore)
turn = 1
while not(halmaBoard.end()):
    os.system('cls')
    halmaBoard.printBoard()
    halmaBoard.move(turn)
    halmaBoard.printBoard()
    turn = turn % 2 + 1
    print("Press Enter to continue")
    a = input()

#print()
#halmaBoard.move(1)
#print()
#halmaBoard.printBoard()
#print(moves)