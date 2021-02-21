from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
import json
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from chess.models import *
from django.core import serializers
from django.contrib.auth.decorators import user_passes_test
import math

# Create your views here.
gameData = {
    "a1": "w-rook",
    "a2": "w-pawn",
    "a3": "",
    "a4": "",
    "a5": "",
    "a6": "",
    "a7": "b-pawn",
    "a8": "b-rook",

    "b1": "w-knight",
    "b2": "w-pawn",
    "b3": "",
    "b4": "",
    "b5": "",
    "b6": "",
    "b7": "b-pawn",
    "b8": "b-knight",

    "c1": "w-bishop",
    "c2": "w-pawn",
    "c3": "",
    "c4": "",
    "c5": "",
    "c6": "",
    "c7": "b-pawn",
    "c8": "b-bishop",

    "d1": "w-queen",
    "d2": "w-pawn",
    "d3": "",
    "d4": "",
    "d5": "",
    "d6": "",
    "d7": "b-pawn",
    "d8": "b-queen",

    "e1": "w-king",
    "e2": "w-pawn",
    "e3": "",
    "e4": "",
    "e5": "",
    "e6": "",
    "e7": "b-pawn",
    "e8": "b-king",

    "f1": "w-bishop",
    "f2": "w-pawn",
    "f3": "",
    "f4": "",
    "f5": "",
    "f6": "",
    "f7": "b-pawn",
    "f8": "b-bishop",

    "g1": "w-knight",
    "g2": "w-pawn",
    "g3": "",
    "g4": "",
    "g5": "",
    "g6": "",
    "g7": "b-pawn",
    "g8": "b-knight",

    "h1": "w-rook",
    "h2": "w-pawn",
    "h3": "",
    "h4": "",
    "h5": "",
    "h6": "",
    "h7": "b-pawn",
    "h8": "b-rook",
}
piece = "false"
square1 = "false"
square2 = "false"
enPassant = "false"
inCheck = "false"
wCastleLeft = "true"
wCastleRight = "true"
bCastleLeft = "true"
bCastleRight = "true"
checkmate = "false"
pgn = []
pgnOutput = ""
loser = "white"
drawOffer = "false"
firstTurn = True
turn = "w"
myTurn = "none"
players = []
player1 = "false"
player2 = "false"
gameHistory = []
endComment = ""
checks = []
rejected = False

def is_player(user):
    global players, rejected
    if len(players) == 2:
        if user.username in players:
            return True
        else:
            rejected = True
            return False
    else:
        return True

def index(request):
    global rejected
    if rejected == True:
        messages.success(request, "Game is currently full.")
        rejected = False
    return render(request, "chess/home.html", {})

@login_required(login_url="login")
@user_passes_test(is_player, login_url="home")
def play(request):
    global checks, endComment, gameHistory, firstTurn, myTurn, gameData, piece, square1, square2, turn, enPassant, inCheck, pgn, wCastleLeft, wCastleRight, bCastleLeft, bCastleRight, pgnOutput, checkmate, loser, players, player1, player2

    if len(players) == 2:
        if request.user.username == players[0]:
            myTurn = "white"
        elif request.user.username == players[1]:
            myTurn = "black"

    if request.method == "POST":

        if request.POST["checkmate"] == "resign":
            if firstTurn == False:
                checkmate = request.POST["checkmate"]
                if myTurn == "white":
                    loser = "white"
                    pgn.append("0-1")
                    endComment = "White resigned. Black was victorious."
                elif myTurn == "black":
                    loser = "black"
                    pgn.append("1-0")
                    endComment = "Black resigned. White was victorious."
                if turn == "w":
                    turn = "b"
                else:
                    turn = "w"
        elif request.POST["checkmate"] == "drawOffer":
            if firstTurn == False:
                if myTurn == "white":
                    checkmate = "white"
                elif myTurn == "black":
                    checkmate = "black"
        elif request.POST["checkmate"] == "draw":
            if firstTurn == False:
                checkmate = request.POST["checkmate"]
                pgn.append("1/2-1/2")
                endComment = "Draw."
                if turn == "w":
                    turn = "b"
                else:
                    turn = "w"
        else:
            piece = request.POST["piece"]
            square1 = request.POST["square1"]
            square2 = request.POST["square2"]
            inCheck = request.POST["inCheck"]
            checkmate = request.POST["checkmate"]
            drawOffer = "false"
            firstTurn = False

            if inCheck == "true":
                checks.append(len(pgn))

            if piece[2:4] == "ki":
                if square1 == "g1" and wCastleRight == "true":
                    gameData["f1"] = "w-rook"
                    gameData["h1"] = ""

                if square1 == "c1" and wCastleLeft == "true":
                    gameData["d1"] = "w-rook"
                    gameData["a1"] = ""

                if square1 == "g8" and bCastleRight == "true":
                    gameData["f8"] = "b-rook"
                    gameData["h8"] = ""

                if square1 == "c8" and bCastleLeft == "true":
                    gameData["d8"] = "b-rook"
                    gameData["a8"] = ""


            if enPassant != "false":
                if square1 == enPassant[0]+str(int(enPassant[1])+1) and piece[0:4] == "w-pa":
                  gameData[enPassant] = ""
                elif square1 == enPassant[0]+str(int(enPassant[1])-1) and piece[0:4] == "b-pa":
                  gameData[enPassant] = ""


            gameData[square2] = ""
            gameData[square1] = piece

            enPassant = request.POST["enPassant"]
            wCastleLeft = request.POST["wCastleLeft"]
            wCastleRight = request.POST["wCastleRight"]
            bCastleLeft = request.POST["bCastleLeft"]
            bCastleRight = request.POST["bCastleRight"]

            gameHistory.append(gameData.copy())

            if len(pgn)%2 != 0:
                pgnOutput = ""
            else:
                pgnOutput = str(int(len(pgn)/2 + 1))+". "

            if checkmate == "true":
                if turn == "w":
                    pgn.append(pgnOutput+request.POST["pgn"][0:-1]+"# 1-0")
                    endComment = "Checkmate. White was victorious."
                else:
                    pgn.append(pgnOutput+request.POST["pgn"][0:-1]+"# 0-1")
                    endComment = "Checkmate. Black was victorious."
            elif checkmate == "stalemate":
                pgn.append(pgnOutput+request.POST["pgn"]+"1/2-1/2")
                endComment = "Stalemate."
            else:
                pgn.append(pgnOutput+request.POST["pgn"])
            turn = request.POST["turn"]
        if checkmate == "true" or checkmate == "stalemate" or checkmate == "resign" or checkmate == "draw":
            global game
            game = Game(player1=player1, player2=player2, pgn=''.join(pgn), endComment=endComment)
            game.save()

            for i in range(len(gameHistory)):
                board = Board(
                    game = game,
                    check = i in checks,
                    a1 = gameHistory[i]["a1"],
                    a2 = gameHistory[i]["a2"],
                    a3 = gameHistory[i]["a3"],
                    a4 = gameHistory[i]["a4"],
                    a5 = gameHistory[i]["a5"],
                    a6 = gameHistory[i]["a6"],
                    a7 = gameHistory[i]["a7"],
                    a8 = gameHistory[i]["a8"],

                    b1 = gameHistory[i]["b1"],
                    b2 = gameHistory[i]["b2"],
                    b3 = gameHistory[i]["b3"],
                    b4 = gameHistory[i]["b4"],
                    b5 = gameHistory[i]["b5"],
                    b6 = gameHistory[i]["b6"],
                    b7 = gameHistory[i]["b7"],
                    b8 = gameHistory[i]["b8"],

                    c1 = gameHistory[i]["c1"],
                    c2 = gameHistory[i]["c2"],
                    c3 = gameHistory[i]["c3"],
                    c4 = gameHistory[i]["c4"],
                    c5 = gameHistory[i]["c5"],
                    c6 = gameHistory[i]["c6"],
                    c7 = gameHistory[i]["c7"],
                    c8 = gameHistory[i]["c8"],

                    d1 = gameHistory[i]["d1"],
                    d2 = gameHistory[i]["d2"],
                    d3 = gameHistory[i]["d3"],
                    d4 = gameHistory[i]["d4"],
                    d5 = gameHistory[i]["d5"],
                    d6 = gameHistory[i]["d6"],
                    d7 = gameHistory[i]["d7"],
                    d8 = gameHistory[i]["d8"],

                    e1 = gameHistory[i]["e1"],
                    e2 = gameHistory[i]["e2"],
                    e3 = gameHistory[i]["e3"],
                    e4 = gameHistory[i]["e4"],
                    e5 = gameHistory[i]["e5"],
                    e6 = gameHistory[i]["e6"],
                    e7 = gameHistory[i]["e7"],
                    e8 = gameHistory[i]["e8"],

                    f1 = gameHistory[i]["f1"],
                    f2 = gameHistory[i]["f2"],
                    f3 = gameHistory[i]["f3"],
                    f4 = gameHistory[i]["f4"],
                    f5 = gameHistory[i]["f5"],
                    f6 = gameHistory[i]["f6"],
                    f7 = gameHistory[i]["f7"],
                    f8 = gameHistory[i]["f8"],

                    g1 = gameHistory[i]["g1"],
                    g2 = gameHistory[i]["g2"],
                    g3 = gameHistory[i]["g3"],
                    g4 = gameHistory[i]["g4"],
                    g5 = gameHistory[i]["g5"],
                    g6 = gameHistory[i]["g6"],
                    g7 = gameHistory[i]["g7"],
                    g8 = gameHistory[i]["g8"],

                    h1 = gameHistory[i]["h1"],
                    h2 = gameHistory[i]["h2"],
                    h3 = gameHistory[i]["h3"],
                    h4 = gameHistory[i]["h4"],
                    h5 = gameHistory[i]["h5"],
                    h6 = gameHistory[i]["h6"],
                    h7 = gameHistory[i]["h7"],
                    h8 = gameHistory[i]["h8"]
                )
                board.save()
        return render(request, "play/play.html", {
            "player": json.dumps({
    			"playerTurn" : myTurn,
                "player1": player1,
                "player2": player2,
                "turn": turn,
                "pgn": pgn,
                "inCheck": inCheck,
                "wCanCastle": [wCastleLeft, wCastleRight],
                "bCanCastle": [bCastleLeft, bCastleRight],
                "enPassant": enPassant
    		}),
            "gameData": json.dumps({
                "gameBoard": gameData
            })
        })

    elif request.is_ajax():
        return JsonResponse({
            "piece": piece,
            "square1": square1,
            "square2": square2,
            "turn": turn,
            "enPassant": enPassant,
            "inCheck": inCheck,
            "wCastleLeft": wCastleLeft,
            "wCastleRight": wCastleRight,
            "bCastleLeft": bCastleLeft,
            "bCastleRight": bCastleRight,
            "pgn": pgn,
            "checkmate": checkmate,
            "loser": loser,
            "player1": player1,
            "player2": player2
        })
    else:
        if checkmate == "true" or checkmate == "stalemate" or checkmate == "resign" or checkmate == "draw":
            gameData = {
                "a1": "w-rook",
                "a2": "w-pawn",
                "a3": "",
                "a4": "",
                "a5": "",
                "a6": "",
                "a7": "b-pawn",
                "a8": "b-rook",

                "b1": "w-knight",
                "b2": "w-pawn",
                "b3": "",
                "b4": "",
                "b5": "",
                "b6": "",
                "b7": "b-pawn",
                "b8": "b-knight",

                "c1": "w-bishop",
                "c2": "w-pawn",
                "c3": "",
                "c4": "",
                "c5": "",
                "c6": "",
                "c7": "b-pawn",
                "c8": "b-bishop",

                "d1": "w-queen",
                "d2": "w-pawn",
                "d3": "",
                "d4": "",
                "d5": "",
                "d6": "",
                "d7": "b-pawn",
                "d8": "b-queen",

                "e1": "w-king",
                "e2": "w-pawn",
                "e3": "",
                "e4": "",
                "e5": "",
                "e6": "",
                "e7": "b-pawn",
                "e8": "b-king",

                "f1": "w-bishop",
                "f2": "w-pawn",
                "f3": "",
                "f4": "",
                "f5": "",
                "f6": "",
                "f7": "b-pawn",
                "f8": "b-bishop",

                "g1": "w-knight",
                "g2": "w-pawn",
                "g3": "",
                "g4": "",
                "g5": "",
                "g6": "",
                "g7": "b-pawn",
                "g8": "b-knight",

                "h1": "w-rook",
                "h2": "w-pawn",
                "h3": "",
                "h4": "",
                "h5": "",
                "h6": "",
                "h7": "b-pawn",
                "h8": "b-rook",
            }


            piece = "false"
            square1 = "false"
            square2 = "false"
            enPassant = "false"
            inCheck = "false"
            wCastleLeft = "true"
            wCastleRight = "true"
            bCastleLeft = "true"
            bCastleRight = "true"
            checkmate = "false"
            pgn = []
            pgnOutput = ""
            loser = "white"
            drawOffer = "false"
            gameHistory = []
            endComment = ""
            checks = []

            turn = "w"

            players = []
            player1 = "false"
            player2 = "false"

        if len(players) == 0:
            players.append(request.user.username)
            player1 = players[0]
            myTurn = "white"
        elif len(players) == 1 and players[0] != request.user.username:
            players.append(request.user.username)
            player2 = players[1]
            myTurn = "black"

        return render(request, "play/play.html", {
            "player": json.dumps({
    			"playerTurn" : myTurn,
                "player1": player1,
                "player2": player2,
                "turn": turn,
                "pgn": pgn,
                "inCheck": inCheck,
                "wCanCastle": [wCastleLeft, wCastleRight],
                "bCanCastle": [bCastleLeft, bCastleRight],
                "enPassant": enPassant
    		}),
            "gameData": json.dumps({
                "gameBoard": gameData
            })
        })

def registerPage(request):
    form = UserCreationForm()

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get("username")
            messages.success(request, "Account was created for " + user)

            return redirect("login")
    return render(request, "chess/register.html", {
        "form": form
        })

def loginPage(request):
	if request.method == "POST":
		username = request.POST.get("username")
		password = request.POST.get("password")

		user = authenticate(request, username=username, password=password)

		if user is not None:
			login(request, user)
			return redirect("home")
	return render(request, "chess/login.html", {})

def logoutUser(request):
    global checkmate, myTurn, loser, pgn, turn
    if myTurn != "none" and len(players) == 2:
        checkmate = "resign"
        if myTurn == "white":
            loser = "white"
            pgn.append("0-1")
            endComment = "White resigned. Black was victorious."
        elif myTurn == "black":
            loser = "black"
            pgn.append("1-0")
            endComment = "Black resigned. White was victorious."
        if turn == "w":
            turn = "b"
        else:
            turn = "w"
        game = Game(player1=player1, player2=player2, pgn=''.join(pgn), endComment=endComment)
        game.save()

        for i in range(len(gameHistory)):
            board = Board(
                game = game,
                check = i in checks,
                a1 = gameHistory[i]["a1"],
                a2 = gameHistory[i]["a2"],
                a3 = gameHistory[i]["a3"],
                a4 = gameHistory[i]["a4"],
                a5 = gameHistory[i]["a5"],
                a6 = gameHistory[i]["a6"],
                a7 = gameHistory[i]["a7"],
                a8 = gameHistory[i]["a8"],

                b1 = gameHistory[i]["b1"],
                b2 = gameHistory[i]["b2"],
                b3 = gameHistory[i]["b3"],
                b4 = gameHistory[i]["b4"],
                b5 = gameHistory[i]["b5"],
                b6 = gameHistory[i]["b6"],
                b7 = gameHistory[i]["b7"],
                b8 = gameHistory[i]["b8"],

                c1 = gameHistory[i]["c1"],
                c2 = gameHistory[i]["c2"],
                c3 = gameHistory[i]["c3"],
                c4 = gameHistory[i]["c4"],
                c5 = gameHistory[i]["c5"],
                c6 = gameHistory[i]["c6"],
                c7 = gameHistory[i]["c7"],
                c8 = gameHistory[i]["c8"],

                d1 = gameHistory[i]["d1"],
                d2 = gameHistory[i]["d2"],
                d3 = gameHistory[i]["d3"],
                d4 = gameHistory[i]["d4"],
                d5 = gameHistory[i]["d5"],
                d6 = gameHistory[i]["d6"],
                d7 = gameHistory[i]["d7"],
                d8 = gameHistory[i]["d8"],

                e1 = gameHistory[i]["e1"],
                e2 = gameHistory[i]["e2"],
                e3 = gameHistory[i]["e3"],
                e4 = gameHistory[i]["e4"],
                e5 = gameHistory[i]["e5"],
                e6 = gameHistory[i]["e6"],
                e7 = gameHistory[i]["e7"],
                e8 = gameHistory[i]["e8"],

                f1 = gameHistory[i]["f1"],
                f2 = gameHistory[i]["f2"],
                f3 = gameHistory[i]["f3"],
                f4 = gameHistory[i]["f4"],
                f5 = gameHistory[i]["f5"],
                f6 = gameHistory[i]["f6"],
                f7 = gameHistory[i]["f7"],
                f8 = gameHistory[i]["f8"],

                g1 = gameHistory[i]["g1"],
                g2 = gameHistory[i]["g2"],
                g3 = gameHistory[i]["g3"],
                g4 = gameHistory[i]["g4"],
                g5 = gameHistory[i]["g5"],
                g6 = gameHistory[i]["g6"],
                g7 = gameHistory[i]["g7"],
                g8 = gameHistory[i]["g8"],

                h1 = gameHistory[i]["h1"],
                h2 = gameHistory[i]["h2"],
                h3 = gameHistory[i]["h3"],
                h4 = gameHistory[i]["h4"],
                h5 = gameHistory[i]["h5"],
                h6 = gameHistory[i]["h6"],
                h7 = gameHistory[i]["h7"],
                h8 = gameHistory[i]["h8"]
            )
            board.save()
    elif myTurn != "none" and len(players) == 1:
        checkmate = "resign"
    logout(request)
    return redirect('login')

def pastGames(request):
    return render(request, "games/games.html", {
        "games": Game.objects.all()
    })

def game(request, game_id):
    game_json = serializers.serialize('json', Game.objects.filter(pk=game_id)[0].moves.all())
    return render(request, "games/board.html", {
        "game_json": game_json,
        "player1": Game.objects.filter(pk=game_id)[0].player1,
        "player2": Game.objects.filter(pk=game_id)[0].player2,
        "pgn": Game.objects.filter(pk=game_id)[0].pgn,
        "endComment": Game.objects.filter(pk=game_id)[0].endComment
    })
