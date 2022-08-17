# Todo
# - message what's wrong when errors

import random

DICE_SIDES = 6
DICE_COUNT = 5
ROLLS_PER_ROUND = 3
BONUS_THRESHOLD = 63
BONUS_SIZE = 35

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
	dices = sorted(list(set(dices)))
	if len(dices) < 4:
		return 0
	one_diff_count = 0
	for i in range(len(dices)-1):
		if dices[i+1] - dices[i] == 1:
			one_diff_count += 1
			if one_diff_count == DICE_COUNT - 2:
				return 15
		else:
			return 0
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
for category in categories:
	CATEGORIES_IN_TITLE += fillUpTo(3, category)
TITLE = "Dealt • Fixed • " + CATEGORIES_IN_TITLE + 'Bo Total'

class GameState(object):
	currentThrow = 0
	rolled = []
	fixed = []
	categoryPoints = {}
	bonusPoints = 0
	bonusCalculated = False

	def __init__(self):
		super(GameState, self).__init__()
		self.rolled = [0] * DICE_COUNT

	def rollDices(self):
		self.currentThrow += 1
		for i in range(len(self.rolled)):
			num = random.randint(1, DICE_SIDES)
			self.rolled[i] = num
		self.rolled.sort()

	def roundsAvailable(self):
		return len(self.categoryPoints) < len(categories)

	def rollsAvailableInRound(self):
		return ROLLS_PER_ROUND - self.currentThrow > 0

	def isValidCommand(self, command, args):
		if command in ['assign', 'a']:
			category = args[0]
			if category not in categories:
				return False
			return not category in self.categoryPoints
		if self.rollsAvailableInRound() == 0:
			return command in ['assign', 'a']
		return command in ['fix', 'unfix', '', 'f', 'u']

	def fix(self, number):
		if number in self.rolled:
			self.rolled.remove(number)
			self.fixed.append(number)
		self.fixed.sort()

	def unfix(self, number):
		if number in self.fixed:
			self.fixed.remove(number)
			self.rolled.append(number)
		self.rolled.sort()

	def updateBonus(self):
		if self.bonusCalculated:
			return
		bonus_score = 0
		bonus_categoies_count = 0
		for i in range(DICE_SIDES):
			number = str(i + 1)
			if number in self.categoryPoints:
				bonus_score += self.categoryPoints[number]
				bonus_categoies_count += 1
		if bonus_score >= BONUS_THRESHOLD:
			self.bonusPoints = BONUS_SIZE
			self.bonusCalculated = True
		elif bonus_categoies_count == DICE_SIDES:
			self.bonusPoints = 0
			self.bonusCalculated = True

	def assignTo(self, category):
		self.rolled += self.fixed
		points = categories[category](self.rolled)
		self.categoryPoints[category] = points

		self.updateBonus()

		self.currentThrow = 0
		self.rolled = [0] * DICE_COUNT
		self.fixed = []

	def total(self):
		return sum([v for k, v in self.categoryPoints.items()]) + self.bonusPoints

	def categoriesPresentation(self):
		output = ''
		for category in categories:
			points = '_' 
			if category in self.categoryPoints:
				points = str(self.categoryPoints[category])
			output += fillUpTo(3, points)
		return output
	
	def displayState(self):
		if self.roundsAvailable():
			print('\n-- Round %d, roll %d --' % (len(self.categoryPoints) + 1, self.currentThrow))
		else:
			print()
		print(TITLE)

		output = ''
		for dice in self.rolled:
			output += '%i' % dice
		output += ' ' * (DICE_COUNT - len(self.rolled))
		output += '   '
		
		for dice in self.fixed:
			output += '%i' % dice
		output += ' ' * (DICE_COUNT - len(self.fixed))
		output += '   '

		output += self.categoriesPresentation()

		if self.bonusCalculated:
			output += fillUpTo(3, str(self.bonusPoints))
		else:
			output += '_  '

		output += '%i' % self.total()
		print(output)

def parseUserInput(user_input):
	args = []
	parts = user_input.split(' ')
	command = parts[0]
	if len(parts) > 1:
		args = parts[1:]
	return command, args

game = GameState()
enter_another_command = False
while game.roundsAvailable():
	if not enter_another_command:
		game.rollDices()
		game.displayState()
	
	command = '-'
	args = []
	while not game.isValidCommand(command, args):
		if command != '-':
			print('invalid command')
		user_input = input()
		command, args = parseUserInput(user_input)
	
	enter_another_command = False
	if command in ['fix', 'f'] :
		for number in args:
			game.fix(int(number))
		enter_another_command = True
	elif command in ['unfix', 'u']:
		for number in args:
			game.unfix(int(number))
		enter_another_command = True
	elif command in ['assign', 'a']:
		game.assignTo(args[0])

game.displayState()
print('\nGame Over\n')