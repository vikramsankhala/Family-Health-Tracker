"""
Device Integration Module for Apple Watch and Garmin
Handles OAuth, API calls, and data synchronization
"""
import requests
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import database

# Apple HealthKit Configuration
APPLE_CLIENT_ID = os.environ.get('APPLE_CLIENT_ID', '')
APPLE_CLIENT_SECRET = os.environ.get('APPLE_CLIENT_SECRET', '')
APPLE_REDIRECT_URI = os.environ.get('APPLE_REDIRECT_URI', 'https://your-app.railway.app/api/devices/apple/callback')

# Garmin Connect Configuration
GARMIN_CONSUMER_KEY = os.environ.get('GARMIN_CONSUMER_KEY', '')
GARMIN_CONSUMER_SECRET = os.environ.get('GARMIN_CONSUMER_SECRET', '')
GARMIN_REDIRECT_URI = os.environ.get('GARMIN_REDIRECT_URI', 'https://your-app.railway.app/api/devices/garmin/callback')

class AppleHealthKitIntegration:
    """Apple HealthKit API Integration"""
    
    def __init__(self):
        self.base_url = "https://api.apple.com/health"
        self.auth_url = "https://appleid.apple.com/auth/authorize"
        self.token_url = "https://appleid.apple.com/auth/token"
    
    def get_authorization_url(self, state: str) -> str:
        """Generate OAuth authorization URL"""
        params = {
            'client_id': APPLE_CLIENT_ID,
            'redirect_uri': APPLE_REDIRECT_URI,
            'response_type': 'code',
            'scope': 'health.read',
            'state': state
        }
        return f"{self.auth_url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
    
    def exchange_code_for_token(self, code: str) -> Dict:
        """Exchange authorization code for access token"""
        try:
            # Note: Apple HealthKit requires special handling
            # This is a simplified version - actual implementation requires
            # proper OAuth 2.0 flow with client secret generation
            response = requests.post(self.token_url, data={
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': APPLE_REDIRECT_URI,
                'client_id': APPLE_CLIENT_ID,
                'client_secret': APPLE_CLIENT_SECRET
            })
            
            if response.status_code == 200:
                return response.json()
            else:
                return {'error': f'Token exchange failed: {response.text}'}
        except Exception as e:
            return {'error': str(e)}
    
    def get_health_data(self, access_token: str, start_date: str, end_date: str) -> Dict:
        """Fetch health data from Apple HealthKit"""
        try:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Apple HealthKit API endpoints
            # Note: Actual endpoints may vary based on Apple's API documentation
            endpoints = {
                'steps': f'{self.base_url}/v1/steps',
                'heart_rate': f'{self.base_url}/v1/heartrate',
                'sleep': f'{self.base_url}/v1/sleep',
                'workouts': f'{self.base_url}/v1/workouts'
            }
            
            data = {}
            for metric, url in endpoints.items():
                try:
                    response = requests.get(url, headers=headers, params={
                        'start_date': start_date,
                        'end_date': end_date
                    })
                    if response.status_code == 200:
                        data[metric] = response.json()
                except:
                    continue
            
            return {'success': True, 'data': data}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def sync_to_database(self, device_id: int, access_token: str, days: int = 7) -> Dict:
        """Sync Apple HealthKit data to database"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            health_data = self.get_health_data(
                access_token,
                start_date.isoformat(),
                end_date.isoformat()
            )
            
            if not health_data.get('success'):
                return health_data
            
            records_synced = 0
            
            with database.get_db() as conn:
                cursor = conn.cursor()
                
                # Sync steps and activity
                if 'steps' in health_data['data']:
                    for record in health_data['data']['steps'].get('data', []):
                        date = record.get('date', datetime.now().date().isoformat())
                        steps = record.get('value', 0)
                        
                        # Update health_tracker_data
                        cursor.execute('''
                            INSERT OR REPLACE INTO health_tracker_data 
                            (date, exercise_minutes, notes, created_at)
                            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                        ''', (date, steps // 20, f'Apple Watch: {steps} steps'))
                        records_synced += 1
                
                # Sync heart rate
                if 'heart_rate' in health_data['data']:
                    for record in health_data['data']['heart_rate'].get('data', []):
                        date = record.get('date', datetime.now().date().isoformat())
                        hr = record.get('value', 0)
                        
                        cursor.execute('''
                            INSERT OR REPLACE INTO health_tracker_data 
                            (date, notes, created_at)
                            VALUES (?, ?, CURRENT_TIMESTAMP)
                        ''', (date, f'Apple Watch: Heart Rate {hr} bpm'))
                        records_synced += 1
                
                # Sync sleep
                if 'sleep' in health_data['data']:
                    for record in health_data['data']['sleep'].get('data', []):
                        date = record.get('date', datetime.now().date().isoformat())
                        sleep_hours = record.get('hours', 0)
                        
                        cursor.execute('''
                            INSERT OR REPLACE INTO health_tracker_data 
                            (date, sleep_hours, created_at)
                            VALUES (?, ?, CURRENT_TIMESTAMP)
                        ''', (date, sleep_hours))
                        records_synced += 1
                
                # Update device sync status
                cursor.execute('''
                    UPDATE device_connections 
                    SET last_sync_at = CURRENT_TIMESTAMP, 
                        sync_status = 'completed',
                        sync_error = NULL
                    WHERE id = ?
                ''', (device_id,))
                
                # Log sync
                cursor.execute('''
                    INSERT INTO device_sync_log 
                    (device_connection_id, sync_type, records_synced, sync_started_at, sync_completed_at, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (device_id, 'apple_healthkit', records_synced, start_date.isoformat(), datetime.now().isoformat(), 'completed'))
            
            return {'success': True, 'records_synced': records_synced}
        except Exception as e:
            return {'success': False, 'error': str(e)}


class GarminConnectIntegration:
    """Garmin Connect API Integration"""
    
    def __init__(self):
        self.base_url = "https://connectapi.garmin.com"
        self.auth_url = "https://connect.garmin.com/oauth/authorize"
        self.token_url = "https://connect.garmin.com/oauth/token"
        self.request_token_url = "https://connect.garmin.com/oauth/request_token"
        self.access_token_url = "https://connect.garmin.com/oauth/access_token"
    
    def get_authorization_url(self, state: str) -> str:
        """Generate OAuth authorization URL"""
        # Garmin uses OAuth 1.0a
        try:
            # Step 1: Get request token
            response = requests.post(self.request_token_url, auth=requests.auth.HTTPBasicAuth(
                GARMIN_CONSUMER_KEY, GARMIN_CONSUMER_SECRET
            ), data={
                'oauth_callback': GARMIN_REDIRECT_URI
            })
            
            if response.status_code == 200:
                # Parse OAuth 1.0a response
                params = dict(item.split('=') for item in response.text.split('&'))
                oauth_token = params.get('oauth_token')
                oauth_token_secret = params.get('oauth_token_secret')
                
                # Store tokens temporarily (in production, use session storage)
                # For now, return authorization URL
                return f"{self.auth_url}?oauth_token={oauth_token}"
            else:
                return None
        except Exception as e:
            return None
    
    def exchange_token(self, oauth_token: str, oauth_verifier: str) -> Dict:
        """Exchange request token for access token"""
        try:
            # OAuth 1.0a flow
            response = requests.post(self.access_token_url, auth=requests.auth.HTTPBasicAuth(
                GARMIN_CONSUMER_KEY, GARMIN_CONSUMER_SECRET
            ), data={
                'oauth_token': oauth_token,
                'oauth_verifier': oauth_verifier
            })
            
            if response.status_code == 200:
                params = dict(item.split('=') for item in response.text.split('&'))
                return {
                    'access_token': params.get('oauth_token'),
                    'access_token_secret': params.get('oauth_token_secret')
                }
            else:
                return {'error': f'Token exchange failed: {response.text}'}
        except Exception as e:
            return {'error': str(e)}
    
    def get_health_data(self, access_token: str, access_token_secret: str, start_date: str, end_date: str) -> Dict:
        """Fetch health data from Garmin Connect"""
        try:
            # Garmin Connect API endpoints
            endpoints = {
                'activities': f'{self.base_url}/wellness-service/wellness/dailySummary',
                'steps': f'{self.base_url}/wellness-service/wellness/dailySteps',
                'heart_rate': f'{self.base_url}/wellness-service/wellness/dailyHeartRate',
                'sleep': f'{self.base_url}/wellness-service/wellness/dailySleep'
            }
            
            data = {}
            for metric, url in endpoints.items():
                try:
                    # OAuth 1.0a signing required
                    response = requests.get(url, auth=requests.auth.HTTPBasicAuth(
                        access_token, access_token_secret
                    ), params={
                        'startDate': start_date,
                        'endDate': end_date
                    })
                    if response.status_code == 200:
                        data[metric] = response.json()
                except:
                    continue
            
            return {'success': True, 'data': data}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def sync_to_database(self, device_id: int, access_token: str, access_token_secret: str, days: int = 7) -> Dict:
        """Sync Garmin Connect data to database"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            health_data = self.get_health_data(
                access_token,
                access_token_secret,
                start_date.isoformat(),
                end_date.isoformat()
            )
            
            if not health_data.get('success'):
                return health_data
            
            records_synced = 0
            
            with database.get_db() as conn:
                cursor = conn.cursor()
                
                # Sync activities
                if 'activities' in health_data['data']:
                    for record in health_data['data']['activities']:
                        date = record.get('calendarDate', datetime.now().date().isoformat())
                        steps = record.get('steps', 0)
                        distance = record.get('distanceInMeters', 0)
                        calories = record.get('totalKilocalories', 0)
                        
                        cursor.execute('''
                            INSERT OR REPLACE INTO health_tracker_data 
                            (date, exercise_minutes, notes, created_at)
                            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                        ''', (date, steps // 20, f'Garmin: {steps} steps, {distance}m, {calories} kcal'))
                        records_synced += 1
                
                # Sync heart rate
                if 'heart_rate' in health_data['data']:
                    for record in health_data['data']['heart_rate']:
                        date = record.get('calendarDate', datetime.now().date().isoformat())
                        avg_hr = record.get('restingHeartRate', 0)
                        max_hr = record.get('maxHeartRate', 0)
                        
                        cursor.execute('''
                            INSERT OR REPLACE INTO health_tracker_data 
                            (date, notes, created_at)
                            VALUES (?, ?, CURRENT_TIMESTAMP)
                        ''', (date, f'Garmin: HR avg {avg_hr}, max {max_hr} bpm'))
                        records_synced += 1
                
                # Sync sleep
                if 'sleep' in health_data['data']:
                    for record in health_data['data']['sleep']:
                        date = record.get('calendarDate', datetime.now().date().isoformat())
                        sleep_hours = record.get('sleepTimeSeconds', 0) / 3600
                        
                        cursor.execute('''
                            INSERT OR REPLACE INTO health_tracker_data 
                            (date, sleep_hours, created_at)
                            VALUES (?, ?, CURRENT_TIMESTAMP)
                        ''', (date, sleep_hours))
                        records_synced += 1
                
                # Update device sync status
                cursor.execute('''
                    UPDATE device_connections 
                    SET last_sync_at = CURRENT_TIMESTAMP, 
                        sync_status = 'completed',
                        sync_error = NULL
                    WHERE id = ?
                ''', (device_id,))
                
                # Log sync
                cursor.execute('''
                    INSERT INTO device_sync_log 
                    (device_connection_id, sync_type, records_synced, sync_started_at, sync_completed_at, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (device_id, 'garmin_connect', records_synced, start_date.isoformat(), datetime.now().isoformat(), 'completed'))
            
            return {'success': True, 'records_synced': records_synced}
        except Exception as e:
            return {'success': False, 'error': str(e)}


def get_device_integration(device_type: str):
    """Factory function to get device integration instance"""
    if device_type.lower() == 'apple_watch' or device_type.lower() == 'apple':
        return AppleHealthKitIntegration()
    elif device_type.lower() == 'garmin':
        return GarminConnectIntegration()
    else:
        raise ValueError(f"Unsupported device type: {device_type}")

