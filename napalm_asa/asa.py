# -*- coding: utf-8 -*-
# Copyright 2016 Dravetech AB. All rights reserved.
#
# The contents of this file are licensed under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with the
# License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

"""
Napalm driver for Cisco ASAs.

Read https://napalm.readthedocs.io for more information.
"""
from netmiko import  __version__ as netmiko_version
from netmiko import ConnectHandler
from napalm.base import NetworkDriver



class ASADriver(NetworkDriver):
    """Napalm driver for a Cisco ASA using SSH."""

    def __init__(self, hostname, username, password, timeout=60, optional_args=None):
        """Constructor."""
        self.device = None
        self.hostname = hostname
        self.username = username
        self.password = password
        self.timeout = timeout

        if optional_args is None:
            optional_args = {}

        # Netmiko possible arguments
        netmiko_argument_map = {
            'ip': None,
            'username': None,
            'password': None,
            'port': None,
            'secret': '',
            'verbose': False,
            'keepalive': 30,
            'global_delay_factor': 3,
            'use_keys': False,
            'key_file': None,
            'ssh_strict': False,
            'system_host_keys': False,
            'alt_host_keys': False,
            'alt_key_file': '',
            'ssh_config_file': None,
        }
        fields = netmiko_version.split('.')
        fields = [int(x) for x in fields]
        maj_ver, min_ver, bug_fix = fields
        if maj_ver >= 2:
            netmiko_argument_map['allow_agent'] = False
        elif maj_ver == 1 and min_ver >= 1:
            netmiko_argument_map['allow_agent'] = False

        self.netmiko_optional_args = {}
        # Build dict of any optional Netmiko args
        for k, v in netmiko_argument_map.items():
            try:
                self.netmiko_optional_args[k] = optional_args[k]
            except KeyError:
                pass

    def open(self):
        """Open a connection"""
        self.device = ConnectHandler(
            device_type='cisco_asa',
            host=self.hostname,
            username=self.username,
            password=self.password,
            **self.netmiko_optional_args
        )


    def close(self):
        """Close the connection to the device"""
        self.device.disconnect()


    def cli(self, commands):
        """ Will execute a list of commands and return the output in a dictionary format"""
        cli_output = dict()
        if type(commands) is not list and type(commands) is str:
            commands = [commands]

        for command in commands:
            output = self.device.send_command(command)
            unknown_action = re.search('Invalid input detected', output)
            if unknown_action:
                msg = 'Unable to execute command {cmd} \nOutput: {out}'.format(cmd=command, out=output)
                logger.error(msg)
            cli_output.setdefault(command, {})
            cli_output[command] = output
        return cli_output
