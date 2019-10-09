import hashlib
import requests
import json

import sys


def proof_of_work(last_block):
    block_string = json.dumps(last_block, sort_keys=True)
    proof = 0
    while valid_proof(block_string, proof) is False:
        proof += 1
    return proof


def valid_proof(block_string, proof):
    guess = f'{block_string}{proof}'.encode()
    guess_hash = hashlib.sha256(guess).hexdigest()

    return guess_hash[:6] == '000000'


if __name__ == '__main__':
    if len(sys.argv) > 1:
        node = sys.argv[1]
    else:
        node = "http://localhost:5000"

    coins_mined = 0

    while True:
        last_block = requests.get(node + '/last-block').json()['last_block']
        print('last_block: ', last_block)

        new_proof = proof_of_work(last_block)
        print('proof: ', new_proof)

        mined = requests.post(node + '/mine', json={"proof": new_proof})

        if mined.json()['message'] == 'New Block Forged':
            coins_mined += 1
        print('coins mined: ', coins_mined)
