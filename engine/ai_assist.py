# engine/ai_assist.py

from openai import OpenAI
from icecream import ic
import json
import os

class AIAssist:
    def __init__(self, game_manager, world_builder):
        self.game_manager = game_manager
        self.world_builder = world_builder

        # Load API key from engine/secrets.json
        # You can get your API key from https://beta.openai.com/
        secrets_file = os.path.join(os.path.dirname(__file__), 'secrets.json')
        with open(secrets_file, 'r') as file:
            secrets = json.load(file)
        self.api_key = secrets.get('openai_api_key', '')

        self.client = OpenAI(api_key=self.api_key)


    def generate_ai_response(self, prompt, max_tokens=250):
        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "system", "content": prompt}],
                model="gpt-4",  # You may need to change the model based on your requirement
                max_tokens=max_tokens
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            ic(f"Error in AI response generation: {e}")
            return f"I'm having trouble understanding that. {e}"

    def handle_player_command(self, command):
        # Access world data and player sheet
        world_data = self.world_builder.world_data
        player_data = self.game_manager.player_sheet

        # AI prompt can now use world_data and player_data for context
        ai_prompt = self.construct_ai_prompt(command, world_data, player_data)
        ai_response = self.generate_ai_response(ai_prompt)

        # Determine action based on AI response and natural language processing
        action_response = ""
        if "move to" in command or "go to" in command:
            destination = command.split("to", 1)[1].strip()
            action_response = self.world_builder.move_player(destination)
        elif "look" in command or "see" in command:
            action_response = self.world_builder.look_around()
        elif "take" in ai_response:
            item_name = ai_response.split("take")[1].strip()
            action_response = self.world_builder.take_item(item_name)
        elif "examine" in ai_response:
            item_name = ai_response.split("examine")[1].strip()
            action_response = self.world_builder.examine_item(item_name)
        elif "where am i" in ai_response:
            action_response = self.world_builder.where_am_i()
        elif "open" in ai_response:
            container_name = ai_response.split("open")[1].strip()
            action_response = self.world_builder.open_container(container_name)
        elif "close" in ai_response:
            action_response = self.world_builder.close_container()
        elif "give" in ai_response:
            item_info = ai_response.split("give")[1].strip()
            action_response = self.world_builder.give_item(item_info)
        elif "help" in ai_response:
            action_response = self.world_builder.display_help()
        else:
            action_response = ai_response

        # Generate AI response based on the action taken
        return self.generate_ai_response_after_action(command, action_response, world_data, player_data)
        
    def construct_ai_prompt(self, command, world_data, player_data):
        # Constructing a narrative based on current game state and player command
        location_name = player_data.location.get("location/sublocation", "Unknown Location")
        location_data = self.world_builder.find_location_data(location_name)

        # Describing the current location
        location_description = f"You are in {location_name}, {location_data['description']}."

        # Listing items in the current location
        items_description = "Items here: " + ", ".join([item['name'] for item in location_data.get('items', [])])

        # Describing player's inventory
        inventory_description = "Your inventory: " + ", ".join([f"{item['name']} (x{item['quantity']})" for item in player_data.inventory])

        # Constructing the final prompt for AI
        ai_prompt = (
            f"As the game narrator, describe the scene and actions in response to the player's command.\n\n"
            f"Current scene: {location_description} {items_description}\n"
            f"Player's Inventory: {inventory_description}\n"
            f"Player's Command: '{command}'\n\n"
            "Narrator's Response:"
        )

        return ai_prompt
    
    def generate_ai_response_after_action(self, command, action_response, world_data, player_data):
        # Constructing a narrative based on current game state and player command
        location_name = player_data.location.get("location/sublocation", "Unknown Location")
        location_data = self.world_builder.find_location_data(location_name)

        # Describing the current location
        location_description = f"You are in {location_name}, {location_data['description']}."

        # Listing items in the current location
        items_description = "Items here: " + ", ".join([item['name'] for item in location_data.get('items', [])])

        # Describing player's inventory
        inventory_description = "Your inventory: " + ", ".join([f"{item['name']} (x{item['quantity']})" for item in player_data.inventory])

        # Constructing the final prompt for AI
        ai_prompt = (
            f"As the game narrator, describe the scene and actions in response to the player's command.\n\n"
            f"Current scene: {location_description} {items_description}\n"
            f"Player's Inventory: {inventory_description}\n"
            f"Player's Command: '{command}'\n"
            f"Action Response: '{action_response}'\n\n"
            "Narrator's Response:"
        )

        return self.generate_ai_response(ai_prompt)
