from typing import Any, Dict
from ibm_ray_config.modules.gen2.image import ImageConfig

class RayImageConfig(ImageConfig):
    
    def __init__(self, base_config: Dict[str, Any]) -> None:
        super().__init__(base_config)
        
        if self.base_config.get('available_node_types'):
            for available_node_type in self.base_config['available_node_types']:
                self.defaults['image_id'] = self.base_config['available_node_types'][available_node_type]['node_config'].get('image_id')
                break
    
    def update_config(self, image_id, minimum_provisioned_size, custom_image):
        #minimum_provisioned_size will be used once non default image used
        if self.base_config.get('available_node_types'):
            for available_node_type in self.base_config['available_node_types']:
                self.base_config['available_node_types'][available_node_type]['node_config']['image_id'] = image_id
                self.base_config['available_node_types'][available_node_type]['node_config']['boot_volume_capacity'] = minimum_provisioned_size
        else:
            self.base_config['available_node_types'][self.DEFAULT_NODE_TYPE]['node_config']['image_id'] = image_id
            self.base_config['available_node_types'][self.DEFAULT_NODE_TYPE]['node_config']['boot_volume_capacity'] = minimum_provisioned_size
