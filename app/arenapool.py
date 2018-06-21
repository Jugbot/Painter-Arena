from multiprocessing import Process,Queue,Pipe, Pool
from sortedcontainers import SortedList


class OpenArena:
    def __init__(self, id, skill):
        self.id = id
        self.skill = skill

    def __lt__(self, other):
        return self.skill < other.skill


from sortedcontainers import SortedList
class Matchmaker:

    def __init__(self, data=list()):
        self.pool = SortedList(data)

    def find(self, skillscore, radius):
        if not self.pool:
            return None

        ind = self.pool.bisect_left(OpenArena(-1, skillscore))
        right = self.pool[ind]
        left = None if ind == 0 else self.pool[ind-1]
        if left and right:
            dl = skillscore - left.skill
            dr = right.skill - skillscore
            if dr < radius or dl < radius:
                if dl > dr:
                    return right.id
                else:
                    return left.id
        elif left:
            dl = skillscore - left.skill
            if dl < radius:
                return left.id
        elif right:
            dr = right.skill - skillscore
            if dr < radius:
                return right.id

        return None

    def add(self, id, skill):
        self.pool.add(OpenArena(id, skill))

    def remove(self, skill):
        self.pool.remove(skill)


if __name__ == '__main__':
    m = Matchmaker()
    print("All None:", m.find(0,0), m.find(0,-10), m.find(10,0))
    m.add(13, 1000)
    print("All None, 13, 13:\n\t", m.find(0, 50), m.find(1000, 10), m.find(998, 50))
    m.add(20, 990)
    print("All None, 13, 13, 20:\n\t", m.find(0, 50), m.find(1000, 10), m.find(998, 50), m.find(991, 50))


# def init(_in, _out):
#     apool = Matchmaker()
#     while True:
#         req, *args = pipe.recv()
#         if req == 'find':
#             result = apool.find(*args)
#             pipe.send(result)
#         elif req == 'add':
#             apool.add(*args)
#         else:
#             print("Error: unknown request", req)