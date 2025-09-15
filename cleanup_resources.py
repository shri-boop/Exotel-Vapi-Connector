#!/usr/bin/env python3
"""
Cleanup Resources Script
========================
Provides DELETE operations for cleaning up Vapi-Exotel integration resources.

This script includes the missing DELETE APIs that were not used in the main setup
but are essential for resource management and cleanup.

Usage:
    python3 cleanup_resources.py --help
    python3 cleanup_resources.py --list-resources
    python3 cleanup_resources.py --cleanup-trunk TRUNK_SID
    python3 cleanup_resources.py --cleanup-vapi-resources
"""

import os
import json
import urllib.request
import base64
import ssl
import argparse
import requests
import urllib3
import sys

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ResourceCleanup:
    """Handles cleanup of Vapi-Exotel integration resources"""
    
    def __init__(self):
        self.load_configuration()
    
    def load_configuration(self):
        """Load configuration from environment variables"""
        self.config = {
            'exotel': {
                'auth_key': os.environ.get('EXO_AUTH_KEY'),
                'auth_token': os.environ.get('EXO_AUTH_TOKEN'),
                'domain': os.environ.get('EXO_SUBSCRIBIX_DOMAIN', 'api.in.exotel.com'),
                'account_sid': os.environ.get('EXO_ACCOUNT_SID'),
            },
            'vapi': {
                'private_key': os.environ.get('VAPI_PRIVATE_KEY'),
                'base_url': 'https://api.vapi.ai'
            }
        }
        
        if self.config['exotel']['domain'] and self.config['exotel']['account_sid']:
            self.config['exotel']['base_url'] = f"https://{self.config['exotel']['domain']}/v2/accounts/{self.config['exotel']['account_sid']}"
    
    def make_exotel_request(self, method, endpoint, payload=None):
        """Make authenticated request to Exotel API v2"""
        url = self.config['exotel']['base_url'] + endpoint
        
        credentials = f"{self.config['exotel']['auth_key']}:{self.config['exotel']['auth_token']}"
        encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
        
        headers = {
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/json'
        }
        
        data = json.dumps(payload).encode('utf-8') if payload else None
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        try:
            with urllib.request.urlopen(req, context=ssl_context) as resp:
                return json.loads(resp.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            error_response = e.read().decode('utf-8')
            print(f"❌ Exotel API Error {e.code}: {error_response}")
            return None
    
    def make_vapi_request(self, method, endpoint, payload=None):
        """Make authenticated request to Vapi API"""
        url = self.config['vapi']['base_url'] + endpoint
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {self.config['vapi']['private_key']}"
        }
        
        if method.upper() == 'DELETE':
            response = requests.delete(url, headers=headers, verify=False)
        elif method.upper() == 'GET':
            response = requests.get(url, headers=headers, verify=False)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
            
        return response
    
    def list_trunk_resources(self, trunk_sid):
        """List all resources associated with a trunk"""
        print(f"📋 Resources for trunk {trunk_sid}:")
        print("=" * 50)
        
        # List destinations
        destinations = self.make_exotel_request('GET', f'/trunks/{trunk_sid}/destination-uris')
        if destinations and destinations.get('response'):
            print("\n🎯 Destinations:")
            for dest_response in destinations['response']:
                if dest_response.get('status') == 'success' and dest_response.get('data'):
                    dest = dest_response['data']
                    print(f"   ID: {dest.get('id')} - {dest.get('destination')}")
        
        # List phone numbers
        phone_numbers = self.make_exotel_request('GET', f'/trunks/{trunk_sid}/phone-numbers')
        if phone_numbers and phone_numbers.get('response'):
            print("\n📞 Phone Numbers:")
            for phone_response in phone_numbers['response']:
                if phone_response.get('status') == 'success' and phone_response.get('data'):
                    phone = phone_response['data']
                    print(f"   ID: {phone.get('id')} - {phone.get('phone_number')}")
        
        # List whitelisted IPs
        whitelisted_ips = self.make_exotel_request('GET', f'/trunks/{trunk_sid}/whitelisted-ips')
        if whitelisted_ips and whitelisted_ips.get('response'):
            print("\n🌐 Whitelisted IPs:")
            for ip_response in whitelisted_ips['response']:
                if ip_response.get('status') == 'success' and ip_response.get('data'):
                    ip_data = ip_response['data']
                    print(f"   ID: {ip_data.get('id')} - {ip_data.get('ip')}/{ip_data.get('mask')}")
        
        # List credentials
        credentials = self.make_exotel_request('GET', f'/trunks/{trunk_sid}/credentials')
        if credentials and credentials.get('response'):
            print("\n🔑 Trunk Credentials:")
            for cred_response in credentials['response']:
                if cred_response.get('status') == 'success' and cred_response.get('data'):
                    cred = cred_response['data']
                    print(f"   ID: {cred.get('id')} - Type: {cred.get('type', 'N/A')}")
    
    def remove_trunk_destination(self, trunk_sid, destination_id):
        """Remove a destination from trunk"""
        print(f"🗑️  Removing destination {destination_id} from trunk {trunk_sid}...")
        
        result = self.make_exotel_request('DELETE', f'/trunks/{trunk_sid}/destination-uris/{destination_id}')
        
        if result:
            print(f"✅ Destination {destination_id} removed successfully")
            return True
        else:
            print(f"❌ Failed to remove destination {destination_id}")
            return False
    
    def remove_trunk_phone_number(self, trunk_sid, phone_mapping_id):
        """Remove a phone number mapping from trunk"""
        print(f"🗑️  Removing phone number mapping {phone_mapping_id} from trunk {trunk_sid}...")
        
        result = self.make_exotel_request('DELETE', f'/trunks/{trunk_sid}/phone-numbers/{phone_mapping_id}')
        
        if result:
            print(f"✅ Phone number mapping {phone_mapping_id} removed successfully")
            return True
        else:
            print(f"❌ Failed to remove phone number mapping {phone_mapping_id}")
            return False
    
    def list_vapi_resources(self):
        """List Vapi resources"""
        print("📋 Vapi Resources:")
        print("=" * 50)
        
        # List credentials
        creds_response = self.make_vapi_request('GET', '/credential')
        if creds_response.status_code == 200:
            credentials = creds_response.json()
            print("\n🔑 BYO Credentials:")
            for cred in credentials:
                if cred.get('provider') == 'byo-sip-trunk':
                    print(f"   ID: {cred.get('id')} - {cred.get('name')}")
        
        # List phone numbers
        phones_response = self.make_vapi_request('GET', '/phone-number')
        if phones_response.status_code == 200:
            phone_numbers = phones_response.json()
            print("\n📞 Phone Number Resources:")
            for phone in phone_numbers:
                if phone.get('provider') == 'byo-phone-number':
                    print(f"   ID: {phone.get('id')} - {phone.get('number')} ({phone.get('name')})")
    
    def remove_vapi_credential(self, credential_id):
        """Remove a Vapi BYO credential"""
        print(f"🗑️  Removing Vapi credential {credential_id}...")
        
        response = self.make_vapi_request('DELETE', f'/credential/{credential_id}')
        
        if response.status_code == 200:
            print(f"✅ Credential {credential_id} removed successfully")
            return True
        else:
            print(f"❌ Failed to remove credential {credential_id}: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    
    def remove_vapi_phone_number(self, phone_number_id):
        """Remove a Vapi phone number resource"""
        print(f"🗑️  Removing Vapi phone number resource {phone_number_id}...")
        
        response = self.make_vapi_request('DELETE', f'/phone-number/{phone_number_id}')
        
        if response.status_code == 200:
            print(f"✅ Phone number resource {phone_number_id} removed successfully")
            return True
        else:
            print(f"❌ Failed to remove phone number resource {phone_number_id}: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    
    def delete_trunk(self, trunk_sid):
        """Delete an entire Exotel trunk"""
        print(f"🗑️  Deleting trunk {trunk_sid}...")
        print("⚠️  WARNING: This will delete the entire trunk and all its resources!")
        
        # First list resources to show what will be deleted
        print("\n📋 Resources that will be deleted:")
        self.list_trunk_resources(trunk_sid)
        
        confirm = input("\n❓ Are you sure you want to delete this trunk? (yes/no): ")
        if confirm.lower() != 'yes':
            print("❌ Trunk deletion cancelled")
            return False
        
        result = self.make_exotel_request('DELETE', f'/trunks?trunk_sid={trunk_sid}')
        
        if result:
            print(f"✅ Trunk {trunk_sid} deleted successfully")
            return True
        else:
            print(f"❌ Failed to delete trunk {trunk_sid}")
            return False

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description='Cleanup Vapi-Exotel Integration Resources')
    parser.add_argument('--list-resources', action='store_true', help='List all resources')
    parser.add_argument('--list-trunk', help='List resources for specific trunk')
    parser.add_argument('--remove-destination', nargs=2, metavar=('TRUNK_SID', 'DEST_ID'), help='Remove trunk destination')
    parser.add_argument('--remove-phone-mapping', nargs=2, metavar=('TRUNK_SID', 'MAPPING_ID'), help='Remove phone number mapping')
    parser.add_argument('--remove-vapi-credential', help='Remove Vapi BYO credential')
    parser.add_argument('--remove-vapi-phone', help='Remove Vapi phone number resource')
    parser.add_argument('--delete-trunk', help='Delete entire trunk (WARNING: Destructive operation)')
    parser.add_argument('--list-vapi', action='store_true', help='List Vapi resources only')
    
    args = parser.parse_args()
    
    cleanup = ResourceCleanup()
    
    if args.list_resources:
        # List all trunks first
        trunks = cleanup.make_exotel_request('GET', '/trunks')
        if trunks and trunks.get('response'):
            print("📋 All Exotel Trunks:")
            for trunk_response in trunks['response']:
                if trunk_response.get('status') == 'success' and trunk_response.get('data'):
                    trunk = trunk_response['data']
                    print(f"   {trunk.get('trunk_sid')} - {trunk.get('trunk_name')} ({trunk.get('status')})")
        
        print("\n")
        cleanup.list_vapi_resources()
    
    elif args.list_trunk:
        cleanup.list_trunk_resources(args.list_trunk)
    
    elif args.list_vapi:
        cleanup.list_vapi_resources()
    
    elif args.remove_destination:
        trunk_sid, dest_id = args.remove_destination
        cleanup.remove_trunk_destination(trunk_sid, dest_id)
    
    elif args.remove_phone_mapping:
        trunk_sid, mapping_id = args.remove_phone_mapping
        cleanup.remove_trunk_phone_number(trunk_sid, mapping_id)
    
    elif args.remove_vapi_credential:
        cleanup.remove_vapi_credential(args.remove_vapi_credential)
    
    elif args.remove_vapi_phone:
        cleanup.remove_vapi_phone_number(args.remove_vapi_phone)
    
    elif args.delete_trunk:
        cleanup.delete_trunk(args.delete_trunk)
    
    else:
        print("🧹 Vapi-Exotel Resource Cleanup Tool")
        print("=" * 50)
        print()
        print("Available commands:")
        print("  --list-resources              List all resources")
        print("  --list-trunk TRUNK_SID        List resources for specific trunk")
        print("  --list-vapi                   List Vapi resources only")
        print("  --remove-destination TRUNK_SID DEST_ID")
        print("  --remove-phone-mapping TRUNK_SID MAPPING_ID")
        print("  --remove-vapi-credential CREDENTIAL_ID")
        print("  --remove-vapi-phone PHONE_NUMBER_ID")
        print("  --delete-trunk TRUNK_SID      Delete entire trunk (DESTRUCTIVE)")
        print()
        print("Examples:")
        print("  python3 cleanup_resources.py --list-resources")
        print("  python3 cleanup_resources.py --list-trunk trmum12345")
        print("  python3 cleanup_resources.py --remove-destination trmum12345 1234")
        print("  python3 cleanup_resources.py --delete-trunk trmum12345")

if __name__ == '__main__':
    main() 