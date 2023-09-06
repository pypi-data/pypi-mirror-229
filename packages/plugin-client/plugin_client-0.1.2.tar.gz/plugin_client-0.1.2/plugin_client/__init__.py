import asyncio
import json
import uuid
import websockets
import requests
import json

from .FunctionManager import FunctionManager



functions = []
api_key = None
host = "154.49.137.166"
port = 8005
use_common_plugin = True

class PluginMessage:
    global use_common_plugin
    def __init__(self, node_id):
        self.node_id = node_id
        
    def get_register_msg(self):
        message =  {
            "action": "register",
            "node_id": self.node_id,
            "function_arr": FunctionManager(functions=functions).generate_functions_array(), # 本地插件
            "use_common_plugin": use_common_plugin   # 是否使用系统自带插件
        }
        return json.dumps(message)
        
    def get_function_response(self, response):
        message =  {
            "action": "function_response",
            "node_id": self.node_id,
            "function_response": response
        }
        return json.dumps(message)
    
    


class PluginClient:
    async def client(self, api_key, host="154.49.137.166", port=8005):
        node_id = api_key
        msg = PluginMessage(node_id)
        uri = f"ws://{host}:{port}/ws/{node_id}"
        function_manager = FunctionManager(functions=functions, auto_remove=True)
        while True:
            try:
                async with websockets.connect(uri) as websocket:
                    # print(msg.get_register_msg())
                    await websocket.send(msg.get_register_msg())
                    while True:
                        message = await websocket.recv()
                        message = json.loads(message)
                        # print(message)
                        if message['action'] == 'function':
                            args = json.loads(message['args'])
                            function_name = message['function_name']
                            task = asyncio.create_task(function_manager.call_function(function_name=function_name, args_dict=args))
                            # 这里可以添加其他非阻塞代码
                            response = await task  # 获取结果
                            send_message = msg.get_function_response(response)
                            # send_message = msg.get_function_response("response")
                            # print(send_message)
                            if websocket.open:
                                try:
                                    await websocket.send(send_message)
                                except Exception as e:
                                    print(f"Error while sending: {e}")
                            else:
                                print("WebSocket is not open.")
                        elif message['action'] == "upload":
                            function_manager.download_file(file_location=message['file_location'])
                        elif message['action'] == 'register_response':
                            print(f"Register successful.Your endpoint is {message['endpoint']}")
                        else:
                            await websocket.send(msg.get_function_response(message))
                            
            except Exception as e:
                print(f"An error occurred: {e}")
                await asyncio.sleep(5)  # Wait for 5 seconds before attempting to reconnect

def start():
    global api_key
    if api_key is None:
        raise ValueError("API key must be set before starting.")
    pc = PluginClient()
    asyncio.get_event_loop().run_until_complete(pc.client(api_key, host, port))