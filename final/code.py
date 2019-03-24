import datetime
import hashlib
import json
from flask import Flask,jsonify,request,render_template
from urllib.parse import urlparse
import requests
#------------------------------------------------------------------------------------------------------------------------------------------------------
class Newschain:
    def __init__(self):
        self.chain = []
        self.organisations = []
        self.writers = []
        self.create_block(proof = 1, previous_hash = '0')
        self.nodes = set()

    def create_block(self, proof, previous_hash):
        block = {'index':len(self.chain)+1,
                 'timestamp':str(datetime.datetime.now()),
                 'proof':proof,
                 'previous_hash':previous_hash,
                 'organisations':self.organisations,
                 'writers':self.writers
                 }
        self.organisations = []
        self.writers = []
        self.chain.append(block)
        return block
    
    def get_previous_block(self):
        return self.chain[-1]
    
    def proof(self, previous_proof):
        new_proof = 1
        check = False
        while check is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if(hash_operation[:4] == '0000'):
                check = True
            else:
                new_proof+=1
        return new_proof
    
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if(hash_operation[:4]!='0000'):
                return False
            if block['previous_hash'] != hash_operation:
                return False
            previous_block = block
            block_index+=1
        return True
    
    def add_organisation(self, name, org_license):
        self.organisations.append({'name':name,
                                   'licence':org_license
                                  })
        previous_block = self.get_previous_block()
        return previous_block['index']+1
    
    def add_writer(self, name, writers_license):
        self.writers.append({'name':name,
                             'license':writers_license
                            })
        previous_block = self.get_previous_block()
        return previous_block['index']+1
    
    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
        
    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
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
        return False
#------------------------------------------------------------------------------------------------------------------------------------
class Newshash:
    def __init__(self):
        self.chain = []
        self.data = []
        self.create_block(proof = 1, previous_hash = '0')
        self.nodes = set()
        
    def create_block(self, proof, previous_hash):
        block = {'index':len(self.chain)+1,
                 'timestamp':str(datetime.datetime.now()),
                 'proof':proof,
                 'previous_hash':previous_hash,
                 'data':self.data                 
                 }
        self.data = []
        self.chain.append(block)
        return block
    
    def proof(self, previous_proof):
        new_proof = 1
        check = False
        while check is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if(hash_operation[:4] == '0000'):
                check = True
            else:
                new_proof+=1
        return new_proof
    
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    def get_previous_block(self):
        return self.chain[-1]
    
    def add_data(self, organisation, writer, data):
        hashed_data = self.hash(data)
        self.data.append({'organisation': organisation,
                          'writer': writer,
                          'data' : hashed_data
                         })
        previous_block = self.get_previous_block()
        return previous_block['index']+1
    
    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if(hash_operation[:4]!='0000'):
                return False
            if block['previous_hash'] != hash_operation :
                return False
            previous_block = block
            block_index+=1
        return True
    
    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
    
    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
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
        return False
#------------------------------------------------------------------------------------------------------------------------------------
app = Flask(__name__)
    
newschain = Newschain()
newshash = Newshash()
#-----------------------------------------------------------------------------------------------------------------------------------------
@app.route("/")
def index():
   return render_template('index.html')

@app.route("/i2")
def index2():
   return render_template('index2.html')
   
@app.route("/addorganisation")
def addorganisation():
   return render_template('add_organisation.html')
   
@app.route("/displayblocks")
def displayblocks():
   return render_template('displayblocks.html')

@app.route("/displaydatablocks")
def displaydatablocks():
   return render_template('displaydatablocks.html')

@app.route("/addwriter")
def addwriter():
   return render_template('add_writer.html')

@app.route("/addnews")
def addnews():
   return render_template('add_news.html')

@app.route("/add_newnodes")
def addnewnodes():
   return render_template('add_newnodes.html')
    
@app.route('/mine_block', methods = ['GET'])
def mine_block():
    previous_block = newschain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = newschain.proof(previous_proof)
    previous_hash = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
    block = newschain.create_block(proof,previous_hash)
    response = {'message':'Congratulations, You have mined a block!!!',
                'index':block['index'],
                'timestamp':block['timestamp'],
                'proof':block['proof'],
                'previous_hash':block['previous_hash'],
                'organisations':block['organisations'],
                'writers':block['writers']}
    return jsonify(response) , 200

@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {'chain':newschain.chain,
                'length':len(newschain.chain)}
    return jsonify(response) , 200
        
@app.route('/add_organisation', methods = ['POST'])
def add_organisation():
    #json = request.get_json()
	name = request.form['name']
	license1 = request.form['license']
	#transaction_keys = {'name','license'}
	#if not all (keys in json for keys in transaction_keys):
	#	return 'Some elements of the transaction are missing', 400
	index = newschain.add_organisation(name,license1)
	response = {'message' : f'This transaction will be added to block {index}'}
	return jsonify(response), 201
    
@app.route('/add_writer', methods = ['POST'])
def add_writer():
    #json = request.get_json()
    name = request.form['name']
    license2 = request.form['license']
    #transaction_keys = {'name','license'}
    #if not all (keys in json for keys in transaction_keys):
    #    return 'Some elements of the transaction are missing', 400
    index = newschain.add_writer(name,license2)
    response = {'message' : f'This transaction will be added to block {index}'}
    return jsonify(response), 201

@app.route('/connect_nodes', methods=['POST'])
def connect_nodes():
    #json = request.get_json()
    v1 = request.form['nodes'];
    print(request.form['nodes']);
    #nodes = json.get('nodes')
    if v1 is None:
        return "No Node" , 400
    #for node in nodes:
    newschain.add_node(v1);
    response = {'message':'All nodes are now connected',
                'total_nodes':list(newschain.nodes)}
    return jsonify(response) , 201
    #return('<h1>Okay</h1>');
	
@app.route('/replace_chain', methods=['GET'])
def replace_chain():
    is_chain_replaced = newschain.replace_chain()
    if is_chain_replaced:
        response = {'message':'The nodes had different chains. So the chain was replaced by the longest chain',
                    'new_chain':newschain.chain}
    else:
        response = {'message':'All good. The chain is the largest one.',
                    'actual_chain':newschain.chain}
    return jsonify(response) , 200
#------------------------------------------------------------------------------------------------------------------------------------------------------
@app.route('/mine_block2', methods = ['GET'])
def mine_block2():
    previous_block = newshash.get_previous_block()
    previous_proof = previous_block['proof']
    proof = newshash.proof(previous_proof)
    previous_hash = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest() 
    block = newshash.create_block(proof,previous_hash)
    response = {'message':'Congratulations, You have mined a block!!!',
                'index':block['index'],
                'timestamp':block['timestamp'],
                'proof':block['proof'],
                'previous_hash':block['previous_hash'],
                'data':block['data']}
    return jsonify(response) , 200  

@app.route('/get_chain2', methods=['GET'])
def get_chain2():
    response = {'chain':newshash.chain,
                'length':len(newshash.chain)}
    return jsonify(response) , 200

@app.route('/connect_nodes2', methods=['POST'])
def connect_nodes2():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return "No Node" , 400
    for node in nodes:
        newshash.add_node(node)
    response = {'message':'All nodes are now connected',
                'total_nodes':list(newshash.nodes)}
    return jsonify(response) , 201

@app.route('/add_data2', methods = ['POST'])
def add_data2():
    #json = request.get_json()
    #transaction_keys = {'organisation','writer','data'}
    #if not all (keys in json for keys in transaction_keys):
    #    return 'Some elements of the transaction are missing', 400
    #index = newshash.add_data(json['organisation'], json['writer'], json['data'])
    index = newshash.add_data(request.form['oname'],request.form['wname'],request.form['newsdata'])
    response = {'message' : f'This transaction will be added to block {index}'}
    return jsonify(response), 201

@app.route('/replace_chain2', methods=['GET'])
def replace_chain2():
    is_chain_replaced = newshash.replace_chain()
    if is_chain_replaced:
        response = {'message':'The nodes had different chains. So the chain was replaced by the longest chain',
                    'new_chain':newshash.chain}
    else:
        response = {'message':'All good. The chain is the largest one.',
                    'actual_chain':newshash.chain}
    return jsonify(response) , 200
#------------------------------------------------------------------------------------------------------------------------------------------------------
app.run(host = '0.0.0.0', port = 5000)
