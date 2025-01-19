class GameState():
    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--" , "--", "--", "--", "--", "--", "--", "--"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["wp","wp","wp","wp","wp","wp","wp","wp"],
            ["wR","wN","wB","wQ","wK","wB","wN","wR"]
                     ]
        self.WTM = True #white to move
        self.movelog = []
        self.moveFunctions = {'p': self.getPawnMoves, 'R': self.getRookMoves, 'N':self.getKnightMoves,
                              'B': self.getBishopMoves, 'Q':self.getQueenMoves, 'K':self.getKingMoves}
        self.WKingLocation = (7,4)
        self.BKingLocation = (0,4)
        self.inCheck = False
        self.pins = []
        self.checks = []
        self.enpassantPossible = ()
        
    def makeMove(self, move):
        self.board[move.startrow][move.startcol] = "--"
        self.board[move.endrow][move.endcol] = move.pieceMoved
        self.movelog.append(move)
        self.WTM = not self.WTM
        if move.pieceMoved == "wK":
            self.WKingLocation = (move.endrow,move.endcol)
        elif move.pieceMoved == "bK":
            self.BKingLocation = (move.endrow,move.endcol)
        if move.isPawnPromotion:
            self.board[move.endrow][move.endcol] = move.pieceMoved[0] + "Q"
    
    def undoMove(self):
        if self.movelog == []:
            return
        else:
            move = self.movelog.pop()
            self.board[move.startrow][move.startcol] = move.pieceMoved
            self.board[move.endrow][move.endcol] = move.piececaptured
            self.WTM = not self.WTM
            if move.pieceMoved == "wK":
                self.WKingLocation = (move.startrow,move.startcol)
            elif move.pieceMoved == "bK":
                self.BKingLocation = (move.startrow,move.startcol)

    def getValidMoves(self):
        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndCheck()
        if self.WTM:
            kingrow = self.WKingLocation[0]
            kingcol = self.WKingLocation[1]
        else:
            kingrow = self.BKingLocation[0]
            kingcol = self.BKingLocation[1]
            
        if self.inCheck:
            if len(self.checks) == 1:
                moves = self.getAllMoves()
                check = self.checks[0]
                checkRow = check[0]
                checkCol = check[1]
                pieceCheck = self.board[checkRow][checkCol]
                validsquares = []
                if pieceCheck[1] == "N":
                    validsquares = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8):
                        validsquare = (kingrow + check[2]*i, kingcol + check[3]*i)
                        validsquares.append(validsquare)
                        if validsquare[0] == checkRow and validsquare[1] == checkCol:
                            break
                    for i in range(len(moves)-1, -1, -1):
                        if moves[i].pieceMoved[1] != "K":
                            if not (moves[i].endrow, moves[i].endcol) in validsquares:
                                moves.remove(moves[i])
            else:
                self.getKingMoves(kingrow, kingcol, moves)
            
        else:
            moves = self.getAllMoves()
            
        return moves
            
        
    def checkForPinsAndCheck(self):
        pins = []
        checks = []
        inCheck = False
        if self.WTM:
            enemycolour = "b"
            allycolour = "w"
            startrow = self.WKingLocation[0]
            startcol = self.WKingLocation[1]
        else:
            enemycolour = "w"
            allycolour = "b"
            startrow = self.BKingLocation[0]
            startcol = self.BKingLocation[1]
            
        directions = [(-1,0),(0,-1),(1,0),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = ()
            for i in range(1, 8):
                endrow = startrow + (d[0]*i)
                endcol = startcol + (d[1]*i)
                
                if 0 <= endrow < 8  and 0 <= endcol < 8:
                    endpiece = self.board[endrow][endcol]
                    if endpiece[0] == allycolour and endpiece[1] != "K":
                        if possiblePin == ():
                            possiblePin = (endrow, endcol, d[0], d[1])
                        else:
                            break
                    elif endpiece[0] == enemycolour:
                        type = endpiece[1]
                        if (0 <= j <= 3 and type == "R") or (4 <= j <= 7 and type == "B") or (i == 1 and type == "p" and ((enemycolour == "w" and 6<=j<=7) or (enemycolour == "b" and 4<=j<=5))) or (type == "Q") or (i == 1 and type == "K"):
                            if possiblePin == ():
                                inCheck = True
                                checks.append((endrow, endcol, d[0], d[1]))
                                break
                            else:
                                pins.append(possiblePin)
                                break
                        else:
                            break
                else:
                    break
        knightMoves = ((2,1),(-2,1),(2,-1),(-2,-1),(1,2),(-1,2),(1,-2),(-1,-2))
        for m in knightMoves:
            endrow = m[0] + startrow
            endcol = m[1] + startcol
            if 0 <= endrow <= 7 and 0 <= endcol <= 7:
                endpiece = self.board[endrow][endcol]
                if endpiece[0] == enemycolour and endpiece[1] == "N":
                    inCheck = True
                    checks.append((endrow, endcol, m[0], m[1]))
        return inCheck, pins, checks
                                        
                
            
            
            

    def getAllMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == "w" and self.WTM) or (turn == "b" and not self.WTM):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r,c,moves)

        return moves


    def getPawnMoves(self,r,c,moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        if self.WTM:
            if r!= 0:
                if self.board[r-1][c] == "--":
                    if not piecePinned or pinDirection == (-1,0):
                        moves.append(Move((r, c), (r-1, c), self.board))
                        if r == 6 and self.board[r-2][c] == "--":
                            moves.append(Move((r, c), (r-2, c), self.board))

                if c-1 >= 0:
                    if self.board[r-1][c-1][0] == 'b':
                        if not piecePinned or pinDirection == (-1,-1):
                            moves.append(Move((r, c), (r-1, c-1), self.board))

                if c+1 <= 7:
                    if self.board[r-1][c+1][0] == 'b':
                        if not piecePinned or pinDirection == (-1,1):
                            moves.append(Move((r, c), (r-1, c+1), self.board))

        else:
            if r!= 7:
                if self.board[r+1][c] == "--":
                    if not piecePinned or pinDirection == (1,0):
                        moves.append(Move((r, c), (r+1, c), self.board))
                        if r == 1 and self.board[r+2][c] == "--":
                            moves.append(Move((r, c), (r+2, c), self.board))

                if c-1 >= 0 and r != 7:
                    if self.board[r+1][c-1][0] == 'w':
                        if not piecePinned or pinDirection == (1,-1):
                            moves.append(Move((r, c), (r+1, c-1), self.board))

                if c+1 <= 7 and r!= 7:
                    if self.board[r+1][c+1][0] == 'w':
                        if not piecePinned or pinDirection == (1,1):
                            moves.append(Move((r, c), (r+1, c+1), self.board))

    def getRookMoves(self,r,c,moves):
        directions = [(0,1),(0,-1),(1,0),(-1,0)]
        enemyPiece = "b" if self.WTM else "w"
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != "Q":
                    self.pins.remove(self.pins[i])
                break
        for d in directions:
            for i in range(1,8):
                endrow = r + (d[0]*i)
                endcol = c + (d[1]*i)
                if 0 <= endrow < 8  and 0 <= endcol < 8:
                    if not piecePinned or pinDirection == d or pinDirection == (- d[0], - d[1]):
                        endpiece = self.board[endrow][endcol]
                        if endpiece == "--":
                            moves.append(Move((r,c), (endrow, endcol), self.board))
                        elif endpiece[0] == enemyPiece:
                            moves.append(Move((r,c), (endrow, endcol), self.board))
                            break
                        else:
                            break
                else:
                    break
                        
    def getKnightMoves(self,r,c,moves):
        piecePinned = False
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break
        directions = [(2,1),(-2,1),(2,-1),(-2,-1),(1,2),(-1,2),(1,-2),(-1,-2)]
        allyPiece = "w" if self.WTM else "b"
        for d in directions:
            endrow = r + d[0]
            endcol = c + d[1]
            if 0 <= endrow < 8  and 0 <= endcol < 8:
                if not piecePinned:
                    endpiece = self.board[endrow][endcol]
                    if endpiece[0] != allyPiece:
                        moves.append(Move((r,c), (endrow, endcol), self.board))

    def getBishopMoves(self,r,c,moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        directions = [(1,1),(-1,-1),(1,-1),(-1,1)]
        enemyPiece = "b" if self.WTM else "w"
        for d in directions:
            for i in range(1,8):
                endrow = r + (d[0]*i)
                endcol = c + (d[1]*i)
                if 0 <= endrow < 8  and 0 <= endcol < 8:
                    if not piecePinned or pinDirection == d or pinDirection == (- d[0], - d[1]):
                        endpiece = self.board[endrow][endcol]
                        if endpiece == "--":
                            moves.append(Move((r,c), (endrow, endcol), self.board))
                        elif endpiece[0] == enemyPiece:
                            moves.append(Move((r,c), (endrow, endcol), self.board))
                            break
                        else:
                            break
                else:
                    break
    
    def getQueenMoves(self,r,c,moves):
        self.getBishopMoves(r,c,moves)
        self.getRookMoves(r,c,moves)

    def getKingMoves(self,r,c,moves):
        rowMoves = (-1, -1, -1, 0, 0, 1, 1, 1)
        colMoves = (-1, 0, 1, -1, 1, -1, 0, 1)
        allyPiece = "w" if self.WTM else "b"
        for i in range(8):
            endrow = r + rowMoves[i]
            endcol = c + colMoves[i]
            if 0 <= endrow < 8  and 0 <= endcol < 8:
                endpiece = self.board[endrow][endcol]
                if endpiece[0] != allyPiece:
                    if allyPiece == "w":
                        self.WKingLocation = (endrow, endcol)
                    else:
                        self.BKingLocation = (endrow, endcol)
                    inCheck, pins, checks = self.checkForPinsAndCheck()
                    if not inCheck:
                        moves.append(Move((r,c), (endrow, endcol), self.board))
                    if allyPiece == "w":
                        self.WKingLocation = (r,c)
                    else:
                        self.BKingLocation = (r,c)

        
class Move():
    ranktoRows = {"1":7 , "2":6, "3":5, "4":4, "5":3, "6":2, "7":1, "8":0}
    rowstoRanks = {k:v for v,k in ranktoRows.items()}
    filestoCol = {"a":0, "b":1, "c":2, "d":3, "e":4, "f":5, "g":6, "h":7}
    coltoFiles = {k:v for v,k in filestoCol.items()}

    def __init__(self, startsq, endsq, board):
        self.startrow = startsq[0]
        self.startcol = startsq[1]
        self.endrow = endsq[0]
        self.endcol = endsq[1]
        self.pieceMoved = board[self.startrow][self.startcol]
        self.piececaptured = board[self.endrow][self.endcol]
        self.moveID = self.startrow*1000 + self.startcol*100 + self.endrow*10 + self.endcol
        self.isPawnPromotion = False
        if (self.pieceMoved == "wp" and self.endrow == 0) or (self.pieceMoved == "bp" and self.endrow == 7):
            self.isPawnPromotion = True
        self.isenpassantMove = False

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False
    def getChessNotation(self):
        return self.getRankFile(self.startrow,self.startcol) + self.getRankFile(self.endrow,self.endcol)
    
    def getRankFile(self, r, c):
        return self.coltoFiles[c] + self.rowstoRanks[r]

      
