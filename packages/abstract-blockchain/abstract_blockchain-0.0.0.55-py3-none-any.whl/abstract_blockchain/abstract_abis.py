from .abstract_apis import RPCData,Choose_RPC_Parameters_GUI
from abstract_webtools import DynamicRateLimiterManagerSingleton,get_limited_request
from abstract_security.envy_it import get_env_value
import json
request_manager = DynamicRateLimiterManagerSingleton.get_instance()
class ABIBridge:
    def __init__(self,contract_address:str,rpc:dict=None):
        if rpc == None:
            rpc = Choose_RPC_Parameters_GUI()
        self.rpc = RPCData(rpc)
        self.contract_address = self.try_check_sum(contract_address)
        self.abi_url =f"https://api.{self.rpc.scanner}/api?module=contract&action=getabi&address={self.contract_address}&apikey={self.api_keys()}"
        self.request = self.safe_json_loads(self.get_request())
        self.abi = self.get_response()
        self.contract_bridge = self.create_abi_bridge()
        self.contract_functions = self.list_contract_functions()
    def api_keys(self):
        if self.rpc.scanner in ['ftmscan.com','moonbeam.moonscan.io','polygonscan.com','bscscan.com']:
            return get_env_value(key=self.rpc.scanner)
        return get_env_value(key='etherscan.io')
    def get_request(self,request_type:str=None,request_min:int=10,request_max:int=30,limit_epoch:int=60,request_start:int=None,json_data:dict=None):
        request_manager.add_service(request_type,request_min, request_max, limit_epoch,request_start)
        return get_limited_request(request_url=self.abi_url,service_name=request_type)
    def get_response(self):
        return self.safe_json_loads(self.request["result"])
    def try_check_sum(self,address:str):
        try:
            address = self.check_sum(address)
            return address
        except:
            raise ValueError("Invalid Ethereum Address")
    def safe_json_loads(self, abi):
        if isinstance(abi, str):
            return json.loads(abi)
        elif isinstance(abi, (dict, list)):
            return abi
        else:
            raise TypeError("Invalid type for ABI. Must be either str, dict, or list.")
    def check_sum(self,address:str):
        return self.rpc.w3.to_checksum_address(address)
    def create_abi_bridge(self):
        return self.rpc.w3.eth.contract(address=self.contract_address, abi=self.abi)
    def list_contract_functions(self):
        functions = []
        for item in self.abi:
            if item['type'] == 'function':
                function_details = {
                    "name": item['name'],
                    "inputs": [(i['name'], i['type']) for i in item['inputs']],
                    "outputs": [(o['name'], o['type']) for o in item['outputs']]
                }
                functions.append(function_details)
        return functions
    def get_read_only_functions(self,abi:list=None):
        if abi == None:
            abi=self.abi
        read_only_functions = []
        for item in abi:
            if item['type'] == 'function' and (item['stateMutability'] == 'view' or item['stateMutability'] == 'pure'):
                read_only_functions.append(item['name'])
        return read_only_functions
    def get_required_inputs(self,function_name:str,abi:list=None):
        if abi == None:
            abi=self.abi
        for item in self.abi:
            if item['type'] == 'function' and item["name"] == function_name:
                return item["inputs"]
    def call_function(self, function_name, *args, **kwargs):
        """
        Calls a read-only function on the contract.

        :param function_name: Name of the function to call.
        :param args: Positional arguments to pass to the function.
        :param kwargs: Keyword arguments to pass to the function.
        :return: Result of the function call.
        """
        contract_function = getattr(self.contract_bridge.functions, function_name)#(*args, **kwargs)
        if len(args) == 1 and not kwargs:
            return contract_function(args[0]).call()
        else:
            return contract_function(**kwargs).call()
    def create_functions(self, subsinstance, function_name, *args, **kwargs):
        # Access the subsinstance (like "functions" in the contract)
        sub_instance = getattr(self.contract_bridge, subsinstance)  # use self.contract_bridge
            
        # Get the desired function from the subsinstance
        function = getattr(sub_instance, function_name)

        # If there's only one positional argument and no keyword arguments, use it directly.
        # Otherwise, use kwargs as named arguments.
        if len(args) == 1 and not kwargs:
            return function(args[0]).call()
        else:
            return function(**kwargs).call()
def default_rpc():
    return {'Network': 'Mainnet', 'RPC': 'https://mainnet.infura.io/v3/9aa3d95b3bc440fa88ea12eaa4456161', 'Block_Explorer': 'https://etherscan.io', 'ChainID': '0x1', 'Symbol': 'ETH', 'Network_Name': 'Ethereum'}
##EXAMPLE USAGE
#
# abi_manager = ABIBridge(contract_address='0x3dCCeAE634f371E779c894A1cEa43a09C23af8d5',rpc=default_rpc())
# read_only_functions = abi_manager.get_read_only_functions()
# for each in read_only_functions:
#     inputs = abi_manager.get_required_inputs(each)
#     if len(inputs)==0:
#         result = abi_manager.call_function(each)
#         print(each,result)
#     else:
#         print(each,inputs)
##   
