def ticket_splitter(input_string):

    # input_string = "Based on the transcript, here are a few Jira tickets that could be created:\n\n1. Ticket Title: Agile Work Environment Integration\n   - Description: Investigate and implement features to align the solution with Telstra's agile work environment, such as support for different types of agile meetings and ceremonies.\n   - Assignee: Steven Yuen\n   - Priority: High\n\n2. Ticket Title: Contextual Output Generation\n   - Description: Develop functionality to use the transcripts of past meetings as context to generate more accurate and valuable output for future meetings.\n   - Assignee: Steven Yuen\n   - Priority: Medium\n\n3. Ticket Title: Centralized Dashboard\n   - Description: Create a centralized dashboard to manage and track all meetings and their associated artifacts, providing a seamless experience for users.\n   - Assignee: Steven Yuen\n   - Priority: Medium\n\n4. Ticket Title: Copilot Integration and Customization\n   - Description: Explore the possibility of integrating Telstra's solution with Copilot, tailoring it to meet specific business needs and leveraging the existing platform.\n   - Assignee: Jason Hong\n   - Priority: Medium\n\n5. Ticket Title: Meeting Minutes Tailoring\n   - Description: Modify the meeting minutes feature to align with different meeting types, such as retros, stand-ups, and ceremonies, to provide more relevant and useful outputs.\n   - Assignee: Chris Qu\n   - Priority: Low\n\nPlease note that these suggested tickets are based on the information provided in the transcript and may need to be adjusted based on further discussions and requirements."

    # Split the input string into sections based on '\n\n'
    sections = input_string.split('\n\n')

    to_return = []

    # Print each section in the list
    for i in range(1,len(sections)-1):


        # Split the input string into lines
        lines = sections[i].split('\n')

        # Initialize an empty dictionary to store the key-value pairs
        ticket_info = {}

        for line in lines:
            # Split each line into key and value using ':'
            key, value = line.strip().split(': ')
            # Remove leading and trailing spaces from the key and value
            key = key.strip()
            value = value.strip()
            # Add the key-value pair to the dictionary
            ticket_info[key] = value

        to_return.append(ticket_info)

    return to_return

def action_splitter(input_string):

    # print(input_string)

    
    # Split the input string into sections based on '\n\n'
    sections = input_string.split('\n\n')

    # Initialize an empty dictionary to store the action items
    action_items = {}

    for section in sections:
        # Split each section into lines
        lines = section.split('\n')
        
        # The first line contains the team member's name and action item number
        team_member = lines[0]
        
        # Initialize a list to store the action items for the team member
        action_item_list = []
        
        for line in lines[1:]:
            if line.startswith('- '):
                # Extract and add each action item to the list
                action_item_list.append(line.lstrip('- '))
        
        # Add the team member and their action items to the dictionary
        action_items[team_member] = action_item_list

    # Print the resulting dictionary
    # print(action_items)

    return action_items

def retro_splitter(input_string):

    # print(input_string)

    # Split the input string into sections based on '\n\n'
    sections = input_string.split('\n\n')

    # Initialize an empty dictionary to store the action items
    action_items = {}

    for section in sections:
        # Split each section into lines
        lines = section.split('\n')
        
        # The first line contains the action item number and description
        action_item_and_description = lines[0].split('. ', 1)
        
        # Check if there is an action item number and description
        if len(action_item_and_description) == 2:
            action_item, action_description = action_item_and_description
            # Add the action item and description to the dictionary
            action_items[action_item] = action_description

    return action_items

def user_story_splitter(input_string):
    # Split the input string into requirements based on '\n\n'
    requirements = input_string.split('\n\n')

    # Initialize an empty dictionary to store the requirements
    requirements_dict = {}

    # Initialize a counter for requirement numbers
    requirement_number = 1

    for requirement_text in requirements:
        # Add the requirement to the dictionary with a generated number as the key
        requirements_dict[f"{requirement_number}. Requirement"] = requirement_text
        requirement_number += 1

    return requirements_dict

def main():
    action_splitter("Action Items:\n\n1. Steven Yuen:\n- Research and identify features that cater to Agile work environments.\n- Investigate the use of a centralized dashboard for managing meetings.\n- Determine how the solution can differentiate itself from Copilot.\n- Gather requirements and file from the stakeholders.\n\n2. Jason Hong:\n- Continue working on current tasks and projects.\n\n3. David Gailey:\n- Support the shift towards an Agile focus for the solution.\n- Assist in identifying unique features and value proposition compared to Copilot.\n\n4. Chris Qu:\n- Participate in discussions and provide input on the direction of the solution.\n- Assist in determining the necessary features for the Telstra-focused solution.\n\n5. All team members:\n- Collaborate on integrating Copilot into the solution in the long term.\n\n6. Steven Yuen and Jason Hong:\n- Discuss the issue of Copilot access and find a solution.\n\n7. Steven Yuen:\n- Chase up the requirements from the stakeholders.")

if __name__ == '__main__':
    main()