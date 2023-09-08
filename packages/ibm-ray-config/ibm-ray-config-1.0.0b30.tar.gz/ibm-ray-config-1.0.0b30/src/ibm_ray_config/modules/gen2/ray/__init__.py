from ibm_ray_config.modules.gen2.ray.api_key import RayApiKeyConfig
from ibm_ray_config.modules.gen2.ray.endpoint import RayEndpointConfig
from ibm_ray_config.modules.gen2.ray.floating_ip import FloatingIpConfig
from ibm_ray_config.modules.gen2.ray.image import RayImageConfig
from ibm_ray_config.modules.gen2.ray.ssh_key import RaySshKeyConfig
from ibm_ray_config.modules.gen2.ray.vpc import RayVPCConfig
from ibm_ray_config.modules.gen2.ray.workers import WorkersConfig
from ibm_ray_config.modules.config_builder import ConfigBuilder

MODULES = [RayApiKeyConfig, RayEndpointConfig, RayVPCConfig,
           RaySshKeyConfig, RayImageConfig, FloatingIpConfig, WorkersConfig]

from ibm_ray_config.main import load_base_config

def load_config(backend, iam_api_key, region=None,
                    image_id=None, profile_name='bx2-2x8',
                    key_id=None, ssh_key_filename=None,
                    vpc_id=None, min_workers=0, max_workers=0):
    
    base_config = load_base_config(backend)
    head_node_data = base_config['available_node_types'][ConfigBuilder.DEFAULT_NODE_TYPE]
    
    base_config['provider']['iam_api_key'] = iam_api_key
    head_node_data['node_config']['vpc_id'] = vpc_id
    head_node_data['node_config']['image_id'] = image_id
    head_node_data['node_config']['instance_profile_name'] = profile_name
    head_node_data['node_config']['key_id'] = key_id
    base_config['auth']['ssh_private_key'] = ssh_key_filename
    
    base_config['provider']['region'] = region
    base_config['provider']['endpoint'] = f'https://{region}.iaas.cloud.ibm.com'

    base_config['max_workers'] = max_workers
    head_node_data['min_workers'] = min_workers
    head_node_data['max_workers'] = max_workers
    
    return base_config

def parse_config(config):
    res = {'iam_api_key': config['provider']['iam_api_key']}    
    
    for available_node_type in config['available_node_types']:
        res['vpc_id'] = config['available_node_types'][available_node_type]['node_config']['vpc_id']
        res['key_id'] = config['available_node_types'][available_node_type]['node_config']['key_id']     
        res['subnet_id'] = config['available_node_types'][available_node_type]['node_config']['subnet_id']
    
    res['endpoint'] = config['provider']['endpoint']

    if 'iam_endpoint' in config['provider']:
        res['iam_endpoint'] = config['provider']['iam_endpoint']
        
    return res
    