import socketio
import eventlet

# create a Socket.IO server
sio = socketio.Server()
app = socketio.WSGIApp(sio)

rooms = []

# Event handler for connected client
@sio.on("connect")
def connect(sid, environ):
    print("Client connected: ", sid)
    # suto join room after connected
    join_room(sid)


# Event handler for disconnected client
@sio.on("disconnect")
def disconnect(sid):
    print("Client disconnected:", sid)
    # check if the disconnected client is in any room
    leave_room(sid)


# Event handler for starting the game
@sio.on("start_game")
def start_game(sid):
    for room in rooms:
        if sid in room["player"] and room["status"] == "playing": # check the player's room
            print("game started")
            # send the role (X or O) for each client
            sio.emit(
                "role",
                {"role": "x", "room": room},
                room=rooms.index(room),
                to=room["player"][0],
            )
            sio.emit(
                "role",
                {"role": "o", "room": room},
                room=rooms.index(room),
                to=room["player"][1],
            )
            break


# called when client is connected
def join_room(sid):
    room = None
    for i in range(len(rooms)):
        if len(rooms[i]["player"]) < 2: # assign to the room that have < 2 player
            rooms[i]["player"].append(sid)
            if len(rooms[i]["player"]) == 2:
                rooms[i]["status"] = "playing"

            room = rooms[i]
            break

    if room == None: # create new room if all rooms are full
        room = {
            "player": [sid],
            "board": [[None] * 3, [None] * 3, [None] * 3],
            "turn": "x",
            "turn_pos": [],
            "winner": None,
            "draw": False,
            "status": "waiting",
        }
        rooms.append(room)
        print("Room created:", room)

    # add the client to the specified room
    sio.enter_room(sid, rooms.index(room))

    # emit the updated client list to the room
    sio.emit(
        "message", {"sid": sid, "player": len(room["player"])}, room=rooms.index(room)
    )

    print("Client", sid, "joined room", rooms.index(room), "room:", room)


# called when client is disconnected
def leave_room(sid):
    # check if the client is in the specified room
    for i in range(len(rooms)):
        if sid in rooms[i]["player"]:
            rooms[i]["player"].remove(sid)
            if rooms[i]["status"] == "playing":
                rooms[i] = reset_game(rooms[i])
            sio.leave_room(sid, i)
            sio.emit(
                "message",
                {"disconnected": sid, "player": len(rooms[i]["player"])},
                room=i,
            )
            print("Client", sid, "removed from room", i)
            break

# called when the game is over
def reset_game(room):
    room["board"] = [[None] * 3, [None] * 3, [None] * 3]
    room["turn"] = "x"
    room["winner"] = None
    room["draw"] = False
    room["status"] = "waiting"
    room["turn_pos"] = []
    return room


# to check the winner or draw
def check_win(room):
    board = room["board"]

    # checking for winning rows
    for row in range(0, 3):
        if (board[row][0] == board[row][1] == board[row][2]) and (
            board[row][0] is not None
        ):
            room["winner"] = board[row][0]
            break

    # checking for winning columns
    for col in range(0, 3):
        if (board[0][col] == board[1][col] == board[2][col]) and (
            board[0][col] is not None
        ):
            room["winner"] = board[0][col]
            break

    # check for diagonal winner
    if (board[0][0] == board[1][1] == board[2][2]) and (board[0][0] is not None):
        # game won diagonally left to right
        room["winner"] = board[0][0]

    if (board[0][2] == board[1][1] == board[2][0]) and (board[0][2] is not None):
        # game won diagonally right to left
        room["winner"] = board[0][2]

    if all(all(row) for row in board) and room["winner"] is None:
        room["draw"] = True

    if room["winner"] is not None or room["draw"]:
        room["status"] = "finished"
    return room


# Event handler for receiving and broadcasting messages
@sio.on("turn")
def handle_turn(sid, data):
    print("turn", sid, data)
    for i in range(len(rooms)):
        if sid in rooms[i]["player"] and rooms[i]["status"] == "playing":
            rooms[i]["board"][data[0] - 1][data[1] - 1] = rooms[i]["turn"]
            rooms[i]["turn_pos"] = data
            rooms[i] = check_win(rooms[i])
            sid_idx = rooms[i]["player"].index(sid)
            rooms[i]["turn"] = "o" if rooms[i]["turn"] == "x" else "x"
            if rooms[i]["winner"] or rooms[i]["draw"]: # send to all players if the game is over
                sio.emit(
                    "turn",
                    {"room": rooms[i]},
                    room=i,
                )
                rooms[i] = reset_game(rooms[i])
            else: # send to enemy player
                sio.emit(
                    "turn",
                    {"room": rooms[i]},
                    room=i,
                    to=rooms[i]["player"][0 if sid_idx else 1],
                )
            break


if __name__ == "__main__":
    eventlet.wsgi.server(eventlet.listen(("", 8000)), app)
