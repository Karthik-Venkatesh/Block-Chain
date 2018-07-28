#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 28 12:17:12 2018

@author: karthik
"""

# Importing Libraries
import datetime
import hashlib
import json
from flask import Flask, jsonify 

# Building a Block chain

class BlockChain:
    
    def __init__(self):
        self.chain = []
        self.create_block_chain(proof = 1, prev_hash = '0')
    
    def create_block_chain(self, proof, prev_hash):
        block = {
                'index' : len(self.chain),
                'timestamp' : str(datetime.datetime.now()),
                'proof' : proof,
                'prev_hash' : prev_hash
                }
        self.chain.append(block)
        return block
    
    def get_prev_block(self):
        return self.chain[-1]        
    
    def proof_of_work(self, prev_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - prev_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof
    
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    def is_chain_valid(self, chain):
        prev_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block["prev_hash"] != prev_block.hash():
                return False
            proof = block["proof"]
            prev_proof = prev_block["proof"]
            hash_operation = hashlib.sha256(str(proof**2 - prev_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            prev_block = block
            block_index += 1
        return True
        
# Mining BlockChain

# Creating a web app

app = Flask(__name__)

# Creating block chain

block_chain = BlockChain()

# Mining a new block

@app.route('/mine_block', methods = ['GET'])
def mine_block():
    prevoius_block = block_chain.get_prev_block()
    previous_proof = prevoius_block['proof']
    proof = block_chain.proof_of_work(previous_proof)
    prevoius_hash = block_chain.hash(prevoius_block)
    new_block = block_chain.create_block_chain(proof, prevoius_hash)
    response = {
            'message' : 'Success, Mining completed',
            'index' : new_block['index'],
            'timestamp' : new_block['timestamp'],
            'proof' : new_block['proof'],
            'prev_hash' : new_block['prev_hash']
            }
    print(response)
    return jsonify(response), 200

@app.route('/get_chain', methods = ['GET'])
def get_chain():
    response = {
            'chain' : block_chain.chain,
            'length' : len(block_chain.chain) 
            }
    return jsonify(response), 200
    
@app.route('/is_chain_valid', methods = ['GET'])
def is_chain_valid():
    response = {
            'is_chain_valid' : block_chain.is_chain_valid(block_chain.chain)
            }
    return jsonify(response), 200

# Running the app
    
app.run(host = '0.0.0.0', port = 5000)