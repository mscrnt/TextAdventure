import json
from icecream import ic

class QuestTracker:
    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.initial_quests = self.load_initial_quests()

    def load_initial_quests(self):
        try:
            with open('data/quests.json', 'r') as f:
                return json.load(f)
        except Exception as e:
            ic(f"Error loading quests: {e}")
            return []

    def get_quest(self, quest_name):
        return next((quest for quest in self.initial_quests if quest['name'] == quest_name), None)

    def activate_quest(self, quest_name):
        quest_data = self.get_quest(quest_name)
        if quest_data and not quest_data['completed']:
            quest_data['isActive'] = True  # Make sure to set the quest as active
            self.game_manager.player_sheet.add_quest(quest_data)  # Add the active quest to the player's sheet
            ic(f"Quest {quest_name} activated")  # Debug output to confirm activation


    def initialize_quest(self, quest_slug, quest_data):
        quest_class = self.quest_class_for_slug(quest_slug)
        if quest_class:
            return quest_class(self.game_manager, quest_data)
        else:
            raise ValueError(f"No quest class found for slug: {quest_slug}")

    def quest_class_for_slug(self, quest_slug):
        quest_classes = {
            'initialQuest': initialQuest,
            # Other mappings...
        }
        return quest_classes.get(quest_slug)

    def check_all_quests(self):
        ic("Checking all quests")
        ic(self.game_manager.player_sheet.quests)
        for quest_data in self.game_manager.player_sheet.quests:
            ic(f"Quest data before check: {quest_data}")
            if not quest_data['completed'] and quest_data['isActive']:
                ic("Checking quest")
                ic(quest_data)
                quest_class = self.quest_class_for_slug(quest_data['slug'])
                ic(quest_class)
                if quest_class:
                    ic("Checking objectives for quest:", quest_data['name'])
                    quest_object = quest_class(self.game_manager, quest_data)
                    ic(quest_object)
                    objectives_completed = quest_object.check_objectives()
                    ic(f"Objectives completed for quest {quest_data['name']}:", objectives_completed)
                    if objectives_completed:
                        ic(f"Marking quest {quest_data['name']} as completed")
                        quest_data['completed'] = True
                        self.game_manager.player_sheet.update_quest(quest_data)
                        ic(f"Quest {quest_data['name']} marked completed in player sheet")


    def save_quests(self):
        with open('data/quests.json', 'w') as f:
            json.dump(self.quests, f, indent=4)
    
# Base class for all objectives
class BaseObjective:
    def __init__(self, game_manager, objective_data):
        self.game_manager = game_manager
        self.objective_data = objective_data
        self.completed = objective_data.get('completed', False)
        ic(self.objective_data)

    def check_objectives(self):
        for objective in self.objectives:
            if not objective.check_objective():
                return False
        return True

    def complete(self):
        ic(f"Completing objective: {self.objective_data}")
        self.completed = True
        self.objective_data['completed'] = True
        # Ensure that the objective's completion is reflected in the quest data
        #self.game_manager.player_sheet.update_quest(self.objective_data)
        

# Objective for reading an email
class ReadEmailObjective(BaseObjective):
    def check_objective(self):
        ic("Checking ReadEmailObjective")
        email = self.game_manager.player_sheet.get_email(self.objective_data['target'])
        ic(email)  # Check the state of the email
        if email and email['read']:
            ic("Email read, completing objective")
            self.complete()
            return True
        else:
            ic("Email not read")
        return False


# Objective for fetching an item
class FetchItemObjective(BaseObjective):
    def check_objective(self):
        item = self.game_manager.player_sheet.get_inventory_item_details(self.objective_data['target'])
        ic(item)
        if item:
            self.complete()
            return True
        return False


# BaseQuest now handles multiple objectives
class BaseQuest:
    def __init__(self, game_manager, quest_data):
        self.game_manager = game_manager
        self.quest_data = quest_data
        ic(self.quest_data)
        self.objectives = [self._create_objective(obj_data) for obj_data in quest_data['objectives']]
        ic(self.objectives)

    def _create_objective(self, objective_data):
        ic(objective_data)
        if objective_data['type'] == 'readEmail':
            return ReadEmailObjective(self.game_manager, objective_data)
        elif objective_data['type'] == 'fetchQuest':
            return FetchItemObjective(self.game_manager, objective_data)
        else:
            raise ValueError(f"Unknown objective type: {objective_data['type']}")
        
    def check_objectives(self):
        all_objectives_completed = all(obj.check_objective() for obj in self.objectives)
        ic("All objectives completed:", all_objectives_completed)

        if all_objectives_completed:
            self.complete()  # Mark the quest as complete if all objectives are done
            return True

        return False

    def complete(self):
        self.quest_data['completed'] = True
        ic(f"Quest completed: {self.quest_data}")
            
## Individual quests go here

# The initialQuest class would be a specific instance of BaseQuest
class initialQuest(BaseQuest):
    def __init__(self, game_manager, quest_data):
        # Pass the quest_data to the superclass constructor
        super().__init__(game_manager, quest_data)

    def check_objectives(self):
        # The inherited check_objectives method from BaseQuest will be used
        return super().check_objectives()
    