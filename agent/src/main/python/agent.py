import sys
import grpc
import os
import config
import base.climate_pb2_grpc as climate_grpc

homecontrol_root = os.getenv('HOMECONTROL')
agent_config_file = os.path.join(homecontrol_root, 'agent/conf/agent.conf')
agent_config = config.read_config(agent_config_file)
base_host_address = agent_config.get(config.BASE_SERVER, 'address')
base_host_grpc_port = agent_config.get(config.BASE_SERVER, 'grpc_port')

channel = grpc.insecure_channel(base_host_address + ':' + base_host_grpc_port)
print('grpc channel initialized using address: %s and port %s' % (base_host_address, base_host_grpc_port))

stub = climate_grpc.ClimateStatsStub(channel)
try:
    stub.ReportTemperature(None)
except grpc.RpcError as e:
    print('report temperature rpc failed due to error %s' % e)
