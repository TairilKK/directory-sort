extensions = ['log', 'pdf', 'docs']

for extension in extensions:
    for i in range(10):
        with open(f'test_dir\\file_{i}.{extension}', 'w') as f:
            pass