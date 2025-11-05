#!/usr/bin/env python3
"""
Discord Data Scraper - Web Interface
Flask-based web GUI similar to Apify
"""

from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import json
import os
import threading
from datetime import datetime
from discord_scraper import DiscordScraper
from config_schema import ConfigSchema
from state_manager import StateManager

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'discord-scraper-secret-key-change-in-production'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Global variables for scraping state
scraping_jobs = {}
job_id_counter = 0


class WebScraperProgress:
    """Progress tracker for web interface"""

    def __init__(self, job_id, socketio):
        self.job_id = job_id
        self.socketio = socketio
        self.total_scraped = 0
        self.status = "running"
        self.messages = []

    def log(self, message, level="info"):
        """Log a message"""
        log_entry = {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "level": level,
            "message": message
        }
        self.messages.append(log_entry)
        self.socketio.emit('log_message', {
            'job_id': self.job_id,
            'log': log_entry
        })

    def update_progress(self, scraped_count):
        """Update progress"""
        self.total_scraped = scraped_count
        self.socketio.emit('progress_update', {
            'job_id': self.job_id,
            'scraped': scraped_count,
            'status': self.status
        })

    def set_status(self, status):
        """Set status"""
        self.status = status
        self.socketio.emit('status_update', {
            'job_id': self.job_id,
            'status': status
        })


def run_scraping_job(job_id, config, token, timeout=None):
    """
    Run scraping job in background thread

    Args:
        job_id: Job identifier
        config: Scraping configuration
        token: Discord token
        timeout: Optional timeout in seconds (None for no timeout)
    """
    global scraping_jobs

    job = scraping_jobs[job_id]
    progress = WebScraperProgress(job_id, socketio)

    try:
        progress.log("Starting Discord scraper...")
        progress.set_status("running")

        # Get configuration
        action = config["action"]
        min_delay = config.get("minDelay", 1.0)
        max_delay = config.get("maxDelay", 3.0)

        # Create scraper
        scraper = DiscordScraper(token=token, min_delay=min_delay, max_delay=max_delay)

        if action == "scrapeMessages":
            params = config["scrapeMessages"]
            channel_url = params["channelUrl"]
            guild_id, channel_id = DiscordScraper.parse_channel_url(channel_url)

            progress.log(f"Scraping messages from channel {channel_id}")

            # Get channel info
            channel_info = scraper.get_channel_info(channel_id)
            if channel_info:
                progress.log(f"Channel: {channel_info.get('name', 'Unknown')}")

            # Scrape messages
            messages = scraper.scrape_messages(
                channel_id=channel_id,
                limit=params.get("limit"),
                before=params.get("before"),
                after=params.get("after")
            )

            progress.update_progress(len(messages))
            progress.log(f"Scraped {len(messages)} messages successfully", "success")

            # Save results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"messages_{channel_id}_{timestamp}.json"
            scraper.save_to_json(messages, filename)

            job['result'] = messages
            job['output_file'] = filename
            job['total_items'] = len(messages)

        elif action == "scrapeChannelMembers":
            params = config["scrapeChannelMembers"]
            channel_url = params["channelUrl"]
            guild_id, channel_id = DiscordScraper.parse_channel_url(channel_url)

            progress.log(f"Scraping members from guild {guild_id}")

            # Get guild info
            guild_info = scraper.get_guild_info(guild_id)
            if guild_info:
                progress.log(f"Guild: {guild_info.get('name', 'Unknown')}")

            # Scrape members
            members = scraper.scrape_guild_members(
                guild_id=guild_id,
                limit=params.get("limit")
            )

            progress.update_progress(len(members))
            progress.log(f"Scraped {len(members)} members successfully", "success")

            # Save results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"members_{guild_id}_{timestamp}.json"
            scraper.save_to_json(members, filename)

            job['result'] = members
            job['output_file'] = filename
            job['total_items'] = len(members)

        progress.set_status("completed")
        progress.log("Scraping completed successfully!", "success")

    except Exception as e:
        progress.log(f"Error: {str(e)}", "error")
        progress.set_status("failed")
        job['error'] = str(e)


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/results')
def results():
    """Results page"""
    return render_template('results.html')


@app.route('/api/start-scraping', methods=['POST'])
def start_scraping():
    """Start a new scraping job"""
    global job_id_counter, scraping_jobs

    try:
        data = request.json

        # Validate required fields
        if 'token' not in data:
            return jsonify({'error': 'Discord token is required'}), 400

        if 'action' not in data:
            return jsonify({'error': 'Action is required'}), 400

        # Build configuration
        config = {
            "action": data['action'],
            "minDelay": float(data.get('minDelay', 1.0)),
            "maxDelay": float(data.get('maxDelay', 3.0))
        }

        if data['action'] == 'scrapeMessages':
            config['scrapeMessages'] = {
                "channelUrl": data.get('channelUrl', ''),
                "limit": int(data['limit']) if data.get('limit') and data['limit'] != '' else None,
                "before": data.get('before') if data.get('before') else None,
                "after": data.get('after') if data.get('after') else None
            }
        elif data['action'] == 'scrapeChannelMembers':
            config['scrapeChannelMembers'] = {
                "channelUrl": data.get('channelUrl', ''),
                "limit": int(data['limit']) if data.get('limit') and data['limit'] != '' else None
            }

        # Validate configuration
        ConfigSchema.validate_config(config)

        # Create job
        job_id_counter += 1
        job_id = job_id_counter

        scraping_jobs[job_id] = {
            'id': job_id,
            'status': 'queued',
            'config': config,
            'created_at': datetime.now().isoformat(),
            'result': None,
            'output_file': None,
            'total_items': 0
        }

        # Get timeout setting
        timeout = None
        if data.get('timeout') and data['timeout'] != '':
            timeout = int(data['timeout'])

        # Start scraping in background thread
        thread = threading.Thread(
            target=run_scraping_job,
            args=(job_id, config, data['token'], timeout)
        )
        thread.daemon = True
        thread.start()

        return jsonify({
            'success': True,
            'job_id': job_id,
            'message': 'Scraping job started'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/job/<int:job_id>')
def get_job_status(job_id):
    """Get job status"""
    if job_id not in scraping_jobs:
        return jsonify({'error': 'Job not found'}), 404

    job = scraping_jobs[job_id]
    return jsonify({
        'id': job['id'],
        'status': job['status'],
        'total_items': job['total_items'],
        'output_file': job['output_file'],
        'created_at': job['created_at']
    })


@app.route('/api/jobs')
def get_all_jobs():
    """Get all jobs"""
    jobs_list = []
    for job_id, job in scraping_jobs.items():
        jobs_list.append({
            'id': job['id'],
            'status': job['status'],
            'total_items': job['total_items'],
            'output_file': job['output_file'],
            'created_at': job['created_at'],
            'action': job['config']['action']
        })

    return jsonify({'jobs': jobs_list})


@app.route('/api/download/<int:job_id>')
def download_results(job_id):
    """Download job results"""
    if job_id not in scraping_jobs:
        return jsonify({'error': 'Job not found'}), 404

    job = scraping_jobs[job_id]
    if not job['output_file']:
        return jsonify({'error': 'No results available'}), 404

    filepath = os.path.join('output', job['output_file'])
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404

    return send_file(filepath, as_attachment=True, download_name=job['output_file'])


@app.route('/api/view/<int:job_id>')
def view_results(job_id):
    """View job results"""
    if job_id not in scraping_jobs:
        return jsonify({'error': 'Job not found'}), 404

    job = scraping_jobs[job_id]
    if not job['result']:
        return jsonify({'error': 'No results available'}), 404

    # Return limited results for preview (first 100 items)
    preview_results = job['result'][:100] if len(job['result']) > 100 else job['result']

    return jsonify({
        'total': len(job['result']),
        'preview_count': len(preview_results),
        'results': preview_results
    })


@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')


if __name__ == '__main__':
    # Create output directory
    os.makedirs('output', exist_ok=True)

    # Run the app
    print("=" * 60)
    print("Discord Data Scraper - Web Interface")
    print("=" * 60)
    print()
    print("Starting web server...")
    print("Open your browser and navigate to: http://localhost:5000")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 60)

    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
