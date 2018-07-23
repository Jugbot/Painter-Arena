from flask_socketio import Namespace, emit, join_room, leave_room
from app import socketio

class Arena_Room(Namespace):
    def on_connect(self):
        print('conn ')
        pass
        # emit('player_join', room=self.room)

    def on_disconnect(self):
        print("dc ")
        # leave_room(self.room)
        # emit('player_leave', room=self.room)

    def on_join(self, name, id):
        print("join ", id)
        join_room(id)
        self.emit_player_join(name, id)

    def emit_player_join(self, name, room):
        print("emit_join ", room)
        socketio.emit('player_join', {'username':name}, room=room, namespace=self.namespace)

    def emit_entry_update(self, name, entry, room):
        print('emit_entry ', room)
        socketio.emit('entry_update', {'username':name, 'data':entry}, room=room, namespace=self.namespace)

    def emit_votes_changed(self, name, votes, room):
        print('emit_votes ', room)
        socketio.emit('votes_changed', {'username': name, 'votes': votes}, room=room, namespace=self.namespace)


arena_room = Arena_Room('/sock')
socketio.on_namespace(arena_room)