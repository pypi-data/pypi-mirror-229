from typing import Any, Dict
from ibm_ray_config.modules.gen2.ssh_key import SshKeyConfig

class RaySshKeyConfig(SshKeyConfig):
    
    def __init__(self, base_config: Dict[str, Any]) -> None:
        super().__init__(base_config)

        if self.base_config.get('available_node_types'):
            for available_node_type in self.base_config['available_node_types']:
                self.defaults['key_id'] = self.base_config['available_node_types'][available_node_type]['node_config'].get('key_id')
                break
        # collects default value for the question regrading ssh_private_key location 
        self.defaults['ssh_key_filename'] = self.base_config['auth']['ssh_private_key']

    def update_config(self, ssh_key_id, ssh_key_path, ssh_user):
        self.base_config['auth']['ssh_private_key'] = ssh_key_path
        self.base_config['auth']['ssh_user'] = ssh_user

        if self.base_config.get('available_node_types'):
            for available_node_type in self.base_config['available_node_types']:
                self.base_config['available_node_types'][available_node_type]['node_config']['key_id'] = ssh_key_id
        else:
            self.base_config['available_node_types'] = {self.DEFAULT_NODE_TYPE: {'node_config': {'key_id': ssh_key_id}}}
