#!/usr/local/python
import pprint
import random
import copy
import sys

class MapContext():
	def __init__(self, x, y, chk, rows):
		self.x = x
		self.y = y
		self.chk = chk
		self.checks = []
		self.energy = []
		self.rows = copy.deepcopy(rows)
		self.footmarks = []
		self.path = []
		self.last_pos_item = None

		for row_idx, row in enumerate(self.rows):
			for col_idx, column in enumerate(row):
				if column == "S":
					self.start = { "row": row_idx, "col": col_idx}
				elif column == "G":
					self.goal = { "row": row_idx, "col": col_idx}
				elif column == "C":
					self.checks.append({ "row": row_idx, "col": col_idx})
				elif column == "E":
					self.energy.append({ "row": row_idx, "col": col_idx})
		self.current = self.start

	def dump_footmarks(self):
		print >>sys.stderr, "".join(self.path)

	def set_lifepoint(self, point):
		self.life_point = point

	def get_lifepoint(self):
		return self.life_point

	def give_up(self):
		if self.life_point == 0:
			return True
		if self.is_dead_end() and self.last_pos_item != "C":
			return True
		return False

	def is_able_to_stop(self):
		if self.is_goal(self.current) and not self.exists_checkpoints():
			return True
		return False

	def is_dead_end(self):
		nexts = self.get_next_candidates()
		for next in nexts:
			if not next in self.footmarks:
				return False
		return True

	def exists_checkpoints(self):
			return self.chk != 0

	def remove_wall(self, nexts):
		return filter(lambda pos: self.rows[pos["row"]][pos["col"]] != "#", nexts)

	def find_checkpoint(self, nexts):
		for next in nexts:
			if self.is_checkpoint(next):
				return next
		return None

	def is_checkpoint(self, pos):
			return self.rows[pos["row"]][pos["col"]] == "C"

	def find_goal(self, nexts):
		for next in nexts:
			if self.is_goal(next):
				return next
		return None
		
	def is_goal(self, pos):
			return self.rows[pos["row"]][pos["col"]] == "G"

	def move_to_next(self, next):
			#if already passed, use life point to pass
			if next in self.footmarks:
				self.life_point -= 1
			self.current = next
			self.last_pos_item = self.rows[self.current["row"]][self.current["col"]] 

			if self.take_energy_drink(self.current):
				self.life_point += 20

			self.take_checkpoint()
			self.footmarks.append(self.current)
			self.path.append(self.current["direction"])

	def take_checkpoint(self):
		if self.is_checkpoint(self.current):
			self.checks = filter(lambda x: x["row"] != self.current["row"] or x["col"] != self.current["col"], self.checks)
			self.rows[self.current["row"]][self.current["col"]] = '.'
			self.chk -=1

	def take_energy_drink(self, pos):
		if self.is_energy_drink(pos):
			self.rows[pos["row"]][pos["col"]] = "."
			return True
		return False

	def is_energy_drink(self, pos):
		return self.rows[pos["row"]][pos["col"]] == "E"
		
	def to_pos(self, pos):
		return { "row": pos["row"], "col": pos["col"] }

	def dump(self):
		for idx, row in enumerate(self.rows):
			disp_row = copy.deepcopy(row)
			if self.current["row"] == idx:
				#pprint.pprint(disp_row)
				disp_row[self.current["col"]] = 'X'		
			print "".join(disp_row).rstrip()

	def get_next_candidates(self):
		possible_next = [{ "row": self.current["row"]+1, "col": self.current["col"], "score": 0, "direction": "D"}, { "row": self.current["row"]-1, "col": self.current["col"], "score": 0, "direction": "U"}, { "row": self.current["row"], "col": self.current["col"]+1, "score": 0, "direction": "R" }, { "row": self.current["row"], "col": self.current["col"]-1, "score": 0, "direction": "L" }]
		return self.remove_wall(possible_next)
	
	def get_nexts(self):
		possible_next = self.get_next_candidates()
		if self.exists_checkpoints():
			check = self.find_checkpoint(possible_next)
			if check:
				return [check]
		else:
			goal = self.find_goal(possible_next)
			if goal:
				return [goal]

		return possible_next

def check_dup(ctx_to_check, ctxs):
	for ctx in ctxs:
		if ctx.current == ctx_to_check.current and ctx.checks == ctx_to_check.checks:
			return True
	return False

def solve(ctx):
	history_ctxs = []
	next_ctxs = [ctx]
	while len(next_ctxs) != 0:
		ctxs = next_ctxs
		next_ctxs = []
		for cur_ctx in ctxs:
			nexts = cur_ctx.get_nexts()
			for idx, next in enumerate(nexts):
				cur_ctx.dump()
				print "===idx:%d next===" % idx
				pprint.pprint(next)

				new_ctx = copy.deepcopy(cur_ctx)
				new_ctx.move_to_next(next)

				if new_ctx.is_able_to_stop():
					new_ctx.dump_footmarks()
					return True
				if new_ctx.give_up():
					print "===give up -- idx:%d next===" % idx
					pprint.pprint(next)
					print("last:%s" % new_ctx.last_pos_item)
					history_ctxs.append(new_ctx)
					continue
				if check_dup(new_ctx, history_ctxs):
					history_ctxs.append(new_ctx)
					continue
				history_ctxs.append(new_ctx)
				next_ctxs.append(new_ctx)
		
	return False
	
def parse():
	f = open("map.txt", "r")
	lines = f.readlines()
	f.close()

	maps = []
	header = None
	idx = 0
	while idx < len(lines):
		x, y, chk = lines[idx].rstrip().split(" ", 2)
		x = int(x)
		y = int(y)
		chk = int(chk)

		#convert to two dimensional list
		data_lines = lines[idx+1:idx+y+1]
		rows = []
		for data_line in data_lines:
			columns = []
			for c in data_line:
				columns.append(c)
			rows.append(columns)
		maps.append(MapContext(x, y, chk, rows))

		idx += y + 1

	return maps

maps = parse()

life_point = 13000
for idx, map in enumerate(maps):
	print "Try to solve map #%d" % idx
	map.set_lifepoint(life_point)
	if solve(map):
		print "map #%d is solved" % idx
		life_point = map.get_lifepoint()
	else:
		print "map #%d is not solved" % idx
		break

print "Finish"
