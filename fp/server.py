import socketio
import eventlet

# create a Socket.IO server
sio = socketio.Server()
app = socketio.WSGIApp(sio)

rooms = []


@sio.on("connect")
def connect(sid, environ):
    print("Client connected: ", sid)
    join_room(sid)


@sio.on("disconnect")
def disconnect(sid):
    print("Client disconnected:", sid)
    # Check if the disconnected client is in any room
    leave_room(sid)


# Event handler for joining a room
def join_room(sid):
    room = None
    for i in range(len(rooms)):
        if len(rooms[i]["player"]) < 2:
            rooms[i]["player"].append(sid)
            if len(rooms[i]["player"]) == 2:
                rooms[i]["status"] = "playing"

            room = rooms[i]
            break

    if room == None:
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

    # Add the client to the specified room
    sio.enter_room(sid, rooms.index(room))

    # Emit the updated client list to the room
    sio.emit("message", {"sid": sid}, room=rooms.index(room))

    print("Client", sid, "joined room", rooms.index(room), "room:", room)
    if room["status"] == "playing":
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


def leave_room(sid):
    # Check if the client is in the specified room
    for i in range(len(rooms)):
        if sid in rooms[i]["player"]:
            rooms[i]["player"].remove(sid)
            if rooms[i]["status"] == "playing":
                rooms[i] = reset_game(rooms[i])
            sio.leave_room(sid, i)
            sio.emit(
                "message",
                {"disconnected": sid},
                room=i,
            )
            print("Client", sid, "removed from room", i)
            break


def reset_game(room):
    room["board"] = [[None] * 3, [None] * 3, [None] * 3]
    room["turn"] = "x"
    room["winner"] = None
    room["status"] = "waiting"
    return room


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

    if room["winner"] is not None:
        room["status"] = "finished"

    if all(all(row) for row in board) and room["winner"] is None:
        room["draw"] = True
    return room


# Event handler for receiving and broadcasting messages
@sio.on("turn")
def handle_turn(sid, data):
    for i in range(len(rooms)):
        if sid in rooms[i]["player"] and rooms[i]["status"] == "playing":
            rooms[i]["board"][data[0]][data[1]] = rooms[i]["turn"]
            rooms[i]["turn"] = "o" if rooms[i]["turn"] == "x" else "x"
            rooms[i]["turn_pos"] = data
            rooms[i] = check_win(rooms[i])
            sio.emit("turn", {"room": rooms[i]}, room=i)
            if rooms[i]["winner"]:
                rooms[i] = reset_game(rooms[i])
            break


if __name__ == "__main__":
    eventlet.wsgi.server(eventlet.listen(("", 8000)), app)
