import sys
import grpc
import os
import config
import base.climate_pb2_grpc as climate_grpc

HOMECONTROL_ROOT_ENV = 'HOMECONTROL'


def agent_sample_setup():
    root_directory = os.getenv(HOMECONTROL_ROOT_ENV)
    if not os.path.isdir(root_directory):
        print('Unable to resolve homecontrol root directory from environment variables. Use launch.sh to run agent');
        sys.exit(1)

    agent_config_file = os.path.join(root_directory, 'agent/conf/agent.conf')
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


def print_usage():
    print('Usage: agent.py home-control-root\n   home-control-root\t/path/to/homecontrol')


if __name__ == '__main__':
    agent_sample_setup()
