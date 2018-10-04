import yaml

data = {
    "ghosts": [
        "inky",
        "pinky",
        "blinky",
        "sue",
    ]
}

yaml_str = yaml.dump(data)

assert yaml.load(yaml_str) == data
