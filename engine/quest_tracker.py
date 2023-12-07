# engine/quest_tracker.py

import json
from icecream import ic
from interfaces import IGameManager, IQuestTracker, IPlayerSheet
from utilities import normalize_name

class QuestTracker(IQuestTracker):
    def __init__(self):
        self.game_manager = None  # To be set later

        ic("Initializing quest tracker")
        
        self.initial_quests = self.load_initial_quests()

    def set_game_manager(self, game_manager: IGameManager):
        if game_manager is None:
            raise ValueError("GameManager cannot be None")
        self.game_manager = game_manager

    def set_player_sheet(self, player_sheet: IPlayerSheet):
        self.player_sheet = player_sheet

    def load_initial_quests(self):
        try:
            with open('data/quests.json', 'r') as f:
                return json.load(f)
        except Exception as e:
            ic(f"Error loading quests: {e}")
            return []

    def initialize_for_new_game(self):
        # Initialize or reset quests for a new game
        self.initial_quests = self.load_initial_quests() 
        ic("Quest tracker initialized for a new game.")

    def get_quest(self, quest_name):
        return next((quest for quest in self.initial_quests if quest['name'] == quest_name), None)


    def activate_quest(self, quest_name):
        if not self.player_sheet:
            ic("Player sheet not set in QuestTracker")
            return
        else:
            quest_data = self.get_quest(quest_name)
            if quest_data and not quest_data.get('completed', False):
                quest_data['isActive'] = True
                self.player_sheet.add_quest(quest_data)  # Assuming add_quest is a method in PlayerSheet
                ic(f"Quest {quest_name} activated") 

    def initialize_quest(self, quest_slug, quest_data):
        quest_class = self.quest_class_for_slug(quest_slug)
        if quest_class:
            return quest_class(self.game_manager, quest_data)
        else:
            raise ValueError(f"No quest class found for slug: {quest_slug}")

    def quest_class_for_slug(self, quest_slug):
        quest_classes = {
            'initialQuest': initialQuest,
            'echoesOfAvalonia': echoesOfAvalonia,  # Make sure this matches the slug in your JSON
            'the-hidden-knowledge': TheHiddenKnowledge,
            'royal-decrees': RoyalDecrees,
            'guardian-of-the-realms': GuardianOfTheRealms
        }
        return quest_classes.get(quest_slug)

    def check_all_quests(self):
        ic("Checking all quests")
        if self.game_manager is None:
            raise RuntimeError("GameManager is not set in QuestTracker")
        for quest_data in self.player_sheet.quests:
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
                        quest_data['completed'] = True
                        self.player_sheet.update_quest(quest_data)
                        ic(f"Quest {quest_data['name']} marked completed in player sheet")


    # def check_npc_quests(self, npc_name):
    #     ic("Checking quests related to NPC:", npc_name)
    #     for quest_data in self.player_sheet.quests:
    #         # Check only active and not yet completed quests
    #         if quest_data['isActive'] and not quest_data['completed']:
    #             ic("Checking quest:", quest_data['name'])
    #             quest_class = self.quest_class_for_slug(quest_data['slug'])
    #             if quest_class:
    #                 # Initialize the quest object from its class
    #                 quest_object = quest_class(self.game_manager, quest_data)
    #                 ic(quest_object)
    #                 # Check if any objectives are related to speaking to the specified NPC
    #                 for obj in quest_object.objectives:
    #                     if isinstance(obj, SpeakToCharacterObjective) and obj.objective_data['target'] == npc_name:
    #                         ic(f"Quest {quest_data['name']} has a SpeakToCharacterObjective for {npc_name}")
    #                         objectives_completed = quest_object.check_objectives()
    #                         if objectives_completed:
    #                             # Mark the quest as completed
    #                             quest_data['completed'] = True
    #                             self.player_sheet.update_quest(quest_data)
    #                             ic(f"Quest {quest_data['name']} marked completed in player sheet")


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

# Objective for reading email(s)
class ReadEmailObjective(BaseObjective):
    def check_objective(self):
        # Handle the case where all items should be checked
        if self.objective_data['target'] == "all-unread":
            return self.check_all_emails_read()

        # Handle the case where specific items are listed
        elif isinstance(self.objective_data['target'], list):
            return all(self.check_specific_email_read(email_name) for email_name in self.objective_data['target'])

        # Handle the case where there is only one target
        else:
            return self.check_specific_email_read(self.objective_data['target'])

    def check_all_emails_read(self):
        emails = self.game_manager.player_sheet.get_all_emails()
        if all(email.get('read', False) for email in emails):
            self.complete()
            return True
        return False

    def check_specific_email_read(self, email_name):
        email = self.game_manager.player_sheet.get_email(email_name)
        if email and email.get('read', False):
            return True
        return False

class SpeakToCharacterObjective(BaseObjective):
    def check_objective(self):
        ic("Checking speak to character objective")
        # Normalize the target NPC name and last spoken NPC name
        target = self.objective_data['target']
        ic(f'Objective data: {target}')
        last_spoken_npc = self.game_manager.world_builder.last_spoken_npc
        ic(f'Last spoken NPC: {last_spoken_npc}')
        target_npc_name = normalize_name(self.objective_data['target'])
        last_spoken_npc = normalize_name(self.game_manager.world_builder.last_spoken_npc)
        
        ic(f'Normalized Target NPC name: {target_npc_name}')
        ic(f'Normalized Last spoken NPC: {last_spoken_npc}')
        
        if last_spoken_npc == target_npc_name:
            ic("Objective met, completing objective")
            self.complete()
            return True
        ic("Objective not met")
        return False


class DefeatEnemyObjective(BaseObjective):
    def check_objective(self):
        enemy_name = self.objective_data['target']
        defeated_enemies = self.game_manager.combat_manager.get_defeated_enemies()
        if enemy_name in defeated_enemies:
            self.complete()
            return True
        return False
    
class CollectObjective(BaseObjective):
    def check_objective(self):
        target_type = self.objective_data.get('targetType', 'item')  # Assuming 'item' as default

        if target_type == 'item':
            return self.check_item_collected()
        elif target_type == 'resource':
            return self.check_resource_collected()
        else:
            ic(f"Unknown target type: {target_type}")
            return False

    def check_item_collected(self):
        item = self.game_manager.player_sheet.get_inventory_item_details(self.objective_data['target'])
        ic(item)
        if item:
            self.complete()
            return True
        return False

    def check_resource_collected(self):
        resource_name = self.objective_data['target']
        required_amount = self.objective_data.get('amount', 1)  # Assuming 1 as default if not specified
        current_amount = self.game_manager.resource_manager.get_resource_amount(resource_name)
        if current_amount >= required_amount:
            self.complete()
            return True
        return False
    
# BaseQuest handles multiple objectives
class BaseQuest:
    def __init__(self, game_manager, quest_data):
        self.game_manager = game_manager
        self.quest_data = quest_data
        ic(self.quest_data)
        self.objectives = [self._create_objective(obj_data) for obj_data in quest_data['objectives']]
        ic(self.objectives)

    def _create_objective(self, objective_data):
        objective_type = objective_data['type']
        if objective_type == 'readEmail':
            return ReadEmailObjective(self.game_manager, objective_data)
        elif objective_type == 'speakToCharacter':
            return SpeakToCharacterObjective(self.game_manager, objective_data)
        elif objective_type == 'defeatEnemy':
            return DefeatEnemyObjective(self.game_manager, objective_data)
        elif objective_type == 'collect':
            return CollectObjective(self.game_manager, objective_data)
        else:
            raise ValueError(f"Unknown objective type: {objective_type}")
        
    def check_objectives(self):
        all_objectives_completed = all(obj.check_objective() for obj in self.objectives)
        ic(f"All objectives completed for quest '{self.quest_data['name']}': {all_objectives_completed}")
        if all_objectives_completed:
            self.complete()  
            return True
        return False

    def complete(self):
        ic(f"Completing quest: {self.quest_data['name']}")
        self.quest_data['completed'] = True
        self.distribute_rewards()
        ic(f"Quest completed: {self.quest_data}")

    def distribute_rewards(self):
        rewards = self.quest_data.get('rewards', {})
        if 'items' in rewards:
            for item in rewards['items']:
                self.game_manager.player_sheet.add_item(item)
        if 'experience' in rewards:
            self.game_manager.player_sheet.add_experience(rewards['experience'])
        if 'tokens' in rewards:
            self.game_manager.player_sheet.add_tokens(rewards['tokens'])
        ic(f"Rewards distributed for quest: {self.quest_data['name']}")
            
## Individual quests go here

# The initialQuest class would be a specific instance of BaseQuest
class initialQuest(BaseQuest):
    def __init__(self, game_manager, quest_data):
        # Pass the quest_data to the superclass constructor
        super().__init__(game_manager, quest_data)

    def check_objectives(self):
        # The inherited check_objectives method from BaseQuest will be used
        return super().check_objectives()
    
# Echoes of Avalonia quest class
class echoesOfAvalonia(BaseQuest):
    def __init__(self, game_manager, quest_data):
        super().__init__(game_manager, quest_data)

    def check_objectives(self):
        return super().check_objectives()

# The Hidden Knowledge quest class
class TheHiddenKnowledge(BaseQuest):
    def __init__(self, game_manager, quest_data):
        super().__init__(game_manager, quest_data)

    def check_objectives(self):
        return super().check_objectives()

# Royal Decrees quest class
class RoyalDecrees(BaseQuest):
    def __init__(self, game_manager, quest_data):
        super().__init__(game_manager, quest_data)

    def check_objectives(self):
        return super().check_objectives()

# Guardian of the Realms quest class
class GuardianOfTheRealms(BaseQuest):
    def __init__(self, game_manager, quest_data):
        super().__init__(game_manager, quest_data)

    def check_objectives(self):
        return super().check_objectives()