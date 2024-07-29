import os

def find_env_files(start_path):
    env_files = []
    for root, dirs, files in os.walk(start_path):
        for file in files:
            if file.startswith('.env'):
                env_files.append(os.path.join(root, file))
    return env_files

project_path = '/Users/alimac/claude-engineer'
env_files = find_env_files(project_path)

if env_files:
    print("Found the following .env files:")
    for file in env_files:
        print(file)
else:
    print("No .env files found in the project directory.")

# Also check if .env.local exists in the root directory
root_env_local = os.path.join(project_path, '.env.local')
if os.path.exists(root_env_local):
    print(f"\n.env.local exists in the root directory: {root_env_local}")
else:
    print("\n.env.local does not exist in the root directory.")