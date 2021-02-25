import subprocess #calls the ./derive script from python
import json
from dotenv import load_dotenv
import os
from web3 import Web3
from bit import *
from eth_account import Account
import pprint
from bit.network import NetworkAPI
from bit import wif_to_key

from constants import *

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

#load EV
load_dotenv()

#get the mnemonic .env
mnemonic = os.getenv('mnemonic')



def derive_wallets(mnemonic, coin, numderive):

    command = 'php derive -g --mnemonic="'+str(mnemonic)+'" --numderive='+str(numderive)+' --coin='+str(coin)+' --format=jsonpretty' 
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    return json.loads(output)


coins = {'eth':derive_wallets(mnemonic=mnemonic,coin=ETH,numderive=3),'btc-test': derive_wallets(mnemonic=mnemonic,coin=BTCTEST,numderive=3)}
pprint.pprint(coins)

eth_privatekey = coins['eth'][0]['privkey']
btc_privatekey = coins['btc-test'][0]['privkey']

    
def priv_key_to_account(coin, priv_key):
    if coin == ETH:
        return Account.privateKeyToAccount(priv_key)
    if coin == BTCTEST:
        return PrivateKeyTestnet(priv_key)
    
eth_account = priv_key_to_account(ETH,eth_privatekey)
btc_account = priv_key_to_account(BTCTEST,btc_privatekey)

def create_tx(coin,account,recipient,amount):
    if coin ==ETH:
        gasEstimate = w3.eth.estimateGas(
            {"from": account.address, "to": recipient, "value": amount}
        )
        return {
            "to": recipient,
            "from": account.address,
            "value": amount,
            "gasPrice": w3.eth.gasPrice,
            "gas": gasEstimate,
            "nonce": w3.eth.getTransactionCount(account.address)
        }
        
    if coin == BTCTEST:
        return PrivateKeyTestnet.prepare_transaction(account.address, [(recipient, amount, BTC)])  

def send_tx(coin, account, recipient, amount):
    if coin =='ETH':
        trxns_eth = create_tx(coin,account, recipient, amount)
        sign_trxns_eth = account.sign_transaction(trxns_eth)
        result = w3.eth.sendRawTransaction(sign_trxns_eth.rawTransaction)
        print(result.hex())
        return result.hex()
    else:
        trxns_btctest = create_tx(coin,account,recipient,amount)
        sign_trxns_btctest = account.sign_transaction(trxns_btctest)
        tx_hex = NetworkAPI.broadcast_tx_testnet(sign_trxns_btctest)
        return tx_hex

coin = BTCTEST
priv_key = eth_privatekey
account = eth_account
recipient = coins['eth'][1]['address']
amount = 0.0001

# print(account.get_unspents())

send_tx(ETH, account, '0x3eF30d4578763e11998F3a1dC5080bC46ffac714', 0.0001)

def main():
    account = priv_key_to_account(coin, priv_key)
    # createTx = create_tx(coin,account,recipient,amount)
    sendTx = send_tx(coin, account, recipient, amount)
    return

# main()