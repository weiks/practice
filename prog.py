import argparse
parser = argparse.ArgumentParser()
parser.add_argument("instrument", help="instrustment book")
parser.add_argument("book", help="instrument book")
args = parser.parse_args()
print args.instrument, args.book
