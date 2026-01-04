# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# (c) IT4Innovations, VSB-TUO


import functools
import logging
import tempfile
import os
from pathlib import Path, PurePath
import typing
import asyncio

import os
import platform
import socket
import subprocess
import threading
import time
import shutil
from contextlib import closing

################################
import time
################################

import bpy
import braas_hpc 

#############################################################################
def get_job_local_storage_interactive(job_name):
    local_storage_interactive = Path(braas_hpc.raas_connection.get_pref_storage_dir()) / job_name / 'interactive'
    return local_storage_interactive    

def get_job_remote_storage_interactive(job_name):
    remote_storage_interactive = Path('interactive')
    return remote_storage_interactive

############################################################################
class SSHCommand(braas_hpc.raas_connection.SSHProcess):
    """
    SSH command execution using native OpenSSH.
    - Execute commands on remote host
    - Capture stdout/stderr
    - Support for long-running commands (infinite loops)
    """
    def __init__(
        self,
        user_host: str,                 # e.g. "user@remote-host"
        local_port: int,
        remote_host: str,
        remote_port: int,        
        command: str,                   # command to execute
        identity_file: str | None = None,
        ssh_path: str | None = None,    # path to ssh binary, default is found in PATH
        extra_ssh_opts: list[str] | None = None,
        auto_restart: bool = False      # Auto-restart for long-running commands
    ):
        super().__init__(
            user_host=user_host,
            identity_file=identity_file,
            auto_restart=auto_restart,
            check_interval_sec=5.0 if auto_restart else 0,
            ssh_path=ssh_path,
            extra_ssh_opts=extra_ssh_opts
        )
        self.command = command
        self.local_port = local_port
        self.remote_host = remote_host
        self.remote_port = remote_port

        self._stdout: str | None = None
        self._stderr: str | None = None
        self._returncode: int | None = None

    def _build_cmd(self) -> list[str]:
        cmd = [
            self.ssh_path,
            "-T",                     # no TTY
            "-o", "StrictHostKeyChecking=no",  # auto-accept host keys
            "-o", "UserKnownHostsFile=/dev/null",  # don't save host keys
            "-o", "ServerAliveInterval=30",
            "-o", "ServerAliveCountMax=3",
            "-o", "TCPKeepAlive=yes",
            "-L", f"{self.local_port}:{self.remote_host}:{self.remote_port}",
        ]

        if self.identity_file:
            cmd += ["-i", self.identity_file]

        # Add extra options (e.g., ProxyJump, Port, etc.)
        cmd += self.extra_ssh_opts

        cmd.append(self.user_host)
        # Wrap command in bash -c to properly handle shell metacharacters
        # cmd.append("bash")
        # cmd.append("-c")
        cmd.append(self.command)
        return cmd

    def start(self):
        """Start the SSH command process and keep it running (for long-running commands)."""
        print(f"[{self.__class__.__name__}] Starting SSH command: {self.command}")
        super().start()

    def execute(self, timeout: float | None = None) -> tuple[str, str, int]:
        """
        Execute the SSH command synchronously and return (stdout, stderr, returncode).
        Use this for short-lived commands that complete.
        
        Args:
            timeout: Maximum time to wait for command completion
            
        Returns:
            Tuple of (stdout, stderr, returncode)
        """
        print(f"[{self.__class__.__name__}] Executing SSH command: {self.command}")
        self._start_process()
        
        try:
            stdout, stderr = self._proc.communicate(timeout=timeout)
            self._stdout = stdout
            self._stderr = stderr
            self._returncode = self._proc.returncode
            
            if stdout:
                self._log_output("STDOUT", stdout)
            if stderr:
                self._log_output("STDERR", stderr)
                
            print(f"[{self.__class__.__name__}] Command completed with return code: {self._returncode}")
        except subprocess.TimeoutExpired:
            print(f"[{self.__class__.__name__}] Command timed out after {timeout}s")
            self._kill_proc()
            raise TimeoutError(f"SSH command timed out after {timeout}s")
        finally:
            self._proc = None
        
        return self._stdout, self._stderr, self._returncode

    @property
    def stdout(self) -> str | None:
        """Get stdout from last execution."""
        return self._stdout

    @property
    def stderr(self) -> str | None:
        """Get stderr from last execution."""
        return self._stderr

    @property
    def returncode(self) -> int | None:
        """Get return code from last execution."""
        return self._returncode
    
    def is_running(self) -> bool:
        """Check if the SSH command process is currently running."""
        return self._is_healthy()


class SSHCommandJump(SSHCommand):
    """
    SSH command execution through a jump host using ProxyJump.
    - Execute commands on remote host via jump host
    - Support for long-running commands (infinite loops)
    - Automatic ProxyJump configuration
    """
    def __init__(
        self,
        user_host: str,                 # e.g. "user@remote-host" (final destination)
        jump_host: str,                 # e.g. "user@jump-host" (intermediate host)
        local_port: int,
        remote_port: int,
        command: str,                   # command to execute
        identity_file: str | None = None,
        ssh_path: str | None = None,
        extra_ssh_opts: list[str] | None = None,
        auto_restart: bool = False
    ):
        # Don't call super().__init__ yet, we need to set jump_host first
        self.jump_host = jump_host
        self.local_port = int(local_port)
        self.remote_port = int(remote_port)
        #self.remote_host = remote_host       
        
        # Now call parent constructor
        super().__init__(
            user_host=user_host,
            local_port=local_port,
            remote_host="localhost",
            remote_port=remote_port,          
            command=command,
            identity_file=identity_file,
            ssh_path=ssh_path,
            extra_ssh_opts=extra_ssh_opts,
            auto_restart=auto_restart
        )

    def _build_cmd(self) -> list[str]:
        """Build SSH command with ProxyJump."""
        cmd = [
            self.ssh_path,
            "-T",                     # no TTY
            "-J", self.jump_host,     # ProxyJump through jump host
            "-o", "StrictHostKeyChecking=no",  # auto-accept host keys
            "-o", "UserKnownHostsFile=/dev/null",  # don't save host keys
            "-o", "ServerAliveInterval=30",
            "-o", "ServerAliveCountMax=3",
            "-o", "TCPKeepAlive=yes",
            "-L", f"{self.local_port}:localhost:{self.remote_port}",
        ]

        if self.identity_file:
            cmd += ["-i", self.identity_file]

        # Add extra options
        cmd += self.extra_ssh_opts

        cmd.append(self.user_host)
        # Wrap command in bash -c to properly handle shell metacharacters
        # cmd.append("bash")
        # cmd.append("-c")
        cmd.append(self.command)
        return cmd

############################################################################
class SSHTunnel(braas_hpc.raas_connection.SSHProcess):
    """
    SSH tunnel management using native OpenSSH.
    - start/stop
    - health check, optional auto-restart
    - configurable SSH options
    """
    def __init__(
        self,
        user_host: str,                 # e.g. "user@remote-host"
        local_host: str = "localhost",
        local_port: int = 7000,
        remote_host: str = "localhost",
        remote_port: int = 7000,
        identity_file: str | None = None,
        auto_restart: bool = True,
        check_interval_sec: float = 5.0,
        ssh_path: str | None = None,    # path to ssh binary, default is found in PATH
        extra_ssh_opts: list[str] | None = None
    ):
        super().__init__(
            user_host=user_host,
            identity_file=identity_file,
            auto_restart=auto_restart,
            check_interval_sec=check_interval_sec,
            ssh_path=ssh_path,
            extra_ssh_opts=extra_ssh_opts
        )
        self.local_host = local_host
        self.local_port = int(local_port)
        self.remote_host = remote_host
        self.remote_port = int(remote_port)

    @staticmethod
    def _is_port_listening(host: str, port: int, timeout: float = 0.2) -> bool:
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            s.settimeout(timeout)
            try:
                return s.connect_ex((host, port)) == 0
            except OSError:
                return False

    def _build_cmd(self) -> list[str]:
        cmd = [
            self.ssh_path,
            "-N",                     # no remote command (just the tunnel)
            "-T",                     # no TTY
            "-o", "StrictHostKeyChecking=no",  # auto-accept host keys
            "-o", "UserKnownHostsFile=/dev/null",  # don't save host keys
            #"-o", "ExitOnForwardFailure=yes",
            "-o", "ServerAliveInterval=20",
            "-o", "ServerAliveCountMax=3",
            #"-o", "Compression=no",
            #"-c",  "aes128-gcm@openssh.com",  # fast cipher (on ARM without AES-NI consider chacha20-poly1305)
            #"-L", f"{self.local_host}:{self.local_port}:{self.remote_host}:{self.remote_port}",
            "-L", f"{self.local_port}:{self.remote_host}:{self.remote_port}",
        ]
        # ControlMaster can speed up repeated connections; not always available (Windows OpenSSH sometimes lacks it).
        # Safe to leave disabled; if desired, uncomment:
        # cmd += ["-M", "-S", f"/tmp/ssh-ctrl-{self.local_port}", "-o", "ControlPersist=10m"]

        if self.identity_file:
            cmd += ["-i", self.identity_file]

        # Add extra options (e.g., ProxyJump, Port, etc.)
        cmd += self.extra_ssh_opts

        cmd.append(self.user_host)
        return cmd

    def _is_healthy(self) -> bool:
        """Check if tunnel process is alive and port is listening."""
        proc_alive = super()._is_healthy()
        port_listening = self._is_port_listening(self.local_host, self.local_port)
        return proc_alive and port_listening

    def start(self, wait_ready_timeout: float = 10.0):
        print(f"[{self.__class__.__name__}] Starting SSH tunnel: {self.user_host} (local:{self.local_port} -> remote:{self.remote_host}:{self.remote_port})")
        
        if self._proc and self._proc.poll() is None:
            print(f"[{self.__class__.__name__}] Tunnel already running")
            return  # already running

        # if the port is already taken, raise a meaningful error
        if self._is_port_listening(self.local_host, self.local_port):
            error_msg = f"Local port {self.local_host}:{self.local_port} is already in use – choose a different one or close the existing tunnel first."
            print(f"[{self.__class__.__name__}] ERROR: {error_msg}")
            raise RuntimeError(error_msg)

        self._start_process()

        # Wait until the tunnel is actually listening
        deadline = time.time() + wait_ready_timeout
        while time.time() < deadline:
            if self._is_port_listening(self.local_host, self.local_port):
                print(f"[{self.__class__.__name__}] Tunnel is ready and listening on {self.local_host}:{self.local_port}")
                break
            # if ssh already failed, grab its error output
            if self._proc.poll() is not None:
                out, err = self._proc.communicate(timeout=0.2)
                error_msg = f"SSH tunnel failed to start:\nSTDOUT: {out}\nSTDERR: {err}"
                print(f"[{self.__class__.__name__}] ERROR: {error_msg}")
                if braas_hpc.raas_connection.is_verbose_debug():
                    print(error_msg)
                raise RuntimeError(error_msg)
            time.sleep(0.1)
        else:
            # Capture any output before stopping
            if self._proc and self._proc.poll() is None:
                try:
                    out, err = self._proc.communicate(timeout=0.5)
                    print(f"[{self.__class__.__name__}] Tunnel timeout - STDOUT: {out}")
                    print(f"[{self.__class__.__name__}] Tunnel timeout - STDERR: {err}")
                    if braas_hpc.raas_connection.is_verbose_debug():
                        print(f"SSH tunnel timeout - STDOUT: {out}\nSTDERR: {err}")
                except:
                    pass
            self.stop()
            error_msg = f"SSH tunnel did not become ready within {wait_ready_timeout}s. Check your connection or SSH keys."
            print(f"[{self.__class__.__name__}] ERROR: {error_msg}")
            raise TimeoutError(error_msg)

        # watcher (optional auto-restart)
        self._stop_evt.clear()
        if self.auto_restart:
            self._watcher = threading.Thread(target=self._watch_loop, daemon=True)
            self._watcher.start()

    def is_running(self) -> bool:
        """Check if the SSH command process is currently running."""
        return self._is_healthy()



class SSHTunnelAsyncSSHJump:
    """
    SSH tunnel through a jump host using AsyncSSH.
    Creates an SSH tunnel with port forwarding via a proxy jump (bastion host).
    - Uses AsyncSSH for SSH connections
    - Supports authentication via key file or password
    - Runs tunnel in background thread with asyncio event loop
    - Automatic reconnection support
    
    Example usage:
        # Using key file authentication
        tunnel = SSHTunnelAsyncSSHJump(
            user_host="user@destination-host.com",
            jump_host="user@bastion-host.com",
            local_port=8080,
            remote_port=80,
            identity_file="/path/to/private/key",
            key_password="key_passphrase",  # Optional
            auto_restart=True
        )
        tunnel.start()
        
        # Using password authentication
        tunnel = SSHTunnelAsyncSSHJump(
            user_host="user@destination-host.com",
            jump_host="user@bastion-host.com",
            local_port=8080,
            remote_port=80,
            password="your_password",
            auto_restart=False
        )
        tunnel.start()
        
        # Check if running
        if tunnel.is_running():
            print("Tunnel is active")
        
        # Stop the tunnel
        tunnel.stop()
    """
    def __init__(
        self,
        user_host: str,                 # e.g. "user@remote-host" (final destination)
        jump_host: str,                 # e.g. "user@jump-host" (intermediate host)
        local_port: int,
        remote_port: int,
        identity_file: str | None = None,
        key_password: str | None = None,
        password: str | None = None,
        auto_restart: bool = False
    ):
        self.user_host = user_host
        self.jump_host = jump_host
        self.local_port = int(local_port)
        self.remote_port = int(remote_port)
        self.identity_file = identity_file
        self.key_password = key_password
        self.password = password
        self.auto_restart = auto_restart
        
        # Parse user and host from strings
        self._parse_hosts()
        
        # Threading and connection state
        self._thread = None
        self._stop_event = threading.Event()
        self._running = False
        self._loop = None
        self._jump_conn = None
        self._dest_conn = None
        
        # Output capture for debugging
        self._stdout_buffer = []
        self._stderr_buffer = []
        self._max_buffer_lines = 100  # Keep last 100 lines
        
    def _parse_hosts(self):
        """Parse username and hostname from user@host strings."""
        # Parse jump host
        if self.jump_host:
            if '@' in self.jump_host:
                self.jump_user, self.jump_hostname = self.jump_host.split('@', 1)
            else:
                self.jump_user = os.getenv('USER', 'root')
                self.jump_hostname = self.jump_host
        else:
            self.jump_user = None
            self.jump_hostname = None
            
        # Parse destination host
        if '@' in self.user_host:
            self.dest_user, self.dest_hostname = self.user_host.split('@', 1)
        else:
            self.dest_user = os.getenv('USER', 'root')
            self.dest_hostname = self.user_host
    
    def _log_output(self, stream_name: str, output: str):
        """Log output with timestamp and process info."""
        if not output:
            return
            
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        prefix = f"[{timestamp}] [{self.__class__.__name__}] [{stream_name}]"
        
        for line in output.splitlines():
            if line.strip():
                log_msg = f"{prefix}: {line}"
                print(log_msg)
                
                # Store in buffer
                if stream_name == "STDOUT":
                    self._stdout_buffer.append(line)
                    if len(self._stdout_buffer) > self._max_buffer_lines:
                        self._stdout_buffer.pop(0)
                else:
                    self._stderr_buffer.append(line)
                    if len(self._stderr_buffer) > self._max_buffer_lines:
                        self._stderr_buffer.pop(0)
    
    def get_stdout(self) -> list[str]:
        """Get captured stdout lines."""
        return self._stdout_buffer.copy()
    
    def get_stderr(self) -> list[str]:
        """Get captured stderr lines."""
        return self._stderr_buffer.copy()
    
    def print_status(self):
        """Print current status and recent output."""
        print(f"\n=== {self.__class__.__name__} Status ===")
        print(f"Running: {self.is_running()}")
        print(f"\nRecent STDOUT ({len(self._stdout_buffer)} lines):")
        for line in self._stdout_buffer[-10:]:
            print(f"  {line}")
        print(f"\nRecent STDERR ({len(self._stderr_buffer)} lines):")
        for line in self._stderr_buffer[-10:]:
            print(f"  {line}")
        print("=" * 50)
    
    async def _forward_connection(self, reader, writer):
        """Handle a single connection forward from local to remote."""
        import asyncssh
        
        try:
            # Open connection through destination to remote port
            dest_reader, dest_writer = await self._dest_conn.open_connection('localhost', self.remote_port)
            
            # Bidirectional forwarding
            async def forward_data(src_reader, dst_writer):
                try:
                    while not self._stop_event.is_set():
                        data = await src_reader.read(8192)
                        if not data:
                            break
                        dst_writer.write(data)
                        await dst_writer.drain()
                except:
                    pass
                finally:
                    try:
                        dst_writer.close()
                        await dst_writer.wait_closed()
                    except:
                        pass
            
            # Run both directions concurrently
            await asyncio.gather(
                forward_data(reader, dest_writer),
                forward_data(dest_reader, writer),
                return_exceptions=True
            )
        except Exception as e:
            self._log_output("STDERR", f"Port forwarding error: {e}")
            if braas_hpc.raas_connection.is_verbose_debug():
                print(f"Port forwarding error: {e}")
        finally:
            try:
                writer.close()
                await writer.wait_closed()
            except:
                pass
    
    async def _run_tunnel_async(self):
        """Main tunnel loop running in asyncio event loop."""
        import asyncssh
        
        try:
            # Load client keys if needed
            client_keys = []
            if not self.password and self.identity_file:
                try:
                    if self.key_password:
                        client_keys = [asyncssh.read_private_key(self.identity_file, passphrase=self.key_password)]
                    else:
                        client_keys = [asyncssh.read_private_key(self.identity_file)]
                except Exception as e:
                    raise Exception(f"Failed to load SSH key: {e}")
            
            # Handle direct connection (no jump host) vs jump host connection
            if self.jump_hostname:
                # Connect to jump host
                self._log_output("STDOUT", f"Connecting to jump host: {self.jump_hostname}")
                if braas_hpc.raas_connection.is_verbose_debug():
                    print(f"Connecting to jump host: {self.jump_hostname}")
                
                if self.password:
                    self._jump_conn = await asyncssh.connect(
                        self.jump_hostname,
                        username=self.jump_user,
                        password=self.password,
                        known_hosts=None
                    )
                else:
                    self._jump_conn = await asyncssh.connect(
                        self.jump_hostname,
                        username=self.jump_user,
                        client_keys=client_keys,
                        known_hosts=None
                    )
                
                self._log_output("STDOUT", f"Connected to jump host: {self.jump_hostname}")
                
                # Connect to destination through jump host
                self._log_output("STDOUT", f"Creating tunnel to destination: {self.dest_hostname}")
                if braas_hpc.raas_connection.is_verbose_debug():
                    print(f"Creating tunnel to destination: {self.dest_hostname}")
                
                if self.password:
                    self._dest_conn = await self._jump_conn.connect_ssh(
                        self.dest_hostname,
                        username=self.dest_user,
                        password=self.password,
                        known_hosts=None
                    )
                else:
                    self._dest_conn = await self._jump_conn.connect_ssh(
                        self.dest_hostname,
                        username=self.dest_user,
                        client_keys=client_keys,
                        known_hosts=None
                    )
                self._log_output("STDOUT", f"Connected to destination: {self.dest_hostname}")
            else:
                # Direct connection without jump host
                self._log_output("STDOUT", f"Connecting directly to: {self.dest_hostname}")
                if braas_hpc.raas_connection.is_verbose_debug():
                    print(f"Connecting directly to: {self.dest_hostname}")
                
                if self.password:
                    self._dest_conn = await asyncssh.connect(
                        self.dest_hostname,
                        username=self.dest_user,
                        password=self.password,
                        known_hosts=None
                    )
                else:
                    self._dest_conn = await asyncssh.connect(
                        self.dest_hostname,
                        username=self.dest_user,
                        client_keys=client_keys,
                        known_hosts=None
                    )
                self._log_output("STDOUT", f"Connected directly to: {self.dest_hostname}")
            
            # Set up local port forwarding
            self._log_output("STDOUT", f"Setting up port forward: localhost:{self.local_port} -> localhost:{self.remote_port}")
            if braas_hpc.raas_connection.is_verbose_debug():
                print(f"Setting up port forward: localhost:{self.local_port} -> localhost:{self.remote_port}")
            
            # Start server on local port
            server = await asyncio.start_server(
                self._forward_connection,
                'localhost',
                self.local_port
            )
            
            self._running = True
            self._log_output("STDOUT", f"Port forwarding active on localhost:{self.local_port}")
            
            # Keep server running until stop event
            async with server:
                while not self._stop_event.is_set():
                    await asyncio.sleep(1)
        
        except Exception as e:
            self._log_output("STDERR", f"SSH tunnel error: {e}")
            if braas_hpc.raas_connection.is_verbose_debug():
                print(f"SSH tunnel error: {e}")
            self._running = False
            
            if self.auto_restart and not self._stop_event.is_set():
                await asyncio.sleep(5)
                await self._run_tunnel_async()
        finally:
            self._log_output("STDOUT", "Port forwarding stopped")
            await self._cleanup_connections()
    
    async def _cleanup_connections(self):
        """Clean up SSH connections."""
        if self._dest_conn:
            try:
                self._dest_conn.close()
                await self._dest_conn.wait_closed()
            except:
                pass
            self._dest_conn = None
            
        if self._jump_conn:
            try:
                self._jump_conn.close()
                await self._jump_conn.wait_closed()
            except:
                pass
            self._jump_conn = None
    
    def _run_event_loop(self):
        """Run the asyncio event loop in a thread."""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        try:
            self._loop.run_until_complete(self._run_tunnel_async())
        finally:
            self._loop.close()
    
    def start(self):
        """Start the SSH tunnel in a background thread."""
        print(f"[{self.__class__.__name__}] Starting AsyncSSH tunnel: {self.jump_host} -> {self.user_host}")
        print(f"[{self.__class__.__name__}] Port forwarding: localhost:{self.local_port} -> localhost:{self.remote_port}")
        
        if self._thread and self._thread.is_alive():
            print(f"[{self.__class__.__name__}] SSH tunnel already running")
            if braas_hpc.raas_connection.is_verbose_debug():
                print("SSH tunnel already running")
            return
        
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_event_loop, daemon=True)
        self._thread.start()
        
        # Give it a moment to establish connection
        time.sleep(1)
        print(f"[{self.__class__.__name__}] AsyncSSH tunnel started (background thread)")
    
    def stop(self):
        """Stop the SSH tunnel."""
        print(f"[{self.__class__.__name__}] Stopping AsyncSSH tunnel")
        
        if braas_hpc.raas_connection.is_verbose_debug():
            print("Stopping SSH tunnel")
        
        self._stop_event.set()
        self._running = False
        
        if self._loop and not self._loop.is_closed():
            try:
                # Schedule cleanup in the loop
                asyncio.run_coroutine_threadsafe(self._cleanup_connections(), self._loop)
            except:
                pass
        
        if self._thread:
            self._thread.join(timeout=5)
            self._thread = None
    
    def is_running(self) -> bool:
        """Check if the tunnel is currently running."""
        return self._running and self._thread and self._thread.is_alive()


class SSHTunnelParamikoJump:
    """
    SSH tunnel through a jump host using Paramiko.
    Creates an SSH tunnel with port forwarding via a proxy jump (bastion host).
    - Uses Paramiko for SSH connections instead of subprocess
    - Supports authentication via key file or password
    - Runs tunnel in background thread
    - Automatic reconnection support
    
    Example usage:
        # Using key file authentication
        tunnel = SSHTunnelParamikoJump(
            user_host="user@destination-host.com",
            jump_host="user@bastion-host.com",
            local_port=8080,
            remote_port=80,
            identity_file="/path/to/private/key",
            key_password="key_passphrase",  # Optional
            auto_restart=True
        )
        tunnel.start()
        
        # Using password authentication
        tunnel = SSHTunnelParamikoJump(
            user_host="user@destination-host.com",
            jump_host="user@bastion-host.com",
            local_port=8080,
            remote_port=80,
            password="your_password",
            auto_restart=False
        )
        tunnel.start()
        
        # Check if running
        if tunnel.is_running():
            print("Tunnel is active")
        
        # Stop the tunnel
        tunnel.stop()
    """
    def __init__(
        self,
        user_host: str,                 # e.g. "user@remote-host" (final destination)
        jump_host: str,                 # e.g. "user@jump-host" (intermediate host)
        local_port: int,
        remote_port: int,
        identity_file: str | None = None,
        key_password: str | None = None,
        password: str | None = None,
        auto_restart: bool = False
    ):
        self.user_host = user_host
        self.jump_host = jump_host
        self.local_port = int(local_port)
        self.remote_port = int(remote_port)
        self.identity_file = identity_file
        self.key_password = key_password
        self.password = password
        self.auto_restart = auto_restart
        
        # Parse user and host from strings
        self._parse_hosts()
        
        # Threading and connection state
        self._thread = None
        self._stop_event = threading.Event()
        self._running = False
        self._jump_client = None
        self._dest_client = None
        self._transport = None
        
        # Output capture for debugging
        self._stdout_buffer = []
        self._stderr_buffer = []
        self._max_buffer_lines = 100  # Keep last 100 lines
        
    def _parse_hosts(self):
        """Parse username and hostname from user@host strings."""
        # Parse jump host
        if self.jump_host:
            if '@' in self.jump_host:
                self.jump_user, self.jump_hostname = self.jump_host.split('@', 1)
            else:
                self.jump_user = os.getenv('USER', 'root')
                self.jump_hostname = self.jump_host
        else:
            self.jump_user = None
            self.jump_hostname = None
            
        # Parse destination host
        if '@' in self.user_host:
            self.dest_user, self.dest_hostname = self.user_host.split('@', 1)
        else:
            self.dest_user = os.getenv('USER', 'root')
            self.dest_hostname = self.user_host
    
    def _log_output(self, stream_name: str, output: str):
        """Log output with timestamp and process info."""
        if not output:
            return
            
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        prefix = f"[{timestamp}] [{self.__class__.__name__}] [{stream_name}]"
        
        for line in output.splitlines():
            if line.strip():
                log_msg = f"{prefix}: {line}"
                print(log_msg)
                
                # Store in buffer
                if stream_name == "STDOUT":
                    self._stdout_buffer.append(line)
                    if len(self._stdout_buffer) > self._max_buffer_lines:
                        self._stdout_buffer.pop(0)
                else:
                    self._stderr_buffer.append(line)
                    if len(self._stderr_buffer) > self._max_buffer_lines:
                        self._stderr_buffer.pop(0)
    
    def get_stdout(self) -> list[str]:
        """Get captured stdout lines."""
        return self._stdout_buffer.copy()
    
    def get_stderr(self) -> list[str]:
        """Get captured stderr lines."""
        return self._stderr_buffer.copy()
    
    def print_status(self):
        """Print current status and recent output."""
        print(f"\n=== {self.__class__.__name__} Status ===")
        print(f"Running: {self.is_running()}")
        print(f"\nRecent STDOUT ({len(self._stdout_buffer)} lines):")
        for line in self._stdout_buffer[-10:]:
            print(f"  {line}")
        print(f"\nRecent STDERR ({len(self._stderr_buffer)} lines):")
        for line in self._stderr_buffer[-10:]:
            print(f"  {line}")
        print("=" * 50)
    
    def _load_key(self):
        """Load SSH key from file."""
        import paramiko
        
        if not self.identity_file:
            return None
            
        try:
            if self.key_password:
                return paramiko.RSAKey.from_private_key_file(self.identity_file, self.key_password)
            else:
                return paramiko.RSAKey.from_private_key_file(self.identity_file)
        except Exception:
            try:
                if self.key_password:
                    return paramiko.Ed25519Key.from_private_key_file(self.identity_file, self.key_password)
                else:
                    return paramiko.Ed25519Key.from_private_key_file(self.identity_file)
            except Exception as e:
                raise Exception(f"Failed to load SSH key from {self.identity_file}: {e}")
    
    def _create_ssh_client(self, hostname, username, port=22):
        """Create and connect an SSH client."""
        import paramiko
        
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.load_system_host_keys()
        
        connect_kwargs = {
            'hostname': hostname,
            'port': port,
            'username': username,
            'look_for_keys': False,
            'allow_agent': False
        }
        
        if self.password:
            connect_kwargs['password'] = self.password
        else:
            key = self._load_key()
            if key:
                connect_kwargs['pkey'] = key
        
        ssh.connect(**connect_kwargs)
        ssh.get_transport().set_keepalive(30)
        
        return ssh
    
    def _port_forward_handler(self, channel):
        """Handle incoming connections on the local port and forward to remote."""
        import paramiko
        
        try:
            # Connect to the remote port through the destination SSH connection
            remote_channel = self._dest_client.get_transport().open_channel(
                'direct-tcpip',
                ('localhost', self.remote_port),
                ('localhost', 0)
            )
            
            # Bidirectional forwarding
            while not self._stop_event.is_set():
                import select
                r, w, x = select.select([channel, remote_channel], [], [], 1.0)
                
                if channel in r:
                    data = channel.recv(1024)
                    if len(data) == 0:
                        break
                    remote_channel.send(data)
                
                if remote_channel in r:
                    data = remote_channel.recv(1024)
                    if len(data) == 0:
                        break
                    channel.send(data)
                    
            channel.close()
            remote_channel.close()
        except Exception as e:
            if braas_hpc.raas_connection.is_verbose_debug():
                print(f"Port forwarding error: {e}")
    
    def _run_tunnel(self):
        """Main tunnel loop running in background thread."""
        import paramiko
        
        try:
            # Handle direct connection (no jump host) vs jump host connection
            if self.jump_hostname:
                # Connect to jump host
                self._log_output("STDOUT", f"Connecting to jump host: {self.jump_hostname}")
                if braas_hpc.raas_connection.is_verbose_debug():
                    print(f"Connecting to jump host: {self.jump_hostname}")
                
                self._jump_client = self._create_ssh_client(self.jump_hostname, self.jump_user)
                self._log_output("STDOUT", f"Connected to jump host: {self.jump_hostname}")
                
                # Create tunnel through jump host to destination
                self._log_output("STDOUT", f"Creating tunnel to destination: {self.dest_hostname}")
                if braas_hpc.raas_connection.is_verbose_debug():
                    print(f"Creating tunnel to destination: {self.dest_hostname}")
                
                jump_transport = self._jump_client.get_transport()
                dest_addr = (self.dest_hostname, 22)
                local_addr = ('localhost', 0)
                jump_channel = jump_transport.open_channel('direct-tcpip', dest_addr, local_addr)
                
                # Connect to destination through the jump host channel
                self._dest_client = paramiko.SSHClient()
                self._dest_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                
                connect_kwargs = {
                    'username': self.dest_user,
                    'look_for_keys': False,
                    'allow_agent': False,
                    'sock': jump_channel
                }
                
                if self.password:
                    connect_kwargs['password'] = self.password
                else:
                    key = self._load_key()
                    if key:
                        connect_kwargs['pkey'] = key
                
                self._dest_client.connect(self.dest_hostname, **connect_kwargs)
                self._dest_client.get_transport().set_keepalive(30)
                self._log_output("STDOUT", f"Connected to destination: {self.dest_hostname}")
            else:
                # Direct connection without jump host
                self._log_output("STDOUT", f"Connecting directly to: {self.dest_hostname}")
                if braas_hpc.raas_connection.is_verbose_debug():
                    print(f"Connecting directly to: {self.dest_hostname}")
                
                self._dest_client = self._create_ssh_client(self.dest_hostname, self.dest_user)
                self._log_output("STDOUT", f"Connected directly to: {self.dest_hostname}")
                if key:
                    connect_kwargs['pkey'] = key
            
            self._dest_client.connect(self.dest_hostname, **connect_kwargs)
            self._dest_client.get_transport().set_keepalive(30)
            
            # Set up local port forwarding
            self._log_output("STDOUT", f"Setting up port forward: localhost:{self.local_port} -> localhost:{self.remote_port}")
            if braas_hpc.raas_connection.is_verbose_debug():
                print(f"Setting up port forward: localhost:{self.local_port} -> localhost:{self.remote_port}")
            
            # Create local server socket
            import socket
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind(('localhost', self.local_port))
            server_socket.listen(5)
            server_socket.settimeout(1.0)  # Allow checking stop event
            
            self._running = True
            self._log_output("STDOUT", f"Port forwarding active on localhost:{self.local_port}")
            
            # Accept connections and forward them
            while not self._stop_event.is_set():
                try:
                    client_socket, addr = server_socket.accept()
                    self._log_output("STDOUT", f"Accepted connection from {addr}")
                    if braas_hpc.raas_connection.is_verbose_debug():
                        print(f"Accepted connection from {addr}")
                    
                    # Handle this connection in the same thread (simple version)
                    # For production, you might want to spawn a new thread per connection
                    channel = self._dest_client.get_transport().open_channel(
                        'direct-tcpip',
                        ('localhost', self.remote_port),
                        ('localhost', 0)
                    )
                    
                    # Simple bidirectional forwarding
                    def forward(src, dst):
                        try:
                            while not self._stop_event.is_set():
                                data = src.recv(1024)
                                if len(data) == 0:
                                    break
                                dst.send(data)
                        except:
                            pass
                        finally:
                            src.close()
                            dst.close()
                    
                    # Forward in both directions using threads
                    t1 = threading.Thread(target=forward, args=(client_socket, channel))
                    t2 = threading.Thread(target=forward, args=(channel, client_socket))
                    t1.daemon = True
                    t2.daemon = True
                    t1.start()
                    t2.start()
                    
                except socket.timeout:
                    continue
                except Exception as e:
                    self._log_output("STDERR", f"Connection accept error: {e}")
                    if not self._stop_event.is_set() and braas_hpc.raas_connection.is_verbose_debug():
                        print(f"Connection accept error: {e}")
            
            server_socket.close()
            self._log_output("STDOUT", "Port forwarding stopped")
            
        except Exception as e:
            self._log_output("STDERR", f"SSH tunnel error: {e}")
            if braas_hpc.raas_connection.is_verbose_debug():
                print(f"SSH tunnel error: {e}")
            self._running = False
            
            if self.auto_restart and not self._stop_event.is_set():
                time.sleep(5)
                self._run_tunnel()
        finally:
            self._cleanup_connections()
    
    def _cleanup_connections(self):
        """Clean up SSH connections."""
        if self._dest_client:
            try:
                self._dest_client.close()
            except:
                pass
            self._dest_client = None
            
        if self._jump_client:
            try:
                self._jump_client.close()
            except:
                pass
            self._jump_client = None
    
    def start(self):
        """Start the SSH tunnel in a background thread."""
        print(f"[{self.__class__.__name__}] Starting Paramiko tunnel: {self.jump_host} -> {self.user_host}")
        print(f"[{self.__class__.__name__}] Port forwarding: localhost:{self.local_port} -> localhost:{self.remote_port}")
        
        if self._thread and self._thread.is_alive():
            print(f"[{self.__class__.__name__}] SSH tunnel already running")
            if braas_hpc.raas_connection.is_verbose_debug():
                print("SSH tunnel already running")
            return
        
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_tunnel, daemon=True)
        self._thread.start()
        
        # Give it a moment to establish connection
        time.sleep(1)
        print(f"[{self.__class__.__name__}] Paramiko tunnel started (background thread)")
    
    def stop(self):
        """Stop the SSH tunnel."""
        print(f"[{self.__class__.__name__}] Stopping Paramiko tunnel")
        
        if braas_hpc.raas_connection.is_verbose_debug():
            print("Stopping SSH tunnel")
            print("Stopping SSH tunnel")
        
        self._stop_event.set()
        self._running = False
        self._cleanup_connections()
        
        if self._thread:
            self._thread.join(timeout=5)
            self._thread = None
    
    def is_running(self) -> bool:
        """Check if the tunnel is currently running."""
        return self._running and self._thread and self._thread.is_alive()


#############################################################################
class RaasInteractiveSession:
    def __init__(self):
        self.ssh_tunnel_proc = None
        self.ssh_tunnel_paramiko_jump = None
        self.ssh_tunnel_asyncssh_jump = None
        self.ssh_command_proc = None
        self.ssh_command_jump_proc = None

    def create_ssh_command(self, key_file, key_password, password, destination, node, local_port, remote_port, command, ssh_library='SYSTEM', auto_restart=False):
        """create_ssh_command - Start a long-running SSH command process with tunnel
        
        Creates an SSH tunnel with port forwarding and executes a command on the remote host.
        The implementation used depends on ssh_library parameter.
        
        Args:
            key_file: Path to SSH private key file
            key_password: Password for encrypted key file (optional)
            password: Password for password-based auth (optional)
            destination: Destination host (format: user@host)
            node: Remote host for port forwarding (usually 'localhost')
            local_port: Local port for tunnel
            remote_port: Remote port to forward to
            command: Command to execute on remote host
            ssh_library: 'SYSTEM' (OpenSSH), 'PARAMIKO', or 'ASYNCSSH'
            auto_restart: Whether to automatically restart on connection failure
        """
        print(f"[RaasInteractiveSession] Creating SSH command+tunnel to {destination} using {ssh_library}")
        print(f"[RaasInteractiveSession] Port forwarding: localhost:{local_port} -> {node}:{remote_port}")
        print(f"[RaasInteractiveSession] Command: {command}")

        if not self.ssh_command_proc is None:
            print(f"[RaasInteractiveSession] Stopping existing SSH command process")
            self.ssh_command_proc.stop()
            self.ssh_command_proc = None

        if ssh_library == 'SYSTEM':
            # Use native OpenSSH implementation
            self.ssh_command_proc = SSHCommand(
                user_host=destination,
                local_port=local_port,
                remote_host=node,
                remote_port=remote_port,
                command=command,
                identity_file=key_file,
                auto_restart=auto_restart
            )
        elif ssh_library == 'PARAMIKO':
            # For Paramiko, we need to use the tunnel implementation
            # that combines tunnel + command execution
            print(f"[RaasInteractiveSession] Note: Paramiko implementation creates tunnel only, command execution separate")
            self.ssh_command_proc = SSHTunnelParamikoJump(
                user_host=destination,
                jump_host=None,  # No jump host for direct connection
                local_port=local_port,
                remote_port=remote_port,
                identity_file=key_file,
                key_password=key_password,
                password=password,
                auto_restart=auto_restart
            )
        elif ssh_library == 'ASYNCSSH':
            # For AsyncSSH, we need to use the tunnel implementation
            print(f"[RaasInteractiveSession] Note: AsyncSSH implementation creates tunnel only, command execution separate")
            self.ssh_command_proc = SSHTunnelAsyncSSHJump(
                user_host=destination,
                jump_host=None,  # No jump host for direct connection
                local_port=local_port,
                remote_port=remote_port,
                identity_file=key_file,
                key_password=key_password,
                password=password,
                auto_restart=auto_restart
            )
        else:
            raise ValueError(f"Unknown SSH library: {ssh_library}")

        # Start the command process (it will keep running in background)
        self.ssh_command_proc.start()
        print(f"[RaasInteractiveSession] SSH command+tunnel started successfully")

    def close_ssh_command(self):
        """close_ssh_command - Stop/kill the running SSH command process"""

        if not self.ssh_command_proc is None:
            print(f"[RaasInteractiveSession] Stopping SSH command process")
            self.ssh_command_proc.stop()
            self.ssh_command_proc = None

    def create_ssh_command_jump(self, key_file, key_password, password, jump_host, destination, node, local_port, remote_port, command, ssh_library='SYSTEM', auto_restart=False):
        """create_ssh_command_jump - Start a long-running SSH command process through a jump host with tunnel
        
        Creates an SSH tunnel with port forwarding through a jump host and executes a command.
        The implementation used depends on ssh_library parameter.
        
        Args:
            key_file: Path to SSH private key file
            key_password: Password for encrypted key file (optional)
            password: Password for password-based auth (optional)
            jump_host: Jump/bastion host (format: user@host)
            destination: Final destination host (format: user@host)
            node: Remote host for port forwarding (usually 'localhost')
            local_port: Local port for tunnel
            remote_port: Remote port to forward to
            command: Command to execute on remote host
            ssh_library: 'SYSTEM' (OpenSSH), 'PARAMIKO', or 'ASYNCSSH'
            auto_restart: Whether to automatically restart on connection failure
        """
        print(f"[RaasInteractiveSession] Creating SSH command+tunnel with jump: {jump_host} -> {destination} using {ssh_library}")
        print(f"[RaasInteractiveSession] Port forwarding: localhost:{local_port} -> {node}:{remote_port}")
        print(f"[RaasInteractiveSession] Command: {command}")

        if not self.ssh_command_jump_proc is None:
            print(f"[RaasInteractiveSession] Stopping existing SSH command jump process")
            self.ssh_command_jump_proc.stop()
            self.ssh_command_jump_proc = None

        if ssh_library == 'SYSTEM':
            # Use native OpenSSH implementation with ProxyJump
            self.ssh_command_jump_proc = SSHCommandJump(
                user_host=destination,
                jump_host=jump_host,
                local_port=local_port,
                remote_port=remote_port,
                command=command,
                identity_file=key_file,
                auto_restart=auto_restart
            )
        elif ssh_library == 'PARAMIKO':
            # Use Paramiko tunnel implementation with jump host
            self.ssh_command_jump_proc = SSHTunnelParamikoJump(
                user_host=destination,
                jump_host=jump_host,
                local_port=local_port,
                remote_port=remote_port,
                identity_file=key_file,
                key_password=key_password,
                password=password,
                auto_restart=auto_restart
            )
        elif ssh_library == 'ASYNCSSH':
            # Use AsyncSSH tunnel implementation with jump host
            self.ssh_command_jump_proc = SSHTunnelAsyncSSHJump(
                user_host=destination,
                jump_host=jump_host,
                local_port=local_port,
                remote_port=remote_port,
                identity_file=key_file,
                key_password=key_password,
                password=password,
                auto_restart=auto_restart
            )
        else:
            raise ValueError(f"Unknown SSH library: {ssh_library}")

        # Start the command process (it will keep running in background)
        self.ssh_command_jump_proc.start()
        print(f"[RaasInteractiveSession] SSH command+tunnel jump started successfully")

    def close_ssh_command_jump(self):
        """close_ssh_command_jump - Stop/kill the running SSH command process with jump host"""

        if not self.ssh_command_jump_proc is None:
            print(f"[RaasInteractiveSession] Stopping SSH command jump process")
            self.ssh_command_jump_proc.stop()
            self.ssh_command_jump_proc = None

    def close_ssh_tunnel(self):
        """close_ssh_tunnel - Alias for close_ssh_command for backward compatibility"""
        self.close_ssh_command()

    def create_ssh_tunnel_paramiko_jump(self, key_file, key_password, password, jump_host, destination, local_port, remote_port, auto_restart=False):
        """create_ssh_tunnel_paramiko_jump - Create SSH tunnel through jump host using Paramiko
        
        Args:
            key_file: Path to SSH private key file
            key_password: Password for encrypted key file (optional)
            password: Password for password-based auth (optional)
            jump_host: Jump/bastion host (format: user@host)
            destination: Final destination host (format: user@host)
            local_port: Local port for tunnel
            remote_port: Remote port to forward to
            auto_restart: Whether to automatically restart on connection failure
        """
        if not self.ssh_tunnel_paramiko_jump is None:
            self.ssh_tunnel_paramiko_jump.stop()
            self.ssh_tunnel_paramiko_jump = None

        self.ssh_tunnel_paramiko_jump = SSHTunnelParamikoJump(
            user_host=destination,
            jump_host=jump_host,
            local_port=local_port,
            remote_port=remote_port,
            identity_file=key_file,
            key_password=key_password,
            password=password,
            auto_restart=auto_restart
        )

        # Start the tunnel (runs in background thread)
        self.ssh_tunnel_paramiko_jump.start()

    def close_ssh_tunnel_paramiko_jump(self):
        """close_ssh_tunnel_paramiko_jump - Stop the Paramiko SSH tunnel with jump host"""

        if not self.ssh_tunnel_paramiko_jump is None:
            self.ssh_tunnel_paramiko_jump.stop()
            self.ssh_tunnel_paramiko_jump = None

    def create_ssh_tunnel_asyncssh_jump(self, key_file, key_password, password, jump_host, destination, local_port, remote_port, auto_restart=False):
        """create_ssh_tunnel_asyncssh_jump - Create SSH tunnel through jump host using AsyncSSH
        
        Args:
            key_file: Path to SSH private key file
            key_password: Password for encrypted key file (optional)
            password: Password for password-based auth (optional)
            jump_host: Jump/bastion host (format: user@host)
            destination: Final destination host (format: user@host)
            local_port: Local port for tunnel
            remote_port: Remote port to forward to
            auto_restart: Whether to automatically restart on connection failure
        """
        if not self.ssh_tunnel_asyncssh_jump is None:
            self.ssh_tunnel_asyncssh_jump.stop()
            self.ssh_tunnel_asyncssh_jump = None

        self.ssh_tunnel_asyncssh_jump = SSHTunnelAsyncSSHJump(
            user_host=destination,
            jump_host=jump_host,
            local_port=local_port,
            remote_port=remote_port,
            identity_file=key_file,
            key_password=key_password,
            password=password,
            auto_restart=auto_restart
        )

        # Start the tunnel (runs in background thread)
        self.ssh_tunnel_asyncssh_jump.start()

    def close_ssh_tunnel_asyncssh_jump(self):
        """close_ssh_tunnel_asyncssh_jump - Stop the AsyncSSH tunnel with jump host"""

        if not self.ssh_tunnel_asyncssh_jump is None:
            self.ssh_tunnel_asyncssh_jump.stop()
            self.ssh_tunnel_asyncssh_jump = None