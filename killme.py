# Sample list of dictionaries
data_list = [
    {
        "1. Ticket Title": "Agile Work Environment Integration",
        "- Description": "Investigate and implement features to align the solution with Telstra's agile work environment, such as support for different types of agile meetings and ceremonies.",
        "- Assignee": "Steven Yuen",
        "- Acceptance Criteria": "The solution should provide features that are tailored to agile work practices and support different types of agile meetings. It should integrate seamlessly with Telstra's existing agile tools and workflows.",
        "- Duration Estimate": "2 days",
        "- Priority": "High",
        "- User-story": "As a project manager, I want a central dashboard to integrate all agile meetings and provide a consistent timeline so that I can easily track and manage all project activities."
    },
    {
        "42. Ticket Title": "Another Ticket",
        "- Description": "Description of another ticket.",
        "- Assignee": "John Doe",
        "- Acceptance Criteria": "Acceptance criteria for another ticket.",
        "- Duration Estimate": "3 days",
        "- Priority": "Low",
        "- User-story": "As a user, I want something else."
    }
]

# Function to rename keys in a dictionary
def rename_keys(dictionary, key_mapping):
    new_dict = {}
    for key, value in dictionary.items():
        for old_key, new_name in key_mapping.items():
            if key.endswith(old_key):
                new_key = new_name
                new_dict[new_key] = value
    return new_dict

# Define key mapping for renaming
key_mapping = {
    "Ticket Title": "title",
    "Description": "description",
    "Assignee": "assignee",
    "Acceptance Criteria": "acceptanceCriteria",
    "Duration Estimate": "estimate",
    "Priority": "priority",
    "User-story": "userStory"
}

# Rename keys in each dictionary in the list
result = [rename_keys(data, key_mapping) for data in data_list]

# Print the result
for item in result:
    print(item)
