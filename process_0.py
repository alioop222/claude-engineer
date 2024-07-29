import os

root_dir = '/Users/alimac/claude-engineer'
hidden_files = [f for f in os.listdir(root_dir) if f.startswith('.')]
print("Hidden files in root directory:")
for file in hidden_files:
    print(file)

print("\nChecking src directory:")
src_dir = os.path.join(root_dir, 'src')
hidden_files_src = [f for f in os.listdir(src_dir) if f.startswith('.')]
print("Hidden files in src directory:")
for file in hidden_files_src:
    print(file)