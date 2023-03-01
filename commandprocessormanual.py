from agents.agentworldmodel import GOLD, DIRT 

from agents.intents import intent_agent_info, intent_find_dirt, intent_find_gold, intent_find_stuff
from agents.intents import intent_move_dirt_from, intent_move_gold_from, intent_move_some_to
from agents.intents import intent_move_some_gold_to, intent_move_anywhere, intent_move_gold_anywhere, intent_get_all_gold
from agents.intents import intent_praise, intent_unknown_dirt
from agents.intents import intent_turn, intent_forward_backward, intent_goto, intent_go_home
from agents.intents import intent_suck_dirt_at, intent_suck_some_dirt, intent_get_gold_at, intent_get_some_gold
from agents.intents import intent_unknown

from agents.coord import to_coord, is_coord
import string

####################
            
def preprocess(cmd): 
    cmd = ''.join(ch for ch in cmd if ch not in set(string.punctuation))
    return [w.lower() for w  in cmd.split()] 

####################
    
class CommandProcessor:    
    def __init__(self, agent, worldmodel, log):
        self.agent = agent
        self.worldmodel = worldmodel
        self.log = log
        # Any word in the command not in this dictionary
        # will be ignored.  Multiple words put in the same
        # category ( e.g. fetch, bring, get) are considered
        # synonymous in terms of predicting the intent
        
        self.term_categories = {'forward': 'move_direction',
                                'backward': 'move_direction',
                                'around': 'turn_direction',
                                'left': 'turn_direction',
                                'right': 'turn_direction',
                                'around': 'turn_direction',
                                'bring': 'bring',
                                'fetch': 'bring',
                                'get': 'bring',
                                'find': 'find',
                                'gold': 'gold',
                                'dirt': 'dirt',
                                'home': 'home',
                                'where': 'where',
                                'how': 'how',
                                'you': 'you',
                                'turn': 'turn',
                                'suck': 'suck',
                                'mine': 'mine',
                                'go': 'move',
                                'move': 'move',
                                'unload': 'unload',
                                'search': 'search',
                                'what': 'search',
                                'some': 'some',
                                'any':'some',
                                'anywhere':'anywhere',
                                'somewhere':'anywhere',
                                'all': 'all',
                                'every': 'all',
                                'good': 'praise',
                                'well': 'praise',
                                'thank': 'praise',
                                'thanks': 'praise'}
                           
    def interpret_command(self, cmd):
        term_presence = {}   
        for word in cmd.split():
            if is_coord(word):
                if len(term_presence) <1:
                    term_presence['coord'] = to_coord(word)
                else:
                    term_presence['coord2'] = to_coord(word) # allows for 2 coord move
            
            if word.isdigit():
                term_presence['number'] = int(word) 
        print('new dict', term_presence)
                
        # Preprocessing the command breaks it into words, and also 
        # removes non-letters.  It is severe preprocessing!
        # After this loop, all information about the command is in
        # the term_categories dictionary
        
        for term in preprocess(cmd):
            if term in self.term_categories:
                term_presence[self.term_categories[term]] = term
     
        # The intent_* functions translate parameters into "command sequences" that
        # can be executed by the agent
        
        command_sequence = None  
        if 'number' in term_presence and 'move_direction' in term_presence:
            command_sequence =  intent_forward_backward(self, term_presence['move_direction'], term_presence['number'])
        elif 'turn' in term_presence and 'turn_direction' in term_presence:
            command_sequence =  intent_turn(self, term_presence['turn_direction'])
        elif 'suck' in term_presence and 'coord' in term_presence:
            command_sequence =  intent_suck_dirt_at(self, term_presence['coord'])
            print('specific suck', command_sequence)
        elif 'suck' in term_presence and not 'some' in term_presence:
            self.log('using old method')
            print('using old method') 
            command_sequence = intent_suck_some_dirt(self)
        elif 'home' in term_presence:
            command_sequence =  intent_go_home(self)
        elif 'bring' in term_presence and 'gold' in term_presence and 'coord' in term_presence and not 'all' in term_presence:
            command_sequence =  intent_get_gold_at(self, term_presence['coord'])
        elif 'bring' in term_presence and 'gold' in term_presence and not 'all' in term_presence:
            self.log('just grabing gold')
            command_sequence =  intent_get_some_gold(self)
            
        elif 'move' in term_presence and 'coord' and not 'coord2' in term_presence and not 'some' in term_presence and not 'anywhere' in term_presence:
            command_sequence = intent_goto(self, term_presence['coord'])
            print('normal move', command_sequence)
        elif ('where' in term_presence or 'how' in term_presence) and 'you' in term_presence:
            command_sequence = intent_agent_info(self)
        elif ('where' in term_presence or 'find' in term_presence) and ('gold' in term_presence):
            print('Searching for Gold')
            command_sequence = intent_find_gold(self)
        elif ('where' in term_presence or 'find' in term_presence) and ('dirt' in term_presence):
            command_sequence = intent_find_dirt(self)   
        #new command for warm up: This works and runs as anticipated, had to fix line 100
        # in agentworldmodel.py to say dirts not dirt.
        elif 'search' in term_presence and 'coord' in term_presence:
            print('Searching')
            command_sequence = intent_find_stuff(self, term_presence['coord'])
        # Move dirt from one location to another
        elif 'move' in term_presence and 'dirt' in term_presence and 'coord2' in term_presence:
            print('Dirt Transfer', term_presence)
            command_sequence =  intent_move_dirt_from(self, term_presence['coord'], term_presence['coord2'])
            print(command_sequence)
        # Move some dirt to a location from anywhere
        elif 'move' in term_presence and 'dirt' in term_presence and 'some' in term_presence:
            print('Dirt Transfer', term_presence)
            command_sequence =  intent_move_some_to(self, term_presence['coord'])
            print(command_sequence)        
        # Move dirt at locaiton to anywhere empty
        elif 'move' in term_presence and 'dirt' in term_presence and 'anywhere' in term_presence:
            print('Dirt Transfer to anywhere', term_presence)
            command_sequence =  intent_move_anywhere(self, term_presence['coord'])
            print(command_sequence) 
            
        # Move gold from one location to another
        elif 'move' in term_presence and 'gold' in term_presence and 'coord2' in term_presence:
            print('Gold Transfer', term_presence)
            command_sequence =  intent_move_gold_from(self, term_presence['coord'], term_presence['coord2'])
            print('The new command sequence is:', command_sequence)
        # Move gold to a location from anywhere
        elif 'move' in term_presence and 'gold' in term_presence and 'some' in term_presence:
            print('gold Transfer', term_presence)
            command_sequence =  intent_move_some_gold_to(self, term_presence['coord'])
            print(command_sequence)        
        # Move gold at locaiton to anywhere empty
        elif 'move' in term_presence and 'anywhere' in term_presence and 'gold' in term_presence:
            print('Gold Transfer to anywhere', term_presence)
            command_sequence =  intent_move_gold_anywhere(self, term_presence['coord'])
            print(command_sequence)         
        # all above are running as expected.
        
        #. "Sucky, get me all the gold" 
        elif 'all' in term_presence and 'gold' in term_presence:
            print('Gathering all gold', term_presence)
            command_sequence =  intent_get_all_gold(self)
            print(command_sequence)  
            #MINING GOLD TWO AT A TIME, AS GUIDED IN THE PROJECT SPEC
        # THIS WORKS AS EXPECTED, UNLOADS TWO AT A TIME, BUT MAY RUN OUT OF BATTERY
        # BEFORE TASK IS COMPLETED FOR MORE THAN 8 GOLD
        
        # look in recon for dirt, if there is none, it should explore and probe,
        # then suck dirt and stop
        elif 'suck' in term_presence and 'some' in term_presence and 'dirt' in term_presence:
            self.log('So you want some dirt?')
            command_sequence = intent_unknown_dirt(self)
        
        # respond to praise, "good job", "well done" responds, "Thanks, happy to help"
        elif 'praise' in term_presence:
            command_sequence = intent_praise(self)
        
        
        else: 
            command_sequence =  intent_unknown(self)
        return command_sequence
 
