# engine/npc.py

class NPCManager:
    def __init__(self, npc_data, game_ui):
        self.npc_data = npc_data
        self.game_ui = game_ui
        self.current_dialogue_index = 0
        self.conversational_context = {}

    def exit_interaction(self):
        self.game_ui.in_npc_interaction = False
        self.game_ui.current_npc_manager = None
        self.game_ui.display_text("Exited NPC interaction.")
        
    def display_interaction_menu(self):
        print(f"{self.npc_data['name']}: {self.get_current_dialogue()}")
        self.update_dialogue_index()

        options = self.get_interaction_options()
        print("\nOptions:")
        for i, option in enumerate(options, 1):
            print(f"{i}. {option.capitalize()}")

    def get_interaction_options(self):
        options = ["conversation", "give", "take"]
        # Add logic to modify options based on context
        return options

    def get_current_dialogue(self):
        return self.npc_data['interactions'][1]['dialog'][self.current_dialogue_index]

    def update_dialogue_index(self):
        self.current_dialogue_index = (self.current_dialogue_index + 1) % len(self.npc_data['interactions'][1]['dialog'])

    def handle_player_choice(self, choice):
        try:
            choice = int(choice)
            if choice == 1:
                self.handle_conversation()
            elif choice == 2:
                self.handle_give()
            elif choice == 3:
                self.handle_take()
            else:
                print("Invalid choice")
        except ValueError:
            print("Please enter a valid number")

    def handle_conversation(self):
        while True:
            current_dialogue = self.get_current_dialogue()
            print(f"{self.npc_data['name']}: {current_dialogue}")

            # Check if the conversation has options or is a simple message
            if 'options' in current_dialogue:
                for i, option in enumerate(current_dialogue['options'], 1):
                    print(f"{i}. {option['text']}")

                choice = input("Choose an option: ")
                if choice.isdigit() and 1 <= int(choice) <= len(current_dialogue['options']):
                    chosen_option = current_dialogue['options'][int(choice) - 1]
                    # Handle chosen option, might change dialogue index or end conversation
                    if 'end_conversation' in chosen_option and chosen_option['end_conversation']:
                        break
                    elif 'next_dialogue' in chosen_option:
                        self.current_dialogue_index = chosen_option['next_dialogue']
                else:
                    print("Please choose a valid option.")
            else:
                # Simple message, wait for player to acknowledge before moving on
                input("Press Enter to continue...")
                self.update_dialogue_index()

            # Check if the conversation should end after this dialogue
            if 'end_conversation' in current_dialogue and current_dialogue['end_conversation']:
                break

    def handle_give(self):
        # Implement giving logic
        print("Giving an item...")
        # Example: Player gives an item to the NPC
        item_name = input("Enter the name of the item to give: ")
        quantity = input("Enter the quantity: ")
        try:
            quantity = int(quantity)
            details = f"{quantity} {item_name} to {self.npc_data['name']}"
            self.world_builder.handle_give_take('give', details)
        except ValueError:
            print("Invalid quantity. Please enter a number.")

    def handle_take(self):
        # Implement taking logic
        print("Taking an item...")
        # Example: Player takes an item from the NPC
        item_name = input("Enter the name of the item to take: ")
        quantity = input("Enter the quantity: ")
        try:
            quantity = int(quantity)
            details = f"{quantity} {item_name} from {self.npc_data['name']}"
            self.world_builder.handle_give_take('take', details)
        except ValueError:
            print("Invalid quantity. Please enter a number.")