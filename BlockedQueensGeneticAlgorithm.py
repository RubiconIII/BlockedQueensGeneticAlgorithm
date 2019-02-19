#Blocked Queens Genetic Solver - Curtis P. Hohl - 2/15/19
    
from textwrap import wrap
import random
import operator
import time
import math
import datetime

BLOCKED_COORDS = [(2,3), (4,1), (5,5)] #any blocked coords on the board? 0-based
BOARD_SIZE = 7 #size of the board, 0-based
POPULATION_SIZE = 100 #how many in each population
TOP_INDIVIDUALS_TO_KEEP = 1 #how many of the top to keep in each cycle
MUTATE_PROB = .001 #probability of mutation

def runGeneration(num_queens):
    global POPULATION_SIZE
    global TOP_INDIVIDUALS_TO_KEEP
    global MUTATE_PROB
    
    num_to_breed = POPULATION_SIZE - TOP_INDIVIDUALS_TO_KEEP 
    solution_found = False
    last_fitness = 100 #some big unreachable number for the first fitness
    latest_population = [createIndividual(num_queens) for x in range(POPULATION_SIZE)] #create the initial population based on the global size
    generation_number = 0
    mutate_prob = MUTATE_PROB
    
    while(solution_found == False):
        scored_population = []
        for individual in latest_population:
            board = makeBoard() #get the board
            fit_score = testFitness(individual, board) #get the fitness score
            scored_population.append((individual, fit_score)) #store the individual and the fitness score together
        scored_population.sort(key = operator.itemgetter(1)) #sort the scored population by the fitness score
        top_performer = scored_population[0] #grab the top performer

        if(top_performer[1] < last_fitness): #if this generations top performer has a better fitness than the last gen
            print("Generation number: {}. Has fitness: {}. Mutation probability: {}".format(generation_number, top_performer[1], mutate_prob)) #then tell me about it
            
        if (top_performer[1] == 0): #if this top performer is a solution
            print("Found a solution: {}.".format(top_performer[0])) #then tell me about it
            printBoard(top_performer[0]) #and print out the board
            solution_found = True #exit condition
            
        elif(top_performer[1] != 0): #otherwise, if there's no solution in this population
            saved_individuals = []
            new_population = []
            for num in range(TOP_INDIVIDUALS_TO_KEEP):
                saved_individuals.append(scored_population[num][0]) #save the top performers
            for num in range(num_to_breed): #breed the rest
                new_population.append(breed(scored_population, mutate_prob)) #and add them to the new population
            new_population.extend(saved_individuals) #add in the top performers 
            latest_population = new_population
            generation_number += 1
            last_fitness = top_performer[1]
            mutate_prob *= 1.000001 #increase the mutation probability
            if(generation_number % 100000 == 0):
                print("Generation number: {}. Has fitness: {}. Mutation probability: {}".format(generation_number, top_performer[1], mutate_prob)) #tell me about my progress
    

#make two parents conceive a child
def breed(population, mutate_prob):
    global BLOCKED_COORDS
    global POPULATION_SIZE
    global TOP_INDIVIDUALS_TO_KEEP

    num_to_breed = POPULATION_SIZE - TOP_INDIVIDUALS_TO_KEEP

    #birds and bees chosen at random index of population between 0 and num_to_breed: more fit individuals more commonly chosen, falling off linearly towards num_to_breed
    birds = population[math.floor(abs(random.uniform(0, 1) - random.uniform(0, 1) * (1 + num_to_breed - 0) + 0))][0]
    bees = population[math.floor(abs(random.uniform(0, 1) - random.uniform(0, 1) * (1 + num_to_breed - 0) + 0))][0]
    child = ""
    do_mutation = random.random() < mutate_prob #should we do a mutation?
    
    for num in range(len(birds)): #for all of the numbers
        swapper = bool(random.getrandbits(1)) #random true/false
        if (swapper == True): #either take one from the bird
            child += birds[num]
        elif (swapper == False): #or the bee
            child += bees[num]
    if(do_mutation == True): #if the mutation should be done
        child = list(child) #make the child a list, so we can edit
        child[random.randint(0, len(child) - 1)] = random.randint(0, BOARD_SIZE) #change a random member of the string
        child = "".join(str(char) for char in child) #convert back to a string
    parsed_encoding_and_blocks = wrap(child, 2) #create a list of tuple coords from encoding
    formatted_blocks = []
    for x, y in BLOCKED_COORDS: #for all the tuple coords
        formatted_blocks.append("".join((str(x), str(y)))) #format them like the parsed encoding
    parsed_encoding_and_blocks.extend(formatted_blocks) #add the encoding and blocks together
    if (len(set(parsed_encoding_and_blocks)) != len(parsed_encoding_and_blocks) and do_mutation == False): #if there was a duplicate and no mutation
        return breed(population, 0) #breed again without a mutation
    elif(len(set(parsed_encoding_and_blocks)) != len(parsed_encoding_and_blocks) and do_mutation == True): #if there was no duplicate and a mutation
        return breed(population, 1) #breed again with a mutation
    else:
        return child
            
#print out a board for passed in individual
def printBoard(individual):
    board = makeBoard()
    parsed_encoding = wrap(individual, 2) #split up the input string every 2 characters
    
    #fill in the queens
    for coord in parsed_encoding:
        x = int(coord[0])
        y = int(coord[1])
        board[x][y] = "♕" 
    
    #print out the board
    for row in zip(*board): 
        print(" ".join(row))
        
#create a (str)individual that documents the coords of queens on the board
def createIndividual(num_queens):
    individual = []
    while(1): #keep going until we have enough coords
        if not individual: #if individual is empty
            x, y = generateUnblockedRandomCoords() #get x and y
            individual.append((x, y)) #and append them to our list
        elif (len(individual) < num_queens): #if we dont have enough coords yet
            x, y = generateUnblockedRandomCoords() #generate some coords
            if (x, y) not in individual: #if they aren't already existing
                individual.append((x, y)) #append them to our coord list
            else:
                continue #otherwise, try again
        else:
            return "".join("%s%s" % coords for coords in individual) #finally, return the individual as a string

#generate coords that aren't blocked
def generateUnblockedRandomCoords():
    global BOARD_SIZE
    global BLOCKED_COORDS
    
    individual_coords = []
    x = random.randint(0, BOARD_SIZE) #x is a random number within our board size
    y = random.randint(0, BOARD_SIZE) #y is a random number within our board size
    isBlocked = False #by default we assume the coord is valid
    for (xx, yy) in BLOCKED_COORDS: #for every one of the blocked coordinates
        if (x == xx and y == yy): #if the coord is on a blocked space
            isBlocked = True #this coord is labeled blocked
    if (isBlocked == True): #if blocked
        return generateUnblockedRandomCoords() #return a recursive process to regenerate coords
    else:
        return x, y #otherwise, return current coords

#Populate the board wiwth blocked coords
def makeBoard():
    global BOARD_SIZE
    
    board = [["▢" for x in range(BOARD_SIZE + 1)] for y in range(BOARD_SIZE + 1)] #create a board based on the given size
    
    #fill in the blocked spots
    for (xx, yy) in BLOCKED_COORDS:
        board[xx][yy] = "▣"
    return board   

#Test the fitness of a given individual on the given board.
def testFitness(individual, board):
    global BOARD_SIZE
    
    fit_score = 0
    parsed_encoding = wrap(individual, 2) #split up the input string every 2 characters
    
    #fill in the queens
    for coord in parsed_encoding:
        x = int(coord[0])
        y = int(coord[1])
        board[x][y] = "♕"
    
    for coord in parsed_encoding:
        x = int(coord[0])
        y = int(coord[1])
        for step in range(x + 1, BOARD_SIZE + 1): #check to the right of each queen
            if (board[step][y] == "♕"): #if another queen is found
                fit_score += 1 #increase the fitness score
            elif (board[step][y] == "▣"): #if a block is found
                break #stop going that direction
        for step in range(x - 1, -1, -1): #check to the left of each queen
            if (board[step][y] == "♕"): 
                fit_score += 1 
            elif (board[step][y] == "▣"): 
                break 
        for step in range(y + 1, BOARD_SIZE + 1): #check above each queen
            if (board[x][step] == "♕"):
                fit_score += 1
            elif (board[x][step] == "▣"):
                break
        for step in range(y - 1, -1, -1): #check below each queen
            if (board[x][step] == "♕"):
                fit_score += 1
            elif (board[x][step] == "▣"):
                break
         
        #define checks before loop to check coord validity
        check_x_diag = x + 1 #diag x value to check
        check_y_diag = y + 1 #diag y value to check
        while (check_x_diag <= BOARD_SIZE and check_y_diag <= BOARD_SIZE): #check diag right, down
            if (board[check_x_diag][check_y_diag] == "♕"): #if theres a queen
                fit_score += 1 #increase the score
            elif (board[check_x_diag][check_y_diag] == "▣"): #otherwise
                break
            check_x_diag += 1
            check_y_diag += 1
            
        check_x_diag = x - 1
        check_y_diag = y - 1
        while (check_x_diag >= 0 and check_y_diag >= 0): #check diag left, up
            if (board[check_x_diag][check_y_diag] == "♕"):
                fit_score += 1
            elif (board[check_x_diag][check_y_diag] == "▣"):
                break
            check_x_diag -= 1
            check_y_diag -= 1
            
        check_x_diag = x - 1
        check_y_diag = y + 1
        while (check_x_diag >= 0 and check_y_diag <= BOARD_SIZE): #check diag left, down
            if (board[check_x_diag][check_y_diag] == "♕"):
                fit_score += 1
            elif (board[check_x_diag][check_y_diag] == "▣"):
                break
            check_x_diag -= 1
            check_y_diag += 1
            
        check_x_diag = x + 1
        check_y_diag = y - 1
        while (check_x_diag <= BOARD_SIZE and check_y_diag >= 0): #check diag right, up
            if (board[check_x_diag][check_y_diag] == "♕"):
                fit_score += 1
            elif (board[check_x_diag][check_y_diag] == "▣"):
                break
            check_x_diag += 1
            check_y_diag -= 1
    return fit_score 
           
if __name__ == '__main__':
    numQueens = 11 #try putting this number of queens on the board

    print("Starting run for {} queen solution at:".format(numQueens))
    print(datetime.datetime.now())
    start = time.time()
    runGeneration(numQueens)
    end = time.time()
    print("Ran for: {} seconds\n".format(end-start))