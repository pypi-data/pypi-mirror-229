from parsigs.parse_sig_api import SigParser

# inp = 'TAKE 1 TABLET TWICE A DAY WITH MEALS for 3 weeks'
# inp = "INHALE 2 PUFFS INTO THE LUNGS EVERY"

# inp1 = "Take 10 units of once every day at night"

# inp1 = "Take 50 mcg of eltroxin 5 times a week and then take 100 mcg twice a week"

sig_parser = SigParser()

inp1 = "Take 1-2 tablets (5-10 mg total) by mouth every 4 (four) hours as needed "
inp2 = "take 1 tablet of benadryl"

sig_parser.parse_many([inp1, inp2])
print(sig_parser.parse(inp1))

