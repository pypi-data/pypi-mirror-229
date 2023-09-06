from . import netbox
import argparse

def main():
    parser = argparse.ArgumentParser(description="Keep kalm and automate netbox", usage="kalm_netbox <action> \n\n \
               \
               version : 0.0.2 (netbox)\n\
               actions:\n\
               netboxdata                dump netbox data in json \n\
               ssh_config                dump ssh_config\n\
               ansible_inventory         dump ansible inventory\n\
               create_manufacturer       create manufacturer\n\
               create_site               create site\n\
               create_device_type        create device type\n\
               add_vm                    add_vm to netbox\n\
               refresh                   refresh core netbox content\n\
               sites                     list sites\n\
               \
               2023 Knowit Miracle\
               ")
    parser.add_argument('action', metavar='<action>', type=str, nargs='+', help='setup jenkis')
    args = parser.parse_args()
    ready = False
    if args.action[0] == "refresh":
        netbox.refresh()
        return 0
    if args.action[0] == "create_cluster":
        netbox.create_cluster(args)
        return 0
    if args.action[0] == "create_tenant_group":
        netbox.create_tenant_group(args)
        return 0
    
    if args.action[0] == "create_tenant":
        netbox.create_tenant(args)
        return 0
    
    if args.action[0] == "create_device_type":
        netbox.create_device_type(args)
        return 0
    
    if args.action[0] == "create_site":
        netbox.create_site(args)
        return 0
    
    if args.action[0] == "create_manufacturer":
        netbox.create_manufacturer(args)
        return 0
    
    if args.action[0] == "ansible_inventory":
        netbox.ansible_inventory(args)
        return 0
    
    if args.action[0] == "ssh_config":
        netbox.sshconfig(args)
        return 0
    
    if args.action[0] == "netboxdata":
        netbox.netboxdata(args)
        return 0
    
    if args.action[0] == "vizualize":
        netbox.vizulize(args)
        return     
    
    if args.action[0] == "sites":
        print(netbox.get_sites())
        return 0
    
    if args.action[0] == "tenants":
        print(netbox.get_tenants())
        return 0
    
    
    if args.action[0] == "add_vm":
        return netbox.add_vm()    
    return 0

    

    







