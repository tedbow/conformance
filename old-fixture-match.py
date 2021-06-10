# this is just temp script to test matching old fixtures
# 'old_fixtures' is just temp
import filecmp

fixtures = [
    #['TUFTestFixtureSimple', 'simple'], # Matching?
    #['TUFTestFixtureThresholdTwo', 'threshold_two']
    # ['TUFTestFixtureAttackRollback', 'rollback']
    ['TUFTestFixtureThresholdTwoAttack', 'threshold_two_attack']
]

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

for fixture in fixtures:
    old_name = fixture[0]
    new_name = fixture[1]
    print(f"{bcolors.HEADER}********* Compare {old_name} to {new_name} **********{bcolors.ENDC}")
    old_dir = "old_fixtures/" + old_name
    new_dir = "fixtures/" + new_name
    old_client = old_dir + "/tufclient/tufrepo"
    new_client = new_dir + "/client"
    # print("old_client=" + old_client)
    result = filecmp.dircmp(old_client, new_client)
    result.report_full_closure()
    old_server = old_dir + "/tufrepo"
    new_server = new_dir + "/server"
    result = filecmp.dircmp(old_server, new_server)
    result.report_full_closure()
