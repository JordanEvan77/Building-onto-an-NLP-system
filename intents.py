from vacuumenvironment import ACTION_TURN_LEFT, ACTION_TURN_RIGHT, ACTION_FORWARD
from vacuumenvironment import ACTION_SUCK, ACTION_UNSUCK
from vacuumenvironment import ACTION_MINE_GOLD, ACTION_UNLOAD_GOLD
from vacuumenvironment import ACTION_STOP
from agents.agentworldmodel import GOLD, DIRT, WALL, CLEAN, UNKNOWN
from agents.paths import path_to_position, path_to_any, path_to_exactly, path_from_to_position

STOP = [('actions', [ACTION_STOP])]

#############################
#  Information intents
#    agent information
#    find some dirt
#    find some gold

def intent_agent_info(self):
    self.log(f"I am at {self.worldmodel.current_position} and I am heading {self.worldmodel.heading}")
    batpct = "{:.2%}".format(self.agent.battery_level/self.agent.battery_capacity)
    self.log(f"My battery level is at {batpct}")
    self.log(f"My score is {self.agent.score()}")
    self.log(f"I am holding {self.agent.num_gold} gold and {self.agent.num_dirt} dirt")
    return STOP

def intent_find_objtype(self, objtype):
   squares = self.worldmodel.squares_with_state(objtype)
   if len(squares) == 0:
        self.log(f"There is no {objtype} that I know of.")
   else:
        self.log(f"There is some {objtype} at {squares[0]}.  Would you like me to get it for you?")
   return STOP 

def intent_find_dirt(self):
    return intent_find_objtype(self, DIRT)

def intent_find_gold(self):
    return intent_find_objtype(self, GOLD)

# new intent for warm up:
def intent_find_stuff(self, coord):
    self.log(f"Searching for stuff at {coord}")
    if self.worldmodel.state_at(coord) == GOLD:
        self.log(f"There is gold at {coord}!")
    elif self.worldmodel.state_at(coord) == DIRT:
        self.log(f"There is dirt at {coord}!")
    elif self.worldmodel.state_at(coord) == WALL:
        self.log(f"There is a wall at {coord}!")
    elif self.worldmodel.state_at(coord) == CLEAN:
        self.log(f"There is nothing at {coord}!")
    return STOP

# FINAL TASK
def intent_praise(self):
    self.log("Thanks, happy to be of service")
    return STOP

###################################
#  Turning and moving

def intent_turn(self, dir):
    self.log(f"Turning {dir}")
    actions = []
    if dir == 'left':
        actions = [ACTION_TURN_LEFT]
    elif dir == 'right':
        actions = [ACTION_TURN_RIGHT]
    elif dir == 'around':
        actions = [ACTION_TURN_LEFT, ACTION_TURN_LEFT]
    else:
        raise(Exception("Bad direction {dir}"))
    return [('actions', actions)]
       
def intent_forward_backward(self, fb, num):
    self.log(f"Moving {fb} {num} spaces")
    actions = []
    if fb == 'backward':
        actions += [ACTION_TURN_LEFT, ACTION_TURN_LEFT]
    actions += [ACTION_FORWARD] * num
    actions.append(ACTION_STOP)
    return [('actions', actions)]

#########################################
#  Goto
#    Go to a coordinate
#    Go home

def intent_goto(self, coord):
    if self.worldmodel.current_position == coord:
        self.log(f"I am already at {coord}")
        return STOP
    self.log(f"Going to {coord}")
    return [('path', path_to_position(self, coord))]

def intent_go_home(self):
    self.log("Going home")
    p = path_to_position(self, (1,1))
    return [('path', p), ('actions', [ACTION_STOP])]

###########################################
#  Dirt sucking
#    at a coordinate
#    find and suck
    
def intent_suck_dirt_at(self, coord):
    self.log(f"Sucking dirt at {coord}")
    if self.worldmodel.state_at(coord) != DIRT:
        self.log(f"There is no dirt at {coord}!")
        return STOP
    else:
        p = path_to_position(self, coord)
        if not p:
            self.log(f"There is no path from here to {coord}")
            return STOP
        else:
            return [('path', p), 
                    ('actions', [ACTION_SUCK, ACTION_STOP])]

def intent_suck_some_dirt(self):
    p = path_to_any(self, DIRT)
    if p == None:
        return [('explore_dirt')]
    elif len(p) == 0:
        return intent_suck_dirt_at(self, self.worldmodel.current_position)
    else:
        return intent_suck_dirt_at(self, p[-1])

#Second Task#
def intent_move_dirt_from(self, coord1, coord2):
    self.log(f"picking up dirt at {coord1}")
    if self.worldmodel.state_at(coord1) != DIRT:
        self.log(f"There is no dirt at {coord1}!")
        return STOP
    elif self.worldmodel.state_at(coord2) != CLEAN:
        self.log(f"There is already something at {coord2}!")
        return STOP
    else:
        p = path_to_position(self, coord1)
        if not p:
            self.log(f"There is no path from here to {coord1}")
            return STOP
        p2 = path_from_to_position(self, coord1, coord2)
        if not p2:
            self.log(f"There is no path from here to {coord2}")
            return STOP
        else:
            self.log(f"Completing transfer to {coord2}")
            return [('path', p), 
                    ('actions', [ACTION_SUCK]),
                    ('path', p2),
                    ('actions', [ACTION_UNSUCK, ACTION_STOP])]
        
def intent_move_gold_from(self, coord1, coord2):
    self.log(f"picking up gold at {coord1}")
    if self.worldmodel.state_at(coord1) != GOLD:
        self.log(f"There is no gold at {coord1}!")
        return STOP
    elif self.worldmodel.state_at(coord2) != CLEAN:
        self.log(f"There is already something at {coord2}!")
        return STOP
    else:
        p = path_to_position(self, coord1)
        if not p:
            self.log(f"There is no path from here to {coord1}")
            return STOP
        p2 = path_from_to_position(self, coord1, coord2)
        if not p2:
            self.log(f"There is no path from here to {coord2}")
            return STOP
        else:
            self.log(f"Completing transfer to {coord2}")
            return [('path', p), 
                    ('actions', [ACTION_MINE_GOLD]),
                    ('path', p2),
                    ('actions', [ACTION_UNLOAD_GOLD, ACTION_STOP])]

def intent_move_some_to(self, coord):
    self.log(f"finding dirt to move to {coord}")
    if self.worldmodel.state_at(coord) != CLEAN:
        self.log(f"There is already something at {coord}!")
    p = path_to_any(self, DIRT)
    p2 = path_from_to_position(self, p[-1], coord)# needs to guide from new
    #p2 = path_to_position(self, coord)
    if p == None:
        return [('explore_dirt')]
    elif len(p) == 0:
        self.log('sucking dirt right here')
        return [ # if the dirt is right where we are 
                ('actions', [ACTION_SUCK]),
                ('path', p2),
                ('actions', [ACTION_UNSUCK, ACTION_STOP])]
    else:
        self.log('finding some dirt and moving it')
        return [('path', p), 
                ('actions', [ACTION_SUCK]),
                ('path', p2),
                ('actions', [ACTION_UNSUCK, ACTION_STOP])]


def intent_move_some_gold_to(self, coord):
    self.log(f"finding gold to move to {coord}")
    if self.worldmodel.state_at(coord) != CLEAN:
        self.log(f"There is already something at {coord}!")
    p = path_to_any(self, GOLD)
    p2 = path_from_to_position(self, p[-1], coord)# needs to guide from new
    #p2 = path_to_position(self, coord)
    if p == None:
        return [('explore_gold')]
    elif len(p) == 0:
        self.log('mining gold right here')
        return [ # if the dirt is right where we are 
                ('actions', [ACTION_MINE_GOLD]),
                ('path', p2),
                ('actions', [ACTION_UNLOAD_GOLD, ACTION_STOP])]
    else:
        self.log('finding some gold and moving it')
        return [('path', p), 
                ('actions', [ACTION_MINE_GOLD]),
                ('path', p2),
                ('actions', [ACTION_UNLOAD_GOLD, ACTION_STOP])]      
    
def intent_move_anywhere(self, coord):
    self.log(f"Moving Dirt From {coord} to anywhere")
    if self.worldmodel.state_at(coord) != DIRT:
        self.log(f"There isn't any dirt at {coord}!")
        return [ACTION_STOP]
    p = path_to_position(self, coord)
    p2 = path_to_any(self, CLEAN)
    print('New p2', p2)
    if p2 == []: # helps prevent dropping dirt right back to where it was
        self.log('Changing destination location')
        p2 = path_from_to_position(self, coord, self.worldmodel.current_position)
    if len(p) == 0:
        self.log('sucking dirt right here')
        return [ # if the dirt is right where we are 
                ('actions', [ACTION_SUCK]),
                ('path', p2),
                ('actions', [ACTION_UNSUCK, ACTION_STOP])]
    else:
        self.log('going to dirt and moving it')
        return [('path', p), 
                ('actions', [ACTION_SUCK]),
                ('path', p2),
                ('actions', [ACTION_UNSUCK, ACTION_STOP])]
    
def intent_move_gold_anywhere(self, coord):
    self.log(f"Moving Gold From {coord} to anywhere")
    if self.worldmodel.state_at(coord) != GOLD:
        self.log(f"There isn't any Gold at {coord}!")
        return [ACTION_STOP]
    p = path_to_position(self, coord)
    p2 = path_to_any(self, CLEAN)
    if p2== []: # helps prevent dropping dirt right back to where it was
        self.log(f'Changing destination location, {self.worldmodel.current_position}')
        p2 = path_from_to_position(self, coord, self.worldmodel.current_position)
    if len(p) == 0:
        self.log('mining gold right here')
        return [ # if the dirt is right where we are 
                ('actions', [ACTION_MINE_GOLD]),
                ('path', p2),
                ('actions', [ACTION_UNLOAD_GOLD, ACTION_STOP])]
    else:
        self.log('finding some gold and moving it')
        return [('path', p), 
                ('actions', [ACTION_MINE_GOLD]),
                ('path', p2),
                ('actions', [ACTION_UNLOAD_GOLD, ACTION_STOP])] 

def intent_get_all_gold(self):
    p = path_to_exactly(self, GOLD)
    print('p is now', p)
    full_actions = []
    squares = self.worldmodel.squares_with_state(GOLD)
    while p != None:
        print('p is now', p)
        # path to first gold is p, identify path to second gold
        squares.remove(p[-1]) # removing the already identified gold
        print('all gold squares', squares)
        if squares == []:
            self.log('doing last and exiting')
            pfinal = path_from_to_position(self, p[-1], (1,1))
            full_actions.append(('path', p))
            full_actions.append(('actions', [ACTION_MINE_GOLD]))
            full_actions.append(('path', pfinal))
            return full_actions
        
        p2 = path_from_to_position(self, p[-1], squares[0]) # unfound gold!
        if p2 == []:
            return full_actions
        squares.remove(p2[-1])
        coord = p2[-1]
        p3 = path_from_to_position(self, coord, (1,1))
        # run to two locations and then home
        self.log('all gold is being found, planning first 2')
        full_actions.append(('path', p))
        full_actions.append(('actions', [ACTION_MINE_GOLD]))
        full_actions.append(('path', p2))
        full_actions.append(('actions', [ACTION_MINE_GOLD]))
        full_actions.append(('path', p3))
        full_actions.append(('actions', [ACTION_UNLOAD_GOLD, ACTION_UNLOAD_GOLD]))
        if squares == []:
            return full_actions
        p = path_from_to_position(self, (1,1), squares[0])
        print('The newest path is', p)
        
        #if not p:
        #    self.log("There is no gold available!")
        #    break
    self.log('all actions are ready, running')
    return full_actions


def intent_unknown_dirt(self):
    self.log('looking for some dirt')
    squares = self.worldmodel.squares_with_state(DIRT)
    if len(squares) == 0:
        trigger = 'go'
        while trigger != 'done':
            self.log("There is no Dirt that I know of, beginning search.")
            print('all the mystery', self.worldmodel.squares_with_state(UNKNOWN))
            p = self.worldmodel.squares_with_state(UNKNOWN)
            #if self.worldmodel.state_at(p[0]) == DIRT: # cant know until its gone
            self.log(f'Found somewhere to search{p[-1]}')
            trigger= 'done'
            p2 = path_from_to_position(self, self.worldmodel.current_position, p[-1])
            self.log('There may be dirt here, type suck some dirt again!')
            return [('path', p2)]
            
            #else: # used to update the world model and move on
            #    actual_state = self.world[p[-1]]
            #    self.worldmodel.state_at(p[-1]) = actual_state
                
         
    else:
         self.log(f"There is some Dirt at {squares[0]}")
         p = path_to_position(self, squares[0])
         return[('path', p),
                ('actions', [ACTION_SUCK, ACTION_STOP])]
    
########################################
#   Gold getting (mine, return home, unload)
#     at a known coordinate
#     find and get gold
    
def intent_get_gold_at(self, coord):
    self.log(f"Getting gold at {coord}")
    if self.worldmodel.state_at(coord) != GOLD:
        self.log(f"There is no gold at {coord}!")
        return STOP
    else:
        p = path_to_position(self, coord)
        if not p:
            self.log(f"There is no path from here to {coord}")
            return STOP
        else:
            p2 = path_from_to_position(self, coord, (1,1))
            return [('path', p), 
                    ('actions', [ACTION_MINE_GOLD]),
                    ('path', p2), 
                    ('actions', [ACTION_UNLOAD_GOLD, ACTION_STOP])]
            
def intent_get_some_gold(self):
    p = path_to_exactly(self, GOLD)
    if not p:
        self.log(f"There is no gold available!")
        return STOP
    else:
        return intent_get_gold_at(self, p[-1])

#########################################
#  If all else fails
    
def intent_unknown(self):
    self.log(f"Hmmm ... I don't know what to do about that")
    return STOP

