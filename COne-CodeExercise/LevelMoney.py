#python script to connect COne API 
import http.client
import urllib.parse

import json
import datetime
import sys

# Global variables to store URI's and email/password for calling APIs

#authentication
#login_id = "1110590645"
#login_password = "0F3D83C5DDBE77986F8162E31A26ED24"
#api_token = "AppTokenForInterview"

login_id = "interview@levelmoney.com"
login_password = "password2"
api_token = "AppTokenForInterview"

base_url = "2016.api.levelmoney.com"
api_url = "/api/v2/core/login"
get_all_transactions_url = "/api/v2/core/get-all-transactions"

ignore_donuts = '--ignore-donuts' in sys.argv
#ignore_ccpayments = '--ignore-ccpayments'


def callApi(url, args):
	headers = {"Content-type": "application/json", "Accept": "application/json"}
	conn = http.client.HTTPSConnection(base_url)	
	conn.request("POST", url, json.dumps(args), headers)
	response = conn.getresponse()
	print(response.status)
	print(response.reason)
	#response_body = json.loads(response.read().decode("utf-8"))
	response_body = json.load(response)
	return response_body

def calculateAverage(result):
	totalSpent = 0
	totalIncome = 0
	count = 0

	for entry in result:
		count+= 1
		totalSpent += result[entry]['spent']
		totalIncome += result[entry]['income']


	averageSpent = totalSpent / count
	averageIncome = totalIncome / count

	value = {'spent': averageSpent, 'income': averageIncome}
	return value

def calculateCCpayment(result):

        totalSpent = 0
        totalIncome = 0
        count = 0

        for entry in result:
                count+= 1
                totalSpent += result[entry]['spent']
                totalIncome += result[entry]['income']

        ccSpent = totalSpent
        ccIncome = totalIncome

        value = {'spent' : ccSpent, 'income': ccIncome}
        return value
    
def writeHeaderLine(col1, col2, col3):
	output_file.write('{0:12s}   {1:16s}  {2:16s}'.format(col1, col2, col3))
	output_file.write('\n')    

def writeFormatedLine(col1, col2, col3):
	output_file.write('{0:7s}     ${1:12.2f}     ${2:12.2f}'.format(col1, col2, abs(col3)))
	output_file.write('\n')

def getTransaction(result, transaction_line, ignore_donuts):
        
        if ignore_donuts and transaction_line['merchant'] in {'Krispy Kreme Donuts', 'DUNKIN #336784'}:
            return
        
        amount = transaction_line['amount']
        date = datetime.datetime.strptime(transaction_line['transaction-time'], "%Y-%m-%dT%H:%M:%S.000Z").date()
        key = str(date.year) + "-" + str(date.month)
        if key in result:
                if amount > 0:
                        tempAmount = result[key]['income'] + amount
                        result[key]['income'] = tempAmount
                else:
                        tempAmount = result[key]['spent'] + amount
                        result[key]['spent'] = tempAmount
        else:
                value = {}
                if amount > 0:
                        value['spent'] = 0
                        value['income'] = amount
                else:
                        value['spent'] = 0
                        value['income'] = amount
                result[key] = value
        return

#make API calls
#login_id = input("Username: ")
#login_password = input("Password: ")
#api_token = input("API Token: " )

login_response = callApi(api_url, {"email":  login_id, "password":  login_password, "args": {'api-token': api_token}})
print(login_response)
get_all_transactions_response = callApi(get_all_transactions_url, {'args': {'uid': login_response['uid'], 'token': login_response['token'], 'api-token': api_token}})


# For successful API call, response code will be 200 (OK)
#if login_response['error']:

#    #Open destination file
output_file = open("LevelMoney.txt", "w")
#    #Parse response
transactions = get_all_transactions_response['transactions']
result = {}

#    #Parse income/expendatures from transactions into aggregate result
for transaction in transactions:
    getTransaction(result, transaction, ignore_donuts)

    #Write aggregate result to file
writeHeaderLine('Date', 'Income', 'Spent')
for entry in sorted(result):
    writeFormatedLine(entry, result[entry]['income'], result[entry]['spent'] )


average = calculateAverage(result)
output_file.write('\n')
output_file.write('\n')
writeHeaderLine(' ', 'Income', 'Spent')
writeFormatedLine('Average', average['income'], average['spent'])
output_file.close()

#else:

    # If response code is not ok (200), print the resulting http error code with description
#    print(login_response['error'])

