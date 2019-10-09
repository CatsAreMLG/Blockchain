import hashlib
import json
from time import time
from uuid import uuid4

from flask import Flask, jsonify, request


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.nodes = set()
        self.new_block(previous_hash=1, proof=100)

    def new_block(self, proof, previous_hash=None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        self.current_transactions = []
        self.chain.append(block)

        return block

    def new_transaction(self, sender, recipient, amount):
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })

        return self.last_block['index'] + 1

    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()

        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def valid_proof(block_string, proof):
        guess = f'{block_string}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()

        return guess_hash[:6] == '000000'

    def valid_chain(self, chain):
        prev_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]

            print(f'{prev_block}')
            print(f'{block}')
            print("\n-------------------\n")

            if self.hash(prev_block) != block['previous_hash']:
                return False

            block_string = json.dumps(prev_block, sort_keys=True)

            if not self.valid_proof(block_string, block['proof']):
                return False

            prev_block = block
            current_index += 1

        return True


app = Flask(__name__)

node_identifier = str(uuid4()).replace('-', '')

blockchain = Blockchain()


@app.route('/mine', methods=['POST'])
def mine():
    # proof = blockchain.proof_of_work()
    values = request.get_json()
    required = ['proof']

    if not all(k in values for k in required):
        return 'Missing Values', 400

    last_block = blockchain.last_block
    last_block_string = json.dumps(last_block, sort_keys=True)

    if not blockchain.valid_proof(last_block_string, values['proof']):
        response = {
            'message': 'Proof was invalid or submitted too late'
        }
        return jsonify(response, 500)

    blockchain.new_transaction(sender='0', recipient=node_identifier, amount=1)

    previous_hash = blockchain.hash(blockchain.last_block)
    block = blockchain.new_block(values['proof'], previous_hash)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }

    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing Values', 400

    index = blockchain.new_transaction(values['sender'],
                                       values['recipient'],
                                       values['amount'])

    response = {'message': f'Transaction will be added to Block {index}'}

    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }

    return jsonify(response), 200


@app.route('/last-block', methods=['GET'])
def last_block():
    response = {
        'last_block': blockchain.last_block
    }

    return jsonify(response), 200


@app.route('/valid-chain', methods=['GET'])
def valid_chain():
    response = {
        'valid-chain': blockchain.valid_chain(blockchain.chain)
    }

    return jsonify(response), 200


# Run the program on port 5000
if __name__ == '__main__':
    app.run(host='localhost', port=5000)
