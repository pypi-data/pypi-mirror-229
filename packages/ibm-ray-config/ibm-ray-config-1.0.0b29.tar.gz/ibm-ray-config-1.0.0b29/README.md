# Ray VPC allocator / Configuration Generator For IBM VPC

`ibm-ray-config` is a CLI tool that seamlessly allocates and registers VPC resources (such as: subnets, gateways, ips, ssh keys and security groups rules), to generate Ray configuration files and executables for IBM VPC.

## Setup

The tool has been mostly tested with Ubuntu 20.04/22.04 and Fedora 35/37, but should work on most Linux systems.   
Requirements: `ssh-keygen` utility installed:
```
sudo apt install openssh-client
```

Install `ibm-ray-config` from pip repository

```
pip install ibm-ray-config
```

## Usage

### Set up IBM VPC resources and configure a cluster for Ray:

```
ibm-ray-config [--iam-api-key IAM_API_KEY] [--r REGION] [-o OUTPUT_PATH] [--compute-iam-endpoint IAM_ENDPOINT] [--version] 
```

Get a short description of the available flags via ```ibm-ray-config --help```

<br/>

#### Flags Detailed Description

<!--- <img width=125/> is used in the following table to create spacing --->
 |<span style="color:orange">Key|<span style="color:orange">Default|<span style="color:orange">Mandatory|<span style="color:orange">Additional info|
 |---|---|---|---|
 | iam-api-key   | |yes|IBM Cloud API key. To generate a new API Key, adhere to the following [guide](https://www.ibm.com/docs/en/spectrumvirtualizecl/8.1.3?topic=installing-creating-api-key)
 |output-path   |current working directory ($PWD) | no |A custom location for the program's outputs |
 |version       | | no |Returns ibm-ray-config's package version|
 |region| | no|Geographical location for deployment and scope for available resources by the IBM-VPC service. Region are listed <a href="https://cloud.ibm.com/docs/vpc?topic=vpc-creating-a-vpc-in-a-different-region&interface=cli"> here</a>. |
 compute_iam_endpoint|https://iam.cloud.ibm.com|no|Alternative IAM endpoint url for the cloud provider, e.g. https://iam.test.cloud.ibm.com|

### Operate the cluster
To interact with the cluster, execute the scripts in `<cluster_folder>/scripts/`:  
- `up.sh`, `down.sh`, `stop.sh` and `submit.sh` correspond to Ray's counterpart [commands](https://docs.ray.io/en/latest/cluster/cli.html?highlight=cli#ray-monitor).
- `down-vpc.sh`  will delete all resources created by Ray and `ibm-ray-config`  
- `connect.sh` will open a secure connection to your cluster, while `disconnect.sh` will terminate it.
- `ray.sh` can be used to run all other of Ray's [commands](https://docs.ray.io/en/latest/cluster/cli.html?highlight=cli#ray-monitor).
- `tunnel.sh` establish forward additional ports over secure ssh tunnel using, e.g. ray serve ports: `tunnel.sh 8000`. 

Notice - To use Ray commands without the aforementioned scripts, either run them from the cluster's folder, or edit the `ssh_private_key` field to contain the absolute path to the associated ssh private key.

### Using ibm-ray-config Config Tool Programmatically
#### Disclaimer:  
This feature is currently dysfunctional, as it wasn't maintained throughout the previous releases.  
We hope to support it in the near future. 

Attention: though not all fields are mandatory, unspecified resources will be created automatically on the backend.

Mandatory fields are: `iam_api_key` and `region`.
Processor architecture: Intel x86.    

Unspecified Fields will be replaced with the following values:     
- `vpc_id` - If available a random one will be chosen.
         Otherwise (if no VPC exists) a new VPC named:ray-default-vpc-<INT> will be created and a random floating-ip will be assigned to the subnet's gateway. The process may create a new floating-ip if no unbound ip exists. 
- `ssh_key_filename` (path to private ssh-key) - A new one will be created and registered under the specified region. 
- `key_id` (ssh-key on the IBM-VPC platform) - If ssh_key_filename instead specified the public key will be generated and registered, otherwise, a new key will be created and registered.   
- `image_id` - The VMs image will be Ubuntu 20.04.
- `profile_name` - 'bx2-2x8', which equates to: 2CPUs, 8GiB RAM, 100GB storage.
- `min_workers` - 0.
- `max_workers` - 0.

Example:
```
from ibm_ray_config import generate_config

api_key = '<IAM_API_KEY>'
region = 'eu-de'
generate_config(iam_api_key=api_key, region=region, image_id='r010-5a674db7-95aa-45c5-a2f1-a6aa9d7e93ad', key_id='r010-fe6cb103-60e6-46bc-9cb5-14e415990849', ssh_key_filename='/home/kpavel/.ssh/id_rsa', profile_name='bx2-2x8', vpc_id='r010-af1adda4-e4e5-4060-9aa2-7a0c981aff8e', min_workers=1, max_workers=1)
```

Minimal example using mandatory fields:

```
from ibm_ray_config import generate_config

api_key = <IAM_API_KEY>
region = 'eu-de'
config_file = generate_config(iam_api_key=api_key, region=region)
```

### Test and Usage 
Attention: to run multiple clusters under the same VPC, make sure their cluster names (`cluster_name` in the config file) are unique.      

To deploy a Ray cluster with the configuration created, please use the <a href="https://github.com/project-codeflare/ibm-vpc-ray-connector"> ibm-vpc-ray-connector </a>. Follow the instructions via the provided link to test your configuration files.

## Execution Example
![part1](doc-assets/example1.png?raw=true)
![part2](doc-assets/example2.png?raw=true)
