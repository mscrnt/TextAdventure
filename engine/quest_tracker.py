import json
from icecream import ic

class QuestTracker:
    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.active_quests = {}
        ic(self.load_quests())
        ic(f"Active quests after loading: {self.active_quests}")

    def load_quests(self):
        with open('data/quests.json', 'r') as f:
            self.quests = json.load(f)
        ic(self.quests)
        for quest in self.quests:
            if quest['isActive']:
                ic(f"Loading active quest: {quest['name']}")
                self.game_manager.player_sheet.add_quest(quest)
                self.initialize_quest(quest['slug'], quest)

    def get_quest(self, quest_name):
        quest = next((quest for quest in self.quests if quest['name'] == quest_name), None)
        ic(quest)
        return quest

    def activate_quest(self, quest_name):
        quest_data = self.get_quest(quest_name)
        if quest_data and not quest_data['completed']:
            quest_data['isActive'] = True
            self.save_quests()
            quest_object = self.initialize_quest(quest_name, quest_data)
            if quest_object:
                self.active_quests[quest_name] = quest_object
                quest_object.activate()

    def initialize_quest(self, quest_slug, quest_data):
        ic(f"Initializing quest: {quest_slug} with data: {quest_data}")
        
        quest_class = self.quest_class_for_slug(quest_slug)
        if quest_class:
            quest = quest_class(self.game_manager, quest_data)
            ic(f"Quest object created: {quest}")
            
            # Add the created quest object to the active_quests dictionary
            self.active_quests[quest_data['name']] = quest
            ic(f"Active quests updated: {self.active_quests}")

            return quest
        else:
            raise ValueError(f"No quest class found for slug: {quest_slug}")

    def quest_class_for_slug(self, quest_slug):
        quest_classes = {
            'initialQuest': initialQuest,
            # Add other mappings as needed
        }
        return quest_classes.get(quest_slug)

    def complete_quest(self, quest_name):
        quest_object = self.active_quests.get(quest_name)
        if quest_object:
            quest_object.complete()
            self.save_quests()

    def check_all_quests(self):
        ic("Checking all quests")
        for quest_name, quest_object in self.active_quests.items():
            ic(quest_name)
            ic(quest_object)
            if quest_object.check_objectives():
                self.complete_quest(quest_name)
                self.game_manager.player_sheet.complete_quest(quest_name, self)
                self.active_quests.pop(quest_name)
                return True
        return False
    

    def update_quest_data(self, updated_quest):
        for index, quest in enumerate(self.quests):
            if quest['name'] == updated_quest['name']:
                self.quests[index] = updated_quest
                break
        self.save_quests()

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
        objectives_complete = all(obj.check_objective() for obj in self.objectives)
        ic(objectives_complete)
        return objectives_complete

    def complete(self):
        if all(obj.completed for obj in self.objectives):
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
    
