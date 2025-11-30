#!/usr/bin/env python3
"""
A5000mine ISO Builder Server
Web interface for creating custom bootable mining ISOs
"""

import json
import os
import subprocess
import threading
import time
import uuid
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler, HTTPStatus
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import tempfile
import shutil

# Configuration
BUILD_DIR = os.path.join(os.path.dirname(__file__), '..', 'build')
ISO_BUILDER_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.join(ISO_BUILDER_DIR, '..')
CONFIG_FILE = os.path.join(PROJECT_ROOT, 'config', 'config.json')

# Global state for builds
active_builds = {}
build_lock = threading.Lock()

class ISOBuilderHandler(SimpleHTTPRequestHandler):
    """Custom HTTP request handler for ISO builder"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ISO_BUILDER_DIR, **kwargs)

    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)

        if parsed_path.path == '/api/build-status':
            self.handle_build_status()
        elif parsed_path.path.startswith('/api/download/'):
            self.handle_download(parsed_path.path)
        else:
            # Serve static files
            super().do_GET()

    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/api/build-iso':
            self.handle_build_iso()
        else:
            self.send_error(HTTPStatus.NOT_FOUND, "Endpoint not found")

    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS"""
        self.send_response(HTTPStatus.OK)
        self.send_cors_headers()
        self.end_headers()

    def send_cors_headers(self):
        """Send CORS headers"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def handle_build_iso(self):
        """Handle ISO build request"""
        try:
            # Read request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            config = json.loads(post_data.decode('utf-8'))

            # Validate configuration
            if not validate_config(config):
                self.send_json_response({
                    'success': False,
                    'error': 'Invalid configuration'
                }, HTTPStatus.BAD_REQUEST)
                return

            # Generate build ID
            build_id = str(uuid.uuid4())

            # Start build in background thread
            build_thread = threading.Thread(
                target=start_build_process,
                args=(build_id, config)
            )
            build_thread.daemon = True
            build_thread.start()

            # Return build ID
            self.send_json_response({
                'success': True,
                'build_id': build_id,
                'message': 'Build started successfully'
            })

        except json.JSONDecodeError:
            self.send_json_response({
                'success': False,
                'error': 'Invalid JSON data'
            }, HTTPStatus.BAD_REQUEST)
        except Exception as e:
            print(f"Error starting build: {e}")
            self.send_json_response({
                'success': False,
                'error': str(e)
            }, HTTPStatus.INTERNAL_SERVER_ERROR)

    def handle_build_status(self):
        """Handle build status requests"""
        try:
            # Extract build ID from query parameters
            parsed_path = urlparse(self.path)
            query_params = parse_qs(parsed_path.query)
            build_id = query_params.get('id', [None])[0]

            if not build_id or build_id not in active_builds:
                self.send_json_response({
                    'status': 'not_found',
                    'error': 'Build not found'
                }, HTTPStatus.NOT_FOUND)
                return

            build_info = active_builds[build_id]
            with build_lock:
                status_data = {
                    'status': build_info['status'],
                    'progress': build_info['progress'],
                    'message': build_info['message'],
                    'logs': build_info['logs'][-20:]  # Last 20 log entries
                }

                if build_info['status'] == 'completed':
                    status_data['filename'] = build_info.get('filename')
                elif build_info['status'] == 'failed':
                    status_data['error'] = build_info.get('error')

            self.send_json_response(status_data)

        except Exception as e:
            print(f"Error getting build status: {e}")
            self.send_json_response({
                'status': 'error',
                'error': str(e)
            }, HTTPStatus.INTERNAL_SERVER_ERROR)

    def handle_download(self, path):
        """Handle ISO download requests"""
        try:
            # Extract filename from path
            filename = path.replace('/api/download/', '')

            # Security check - only allow .iso files
            if not filename.endswith('.iso'):
                self.send_error(HTTPStatus.FORBIDDEN, "Invalid file type")
                return

            iso_path = os.path.join(BUILD_DIR, filename)

            if not os.path.exists(iso_path):
                self.send_error(HTTPStatus.NOT_FOUND, "File not found")
                return

            # Send file
            self.send_response(HTTPStatus.OK)
            self.send_cors_headers()
            self.send_header('Content-Type', 'application/octet-stream')
            self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
            self.send_header('Content-Length', os.path.getsize(iso_path))
            self.end_headers()

            with open(iso_path, 'rb') as f:
                shutil.copyfileobj(f, self.wfile)

        except Exception as e:
            print(f"Error downloading file: {e}")
            self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR, str(e))

    def send_json_response(self, data, status=HTTPStatus.OK):
        """Send JSON response"""
        self.send_response(status)
        self.send_cors_headers()
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def log_message(self, format, *args):
        """Override to reduce logging noise"""
        # Only log errors
        if args and len(args) > 1 and args[1] != '200':
            super().log_message(format, *args)


def validate_config(config):
    """Validate build configuration"""
    required_fields = ['wallet', 'worker_name', 'pool_url', 'power_limit', 'core_offset', 'mem_offset']

    # Check required fields
    for field in required_fields:
        if field not in config:
            return False

    # Validate wallet address
    if not config['wallet'].startswith('ak_'):
        return False

    # Validate pool URL
    if not config['pool_url'].startswith('stratum+tcp://'):
        return False

    # Validate numeric fields
    numeric_fields = ['power_limit', 'core_offset', 'mem_offset']
    for field in numeric_fields:
        try:
            int(config[field])
        except (ValueError, TypeError):
            return False

    # Validate power limit range
    if not (100 <= config['power_limit'] <= 300):
        return False

    return True


def start_build_process(build_id, config):
    """Start the ISO build process"""
    with build_lock:
        active_builds[build_id] = {
            'status': 'running',
            'progress': 0,
            'message': 'Initializing build...',
            'logs': ['Build process started'],
            'start_time': datetime.now().isoformat()
        }

    try:
        # Create temporary config file
        temp_config = create_temp_config(config)

        # Run build process
        success, iso_path = run_build_script(build_id, temp_config)

        with build_lock:
            if success:
                filename = os.path.basename(iso_path)
                active_builds[build_id].update({
                    'status': 'completed',
                    'progress': 100,
                    'message': 'Build completed successfully',
                    'filename': filename
                })
                active_builds[build_id]['logs'].append(f'Build completed: {filename}')
            else:
                active_builds[build_id].update({
                    'status': 'failed',
                    'progress': 0,
                    'message': 'Build failed',
                    'error': 'Build script failed'
                })

        # Clean up temp config
        if os.path.exists(temp_config):
            os.unlink(temp_config)

    except Exception as e:
        print(f"Build process error: {e}")
        with build_lock:
            active_builds[build_id].update({
                'status': 'failed',
                'progress': 0,
                'message': 'Build failed',
                'error': str(e)
            })


def create_temp_config(config):
    """Create temporary configuration file"""
    # Read base config
    with open(CONFIG_FILE, 'r') as f:
        base_config = json.load(f)

    # Update with user config
    base_config.update({
        'wallet': config['wallet'],
        'worker_name': config['worker_name'],
        'pool': {
            'url': config['pool_url'],
            'backup_url': 'stratum+tcp://ae.f2pool.com:4040'  # Default backup
        },
        'gpu': {
            'device_id': 0,
            'power_limit': config['power_limit'],
            'core_offset': config['core_offset'],
            'mem_offset': config['mem_offset']
        }
    })

    # Create temp file
    temp_fd, temp_path = tempfile.mkstemp(suffix='.json')
    try:
        with os.fdopen(temp_fd, 'w') as f:
            json.dump(base_config, f, indent=2)
    except:
        os.unlink(temp_path)
        raise

    return temp_path


def run_build_script(build_id, config_file):
    """Run the ISO build script"""
    build_script = os.path.join(PROJECT_ROOT, 'build-iso.sh')

    if not os.path.exists(build_script):
        raise FileNotFoundError(f"Build script not found: {build_script}")

    # Set environment variable for config file
    env = os.environ.copy()
    env['CUSTOM_CONFIG'] = config_file

    # Run build script
    process = subprocess.Popen(
        ['sudo', build_script],
        cwd=PROJECT_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=env
    )

    # Monitor progress
    progress_steps = [
        ('Downloading Ubuntu ISO', 10),
        ('Extracting ISO', 20),
        ('Setting up chroot', 30),
        ('Installing packages', 60),
        ('Rebuilding filesystem', 80),
        ('Creating ISO', 95),
        ('Build complete', 100)
    ]

    current_step = 0

    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break

        if output:
            line = output.strip()
            print(f"Build {build_id}: {line}")

            with build_lock:
                if build_id in active_builds:
                    active_builds[build_id]['logs'].append(line)

                    # Update progress based on output
                    for step_text, step_progress in progress_steps:
                        if step_text.lower() in line.lower():
                            active_builds[build_id]['progress'] = step_progress
                            active_builds[build_id]['message'] = step_text
                            break

    return_code = process.poll()
    success = return_code == 0

    if success:
        # Find the created ISO file
        iso_pattern = os.path.join(BUILD_DIR, 'a5000mine.iso')
        if os.path.exists(iso_pattern):
            return True, iso_pattern

    return False, None


def cleanup_old_builds():
    """Clean up old completed/failed builds"""
    cutoff_time = time.time() - (24 * 60 * 60)  # 24 hours ago

    with build_lock:
        to_remove = []
        for build_id, build_info in active_builds.items():
            if build_info['status'] in ['completed', 'failed']:
                # Parse start time
                try:
                    start_time = datetime.fromisoformat(build_info['start_time'])
                    if start_time.timestamp() < cutoff_time:
                        to_remove.append(build_id)
                except:
                    # If we can't parse time, remove it anyway
                    to_remove.append(build_id)

        for build_id in to_remove:
            del active_builds[build_id]


def main():
    """Start the ISO builder server"""
    # Create build directory if it doesn't exist
    os.makedirs(BUILD_DIR, exist_ok=True)

    # Use port 8000 if not root, otherwise 3000
    port = 8000 if os.geteuid() != 0 else 3000
    server_address = ('', port)
    httpd = HTTPServer(server_address, ISOBuilderHandler)

    print("A5000mine ISO Builder Server")
    print(f"Listening on port {port}")
    print(f"Access at: http://localhost:{port}")
    print("Press Ctrl+C to stop")

    # Start cleanup thread
    cleanup_thread = threading.Thread(target=cleanup_thread_func, daemon=True)
    cleanup_thread.start()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.shutdown()


def cleanup_thread_func():
    """Background thread for cleaning up old builds"""
    while True:
        time.sleep(60 * 60)  # Run every hour
        cleanup_old_builds()


if __name__ == "__main__":
    main()
