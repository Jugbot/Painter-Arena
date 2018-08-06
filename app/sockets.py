from flask_socketio import Namespace, emit, join_room, leave_room
from app import socketio

class Arena_Room(Namespace):
    def on_connect(self):
        print('connect ')
        # emit('player_join', room=self.room)

    def on_disconnect(self):
        print("disconnect ")
        # leave_room(self.room)
        # emit('player_leave', room=self.room)

    def on_subscribe(self, id):
        print("join ", id)
        join_room(id)

    def on_unsubscribe(self, id):
        print("leave ", id)
        leave_room(id)

    def emit_player_join(self, user):
        print("emit_join ")
        socketio.emit('player_join', {user.username: {
                             'avatar': user.avatar,
                             'entry': user.entry,
                             'votes': user.votes_received
                             }}, room=user.arena_id, namespace=self.namespace)

    def emit_player_leave(self, user):
        print("emit_leave ")
        socketio.emit('player_leave', {"username": user.username}, room=user.arena_id, namespace=self.namespace)

    def emit_entry_update(self, user, entry):
        print('emit_entry ')
        socketio.emit('entry_update', {user.username: { 'entry':entry}}, room=user.arena_id, namespace=self.namespace)

    def emit_votes_changed(self, user):
        print('emit_votes ')
        socketio.emit('votes_changed', {user.username: { 'votes': user.votes_received }}, room=user.arena_id, namespace=self.namespace)

    def emit_new_notification(self, room, notif):
        print('emit_notification ', room)
        socketio.emit('new_notification', {'message': notif.message, 'type': notif.type}, room=room, namespace=self.namespace)

    def emit_arena_end(self, user):
        print('emit_arena_end ')
        socketio.emit('arena_end', room=user.arena_id, namespace=self.namespace)


arena_room = Arena_Room('/sock')
socketio.on_namespace(arena_room)