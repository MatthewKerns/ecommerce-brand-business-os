#!/usr/bin/env python3
"""
Simple Flask API endpoint for video generation
Connects the frontend to our video generation architecture
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
from typing import Dict, Any

# Import our video generation architecture
from infrastructure.di import create_video_generation_service
from domain.video_generation import VideoQuality

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

# Initialize video generation service
video_service = None

def get_video_service():
    """Get or create video generation service"""
    global video_service
    if video_service is None:
        video_service = create_video_generation_service()
    return video_service

@app.route('/api/video/generate', methods=['POST'])
def generate_video():
    """Generate video endpoint matching frontend expectations"""
    try:
        data = request.json

        # Extract parameters from request
        raw_script = data.get('raw_script', {})
        channel = data.get('channel', 'air')
        quality_str = data.get('quality', 'standard')
        provider_hint = data.get('provider_hint', 'mock')
        options = data.get('options', {})

        # Map quality string to enum
        quality_map = {
            'low': VideoQuality.LOW,
            'standard': VideoQuality.STANDARD,
            'high': VideoQuality.HIGH,
            'ultra': VideoQuality.ULTRA
        }
        quality = quality_map.get(quality_str, VideoQuality.STANDARD)

        # Get video service
        service = get_video_service()

        # Run async generation in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        result = loop.run_until_complete(
            service.generate_video(
                raw_script=raw_script,
                channel=channel,
                quality=quality,
                provider_hint=provider_hint,
                options=options
            )
        )

        # Convert result to JSON-serializable format
        response = {
            'id': result.id,
            'status': result.status.value,
            'provider_id': result.provider_id,
            'url': result.url,
            'thumbnail_url': result.thumbnail_url,
            'duration_seconds': result.duration_seconds,
            'metadata': result.metadata,
            'error_message': result.error_message
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'failed'
        }), 500

@app.route('/api/video/status', methods=['GET'])
def get_video_status():
    """Get video generation status"""
    try:
        video_id = request.args.get('id')
        provider = request.args.get('provider')

        if not video_id:
            return jsonify({'error': 'Video ID required'}), 400

        # Get video service
        service = get_video_service()

        # Run async status check in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        result = loop.run_until_complete(
            service.get_video_status(video_id, provider)
        )

        # Convert result to JSON-serializable format
        response = {
            'id': result.id,
            'status': result.status.value,
            'provider_id': result.provider_id,
            'url': result.url,
            'thumbnail_url': result.thumbnail_url,
            'duration_seconds': result.duration_seconds,
            'metadata': result.metadata,
            'error_message': result.error_message
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'failed'
        }), 500

@app.route('/api/video/providers', methods=['GET'])
def get_providers():
    """Get available video providers"""
    try:
        service = get_video_service()
        providers = service.get_available_providers()
        return jsonify(providers)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'video-generation-api',
        'architecture': 'plugin-based'
    })

if __name__ == '__main__':
    print("🎬 Video Generation API Server")
    print("=" * 50)
    print("Starting server on http://localhost:8000")
    print("Available endpoints:")
    print("  POST /api/video/generate - Generate video")
    print("  GET  /api/video/status   - Check video status")
    print("  GET  /api/video/providers - List providers")
    print("  GET  /health             - Health check")
    print("=" * 50)

    app.run(host='0.0.0.0', port=8000, debug=True)