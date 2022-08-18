# Todo
# - message what's wrong when errors

import random
from enum import Enum, unique, auto

DICE_SIDES = 6
DICE_COUNT = 5
ROLLS_PER_ROUND = 3
BONUS_THRESHOLD = 63
BONUS_SIZE = 35

@unique
class Action(Enum):
	Invalid = auto()
	Next = auto()
	Fix = auto()
	Unfix = auto()
	Assign = auto()

class Player(object):
	def __parseUserInput(self, user_input):
		parts = user_input.split(' ')
		action_arg = parts[0]
		action = Action.Invalid
		if action_arg in ['fix', 'f'] :
			action = Action.Fix
		elif action_arg in ['unfix', 'u']:
			action = Action.Unfix
		elif action_arg in ['assign', 'a']:
			action = Action.Assign
		elif action_arg == '':
			action = Action.Next
		
		args = []
		if len(parts) > 1:
			args = parts[1:]
		return action, args

	def nextAction(self, game_state):
		user_input = input()
		return self.__parseUserInput(user_input)

class Rules(object):
	def pointsForNumber(number):
		return lambda dices: number * dices.count(number)

	def pointsForChoice(dices):
		return sum(dices)

	def pointsFor4k(dices):
		for value in set(dices):
			if dices.count(value) > 3:
				return sum(dices)
		return 0

	def pointsForFullHouse(dices):
		digits = set(dices)
		if len(digits) != 2:
			return 0
		for digit in digits:
			if dices.count(digit) == 3:
				return sum(dices)
		return 0

	def pointsForSmallStraight(dices):
		dices = (set(dices))
		if not 3 in dices or not 4 in dices:
			return 0
		if 5 in dices:
			if 2 in dices or 6 in dices:
				return 15
		elif 1 in dices and 2 in dices:
			return 15
		return 0

	def pointsForLargeStraight(dices):
		dices.sort()
		for i in range(len(dices)-1):
			if dices[i+1] - dices[i] != 1:
				return 0
		return 30

	def pointsForYacht(dices):
		if len(set(dices)) == 1:
			return 50
		return 0

	categories = {
		'1': pointsForNumber(1),
		'2': pointsForNumber(2),
		'3': pointsForNumber(3),
		'4': pointsForNumber(4),
		'5': pointsForNumber(5),
		'6': pointsForNumber(6),
		'Ch': pointsForChoice,
		'4k': pointsFor4k,
		'FH': pointsForFullHouse,
		'SS': pointsForSmallStraight,
		'LS': pointsForLargeStraight,
		'Y!': pointsForYacht
	}

def fillUpTo(chars_num, s):
	if len(s) >= chars_num:
		return s
	return s + ' ' * (chars_num - len(s))

CATEGORIES_IN_TITLE = ''
for category in Rules().categories:
	CATEGORIES_IN_TITLE += fillUpTo(3, category)
TITLE = "Dealt • Fixed • " + CATEGORIES_IN_TITLE + 'Bo Total'

class GameState(object):
	currentThrow = 0
	rolled = []
	fixed = []
	categoryPoints = {}
	bonusPoints = 0
	bonusCalculated = False

class Game(object):
	state = GameState()
	rules = Rules()
	
	def __init__(self):
		super(Game, self).__init__()
		self.state.rolled = [0] * DICE_COUNT

	def rollDices(self):
		self.state.currentThrow += 1
		for i in range(len(self.state.rolled)):
			num = random.randint(1, DICE_SIDES)
			self.state.rolled[i] = num
		self.state.rolled.sort()

	def roundsAvailable(self):
		return len(self.state.categoryPoints) < len(self.rules.categories)

	def rollsAvailableInRound(self):
		return ROLLS_PER_ROUND - self.state.currentThrow > 0

	def isValidAction(self, action, args):
		if action == Action.Assign:
			category = args[0]
			if category not in self.rules.categories:
				return False
			return not category in self.state.categoryPoints
		if self.rollsAvailableInRound() == 0:
			return action == Action.Assign
		return action in [Action.Fix, Action.Unfix, Action.Next]

	def fix(self, number):
		if number in self.state.rolled:
			self.state.rolled.remove(number)
			self.state.fixed.append(number)
		self.state.fixed.sort()

	def unfix(self, number):
		if number in self.state.fixed:
			self.state.fixed.remove(number)
			self.state.rolled.append(number)
		self.state.rolled.sort()

	def updateBonus(self):
		if self.state.bonusCalculated:
			return
		bonus_score = 0
		bonus_categoies_count = 0
		for i in range(DICE_SIDES):
			number = str(i + 1)
			if number in self.state.categoryPoints:
				bonus_score += self.state.categoryPoints[number]
				bonus_categoies_count += 1
		if bonus_score >= BONUS_THRESHOLD:
			self.state.bonusPoints = BONUS_SIZE
			self.state.bonusCalculated = True
		elif bonus_categoies_count == DICE_SIDES:
			self.state.bonusPoints = 0
			self.state.bonusCalculated = True

	def assignTo(self, category):
		self.state.rolled += self.state.fixed
		points = self.rules.categories[category](self.state.rolled)
		self.state.categoryPoints[category] = points

		self.updateBonus()

		self.state.currentThrow = 0
		self.state.rolled = [0] * DICE_COUNT
		self.state.fixed = []

	def total(self):
		return sum([v for k, v in self.state.categoryPoints.items()]) + self.state.bonusPoints

	def categoriesPresentation(self):
		output = ''
		for category in self.rules.categories:
			points = '_' 
			if category in self.state.categoryPoints:
				points = str(self.state.categoryPoints[category])
			output += fillUpTo(3, points)
		return output
	
	def displayState(self):
		if self.roundsAvailable():
			print('\n-- Round %d, roll %d --' % (len(self.state.categoryPoints) + 1, self.state.currentThrow))
		else:
			print()
		print(TITLE)

		output = ''
		for dice in self.state.rolled:
			output += '%i' % dice
		output += ' ' * (DICE_COUNT - len(self.state.rolled))
		output += '   '
		
		for dice in self.state.fixed:
			output += '%i' % dice
		output += ' ' * (DICE_COUNT - len(self.state.fixed))
		output += '   '

		output += self.categoriesPresentation()

		if self.state.bonusCalculated:
			output += fillUpTo(3, str(self.state.bonusPoints))
		else:
			output += '_  '

		output += '%i' % self.total()
		print(output)

	def playWith(self, player):
		enter_another_action = False
		while game.roundsAvailable():
			if not enter_another_action:
				game.rollDices()
				game.displayState()
			
			action = Action.Invalid
			args = []
			while not game.isValidAction(action, args):
				if action != Action.Invalid:
					print('invalid action')
				action, args = player.nextAction(game.state)
			
			enter_another_action = False
			if action == Action.Fix:
				for number in args:
					game.fix(int(number))
				enter_another_action = True
			elif action == Action.Unfix:
				for number in args:
					game.unfix(int(number))
				enter_another_action = True
			elif action == Action.Assign:
				game.assignTo(args[0])
		
		game.displayState()
		print('\nGame Over\n')

game = Game()
player = Player()
game.playWith(player)