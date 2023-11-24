#https://www.digitalocean.com/community/tutorials/how-to-use-argparse-to-write-command-line-programs-in-python

import argparse


tank_to_fish = {
    "tank_a": "shark, tuna, herring",
    "tank_b": "cod, flounder",
}

parser = argparse.ArgumentParser(description="List fish in aquarium.")
parser.add_argument("tank", type=str)
args = parser.parse_args()

fish = tank_to_fish.get(args.tank, "")
print(fish)
