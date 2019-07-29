from __future__ import print_function
import argparse
import sys
import subprocess
import time
from datetime import datetime

def processArguments():
    parser = argparse.ArgumentParser(description = 'A Python wrapper to the Veracode Java API jar providing "break the build" functionality', 
                                     epilog = 'Any additional arguments will be passed through to the API jar.', allow_abbrev = False)
    parser.add_argument('-o', '--operation', type = str, help = 'API operating to execute. Options = UploadAndScan, CreateAndSubmitDynamicRescan', default = 'UploadAndScan')
    parser.add_argument('-a', '--apiWrapperPath', type = str, help = 'File path to Veracode API Java wrapper', default = './vosp-api-wrappers-java-19.6.5.8.jar')
    parser.add_argument('-v', '--veracodeId', type = str, help = 'Veracode API credentials ID')
    parser.add_argument('-s', '--veracodeSecret', type = str, help = 'Veracode API credentials secret')
    parser.add_argument('-m', '--monitor', action = "store_true", help = 'Monitor the process until the policy compliance status has been determined.')
    parser.add_argument('-wi', '--checkInterval', type = int, default = 60, help = 'Time interval in seconds between scan policy status checks, default = 60s')
    parser.add_argument('-wm', '--maximumWait', type = int, default = 3600, help = 'Maximum time in seconds to wait for scan to complete, default = 3600s')
    args, unparsed = parser.parse_known_args()
    return args, unparsed

class VeracodeAPI():
    def __init__(self, veracodeId, veracodeSecret, apiWrapperPath):
        self.veracodeId = veracodeId
        self.veracodeSecret = veracodeSecret
        self.apiWrapperPath = apiWrapperPath
        self.baseCommand = ['java', '-jar', self.apiWrapperPath, '-vid', self.veracodeId, '-vkey', self.veracodeSecret]

    def log(self, linesToLog: str):
        exLinesToLog = "{0} - {1}".format(datetime.now().strftime('[%y.%m.%d %H:%M:%S]'), linesToLog)
        print(exLinesToLog, flush = True)

    def processOutput(self, outputTextToProcess: str, startsWith: str, endsWith: str) -> str:
        end_of_leader = s.index(leader) + len(leader)
        start_of_trailer = s.index(trailer, end_of_leader)
        return s[end_of_leader:start_of_trailer]

    def runCommand(self, operation: str, extraArgs: list):
        commandToRun = self.baseCommand + ['-action', operation] + extraArgs
        self.log('Running command: ' + ' '.join(['java', '-jar', self.apiWrapperPath, '-vid', self.veracodeId[:6] + '...', '-vkey', '*****', '-action', operation] + extraArgs))
        commandExecution = subprocess.run(commandToRun, stdout = subprocess.PIPE, stderr = subprocess.STDOUT, bufsize = 0)
        self.log(commandExecution.stdout.decode())
        if commandExecution.returncode == 0:
            try:
                appId = processOutput(commandExecution.stdout.decode(), 'appid=', ')')
                buildId = processOutput(commandExecution.stdout.decode(), 'The build_id of the new build is "', '"')
                return appId, buildId
            except ValueError as e:
                self.log(e)
                sys.exit(1)          
        else:
            sys.exit(commandExecution.returncode)
        return

    def checkStatus(self, appId: str, buildId: str, checkInterval: int, maximumWait: int):
        commandToRun = self.baseCommand + ['-action', 'GetBuildInfo', '-appid', appId, '-buildid', buildId]
        totalTime = 0
        while totalTime <= maximumWait:
            time.sleep(checkInterval)
            commandExecution = subprocess.run(commandToRun, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
            self.log('Checking scan status [' + str(totalTime // checkInterval) + '/' + str(maximumWait // checkInterval) + ']')
            if 'results_ready="true"' in commandExecution.stdout.decode():
                while True:
                    buildStatus = processOutput(commandExecution.stdout.decode(), 'policy_compliance_status="', '"')
                    if buildStatus not in ['Calculating...', 'Not Assessed']:
                        log('Scan complete, policy compliance status: ' + buildStatus)
                        if buildStatus in ['Conditional Pass', 'Pass']:
                            return 'Pass'
                        else:
                            return 'Fail'
                    else:
                        time.sleep(checkInterval)
                        commandExecution = subprocess.run(commandToRun, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
                        log('Scan complete, checking policy status')
            else:
                totalTime = totalTime + checkInterval
        self.log('Scan did not complete within maximum wait time.')
        return 'Time exceeded'

args, unparsed = processArguments()

if args.veracodeId and args.veracodeSecret and args.apiWrapperPath:
    vcApi = VeracodeAPI(args.veracodeId, args.veracodeSecret, args.apiWrapperPath)
    appId, buildId = vcApi.runCommand(args.operation, args.unparsed)
    if args.monitor and appId and buildId and args.checkInterval and args.maximumWait:
        buildStatus = vcApi.checkStatus(appId, buildId, args.checkInterval, args.maximumWait)
        print(buildStatus)
else:
    print('One or more required arguments not provided')
