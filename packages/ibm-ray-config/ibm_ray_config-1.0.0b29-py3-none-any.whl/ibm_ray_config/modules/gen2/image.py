from ibm_ray_config.modules.config_builder import ConfigBuilder, update_decorator, spinner
from typing import Any, Dict
from ibm_ray_config.modules.utils import Color, color_msg, find_obj, find_default


class ImageConfig(ConfigBuilder):
    
    def __init__(self, base_config: Dict[str, Any]) -> None:
        super().__init__(base_config)

    @spinner
    def get_image_objects(self):
        """returns a list of images with amd architecture, sorted by name.  

        uses a paginator to collect images beyond page limit amount.
        """
        images = []
        res = self.ibm_vpc_client.list_images().get_result()
        filtered_res  = filter_images_ubuntu_amd(res['images'])
        images.extend(filtered_res)
        while res.get('next',None):
            link_to_next = res['next']['href'].split('start=')[1].split('&limit')[0]
            res = self.ibm_vpc_client.list_images(start=link_to_next).get_result()
            filtered_res  = filter_images_ubuntu_amd(res['images'])
            images.extend(filtered_res)
        
        return sorted(images,key = lambda img:img['name'])

    @update_decorator
    def run(self) -> Dict[str, Any]:

        image_objects = self.get_image_objects()

        default = find_default({'name': 'ibm-ubuntu-22-04-'}, image_objects, name='name', substring=True)
        image_obj = find_obj(image_objects, 'Please choose an image. Ubuntu image is advised as node setup is using apt.', default=default)
        
        if 'ubuntu' not in image_obj['name']: 
            print(color_msg("Node setup commands are suited to Ubuntu.\nAlter the cluster config setup commands.",Color.RED))

        return image_obj['id'], image_obj['minimum_provisioned_size'], image_obj['owner_type'] == 'user'

    @update_decorator
    def verify(self, base_config):
        image_id = self.defaults['image_id']
        image_objects = self.ibm_vpc_client.list_images().get_result()['images']
        if image_id:
            image_obj = find_obj(image_objects, 'dummy', obj_id=image_id)
        else:
            # find first occurrence
            image_obj = next((obj for obj in image_objects if 'ibm-ubuntu-22-04-' in obj['name']), None)
            
        return image_obj['id'], image_obj['minimum_provisioned_size'], image_obj['owner_type'] == 'user'

    @update_decorator
    def create_default(self):
        image_objects = self.ibm_vpc_client.list_images().get_result()['images']

        image_obj = next((image for image in image_objects if 'ibm-ubuntu-22-04-' in image['name']), None)
        
        print(f'Selected \033[92mUbuntu\033[0m 22.04 VM image, {image_obj["name"]}')
        return image_obj['id'], image_obj['minimum_provisioned_size'], image_obj['owner_type'] == 'user'

def filter_images_ubuntu_amd(images):
    """returns Ubuntu images with amd architecture  
    
    images (dict): image objects 
    """
    return [image for image in images if 'amd' in 
            image['operating_system']['architecture']
            and 'ubuntu' in image['operating_system']['name']]