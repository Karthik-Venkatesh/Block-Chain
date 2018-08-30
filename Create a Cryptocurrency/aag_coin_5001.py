#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 26 10:12:00 2018

@author: karthik
"""

# Importing Libraries
import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4 
from urllib.parse import urlparse

# Building a Block chain

class BlockChain:
    
    def __init__(self):
        self.chain = []
        self.transactions = []
        self.nodes = set()
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
    
    def add_transaction(self, sender, receiver, amount):
        self.transactions.append({
                'sender': sender,
                'receiver': receiver,
                'amount': amount
                })
        previous_block = self.get_prev_block()
        return previous_block['index'] + 1
        
    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
        
    def replace_chain(self):
        networks = self.nodes
        max_length = len(self.chain)
        longest_chain = None
        for node in networks:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain:
            self.chain = longest_chain
            return True
        else:
            return False
            
        
# Mining BlockChain

# Creating a web app

app = Flask(__name__)

# Creating a address for port 5000

node_address = str(uuid4()).replace('-', '')

# Creating block chain

block_chain = BlockChain()

# Mining a new block

@app.route('/mine_block', methods = ['GET'])
def mine_block():
    prevoius_block = block_chain.get_prev_block()
    previous_proof = prevoius_block['proof']
    proof = block_chain.proof_of_work(previous_proof)
    prevoius_hash = block_chain.hash(prevoius_block)
    block_chain.add_transaction(sender = node_address, receiver = 'Somebody 1', amount = 2)
    new_block = block_chain.create_block_chain(proof, prevoius_hash)
    response = {
            'message' : 'Success, Mining completed',
            'index' : new_block['index'],
            'timestamp' : new_block['timestamp'],
            'proof' : new_block['proof'],
            'prev_hash' : new_block['prev_hash'],
            'transactions' : new_block['transactions']
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
    is_valid = block_chain.is_chain_valid(block_chain.chain)
    if is_valid:
        response = { 'message': 'All good, The chain is valid'  }
    else:
        response = { 'message': 'The chain is not valid'  }
    return jsonify(response), 200

@app.route('/add_transaction', methods = ['POST'])
def add_transaction():
    json = request.get_json()
    transaction_keys = ['sender', 'receiver', 'amount']
    if not all (key in json for key in transaction_keys):
        return "Some elemets in transaction are missing", 400
    index = block_chain.add_transaction(sender = json['sender'], receiver = ['receiver'], amount = json['amount'])
    response = {'message': f'this transaction will added to the index{index}'}
    return jsonify(response), 201

@app.route('/connect_node', methods = ['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return 'No nodes found', 400
    for node in nodes:
        block_chain.add_node(address = node)
    response = {
        'message': 'All nodes are connected to block chain',
        'nodes' : list(block_chain.nodes)
    }
    return jsonify(response), 201

@app.route('/replace_chain', methods = ['GET'])
def replace_chain():
    is_chain_replaced = block_chain.replace_chain()
    if is_chain_replaced:
        response = { 
            'message': 'The nodes have different chain.',
            'new_chain': block_chain.chain
            }
    else:
        response = { 
            'message': 'All good, The chain is longest one.',
            'actual_chain': block_chain.chain
            }
    return jsonify(response), 200
# Decentralizing Block Chain

# Running the app
    
app.run(host = '0.0.0.0', port = 5001)