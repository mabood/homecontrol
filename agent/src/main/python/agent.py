import sys
import grpc
import os
import config
import base.climate_pb2_grpc as climate_grpc


def agent_sample_setup(root_directory):
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
    if len(sys.argv) != 2:
        print_usage()
        sys.exit(1)

    home_control_root = sys.argv[1]
    if not os.path.isdir(home_control_root):
        print('Invalid home-control-root: %s\n' % home_control_root)
        print_usage()
        sys.exit(2)

    agent_sample_setup(home_control_root)
