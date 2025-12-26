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

# Fitbit Configuration
FITBIT_CLIENT_ID = os.environ.get('FITBIT_CLIENT_ID', '')
FITBIT_CLIENT_SECRET = os.environ.get('FITBIT_CLIENT_SECRET', '')
FITBIT_REDIRECT_URI = os.environ.get('FITBIT_REDIRECT_URI', 'https://your-app.railway.app/api/devices/fitbit/callback')

# Withings Configuration
WITHINGS_CLIENT_ID = os.environ.get('WITHINGS_CLIENT_ID', '')
WITHINGS_CLIENT_SECRET = os.environ.get('WITHINGS_CLIENT_SECRET', '')
WITHINGS_REDIRECT_URI = os.environ.get('WITHINGS_REDIRECT_URI', 'https://your-app.railway.app/api/devices/withings/callback')

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


class FitbitIntegration:
    """Fitbit API Integration"""
    
    def __init__(self):
        self.base_url = "https://api.fitbit.com/1"
        self.auth_url = "https://www.fitbit.com/oauth2/authorize"
        self.token_url = "https://api.fitbit.com/oauth2/token"
    
    def get_authorization_url(self, state: str) -> str:
        """Generate OAuth authorization URL"""
        params = {
            'client_id': FITBIT_CLIENT_ID,
            'redirect_uri': FITBIT_REDIRECT_URI,
            'response_type': 'code',
            'scope': 'activity heartrate sleep weight',
            'state': state
        }
        return f"{self.auth_url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
    
    def exchange_code_for_token(self, code: str) -> Dict:
        """Exchange authorization code for access token"""
        try:
            import base64
            auth_string = f"{FITBIT_CLIENT_ID}:{FITBIT_CLIENT_SECRET}"
            auth_bytes = auth_string.encode('ascii')
            auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
            
            response = requests.post(self.token_url, 
                headers={
                    'Authorization': f'Basic {auth_b64}',
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                data={
                    'grant_type': 'authorization_code',
                    'code': code,
                    'redirect_uri': FITBIT_REDIRECT_URI
                })
            
            if response.status_code == 200:
                return response.json()
            else:
                return {'error': f'Token exchange failed: {response.text}'}
        except Exception as e:
            return {'error': str(e)}
    
    def get_health_data(self, access_token: str, start_date: str, end_date: str) -> Dict:
        """Fetch health data from Fitbit"""
        try:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json'
            }
            
            endpoints = {
                'activities': f'{self.base_url}/user/-/activities/date/{start_date}.json',
                'heart_rate': f'{self.base_url}/user/-/activities/heart/date/{start_date}/1d.json',
                'sleep': f'{self.base_url}/user/-/sleep/date/{start_date}.json',
                'weight': f'{self.base_url}/user/-/body/log/weight/date/{start_date}.json'
            }
            
            data = {}
            for metric, url in endpoints.items():
                try:
                    response = requests.get(url, headers=headers)
                    if response.status_code == 200:
                        data[metric] = response.json()
                except:
                    continue
            
            return {'success': True, 'data': data}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def sync_to_database(self, device_id: int, access_token: str, days: int = 7) -> Dict:
        """Sync Fitbit data to database"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            records_synced = 0
            
            with database.get_db() as conn:
                cursor = conn.cursor()
                
                # Sync each day
                for i in range(days):
                    sync_date = (start_date + timedelta(days=i)).strftime('%Y-%m-%d')
                    
                    health_data = self.get_health_data(access_token, sync_date, sync_date)
                    
                    if not health_data.get('success'):
                        continue
                    
                    # Sync activities (steps, distance, calories)
                    if 'activities' in health_data['data']:
                        activities = health_data['data']['activities']
                        summary = activities.get('summary', {})
                        steps = summary.get('steps', 0)
                        distance = summary.get('distances', [{}])[0].get('distance', 0)
                        calories = summary.get('caloriesOut', 0)
                        
                        if steps > 0:
                            cursor.execute('''
                                INSERT OR REPLACE INTO health_tracker_data 
                                (date, exercise_minutes, notes, created_at)
                                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                            ''', (sync_date, steps // 20, f'Fitbit: {steps} steps, {distance:.2f} km, {calories} kcal'))
                            records_synced += 1
                    
                    # Sync heart rate
                    if 'heart_rate' in health_data['data']:
                        hr_data = health_data['data']['heart_rate']
                        resting_hr = hr_data.get('activities-heart', [{}])[0].get('value', {}).get('restingHeartRate', 0)
                        
                        if resting_hr > 0:
                            cursor.execute('''
                                INSERT OR REPLACE INTO health_tracker_data 
                                (date, notes, created_at)
                                VALUES (?, ?, CURRENT_TIMESTAMP)
                            ''', (sync_date, f'Fitbit: Resting HR {resting_hr} bpm'))
                            records_synced += 1
                    
                    # Sync sleep
                    if 'sleep' in health_data['data']:
                        sleep_data = health_data['data']['sleep']
                        sleep_summary = sleep_data.get('summary', {})
                        total_sleep_minutes = sleep_summary.get('totalMinutesAsleep', 0)
                        sleep_hours = total_sleep_minutes / 60
                        
                        if sleep_hours > 0:
                            cursor.execute('''
                                INSERT OR REPLACE INTO health_tracker_data 
                                (date, sleep_hours, created_at)
                                VALUES (?, ?, CURRENT_TIMESTAMP)
                            ''', (sync_date, sleep_hours))
                            records_synced += 1
                    
                    # Sync weight
                    if 'weight' in health_data['data']:
                        weight_data = health_data['data']['weight']
                        weights = weight_data.get('weight', [])
                        if weights:
                            latest_weight = weights[-1].get('weight', 0)
                            if latest_weight > 0:
                                cursor.execute('''
                                    INSERT OR REPLACE INTO health_tracker_data 
                                    (date, weight, created_at)
                                    VALUES (?, ?, CURRENT_TIMESTAMP)
                                ''', (sync_date, latest_weight))
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
                ''', (device_id, 'fitbit', records_synced, start_date.isoformat(), datetime.now().isoformat(), 'completed'))
            
            return {'success': True, 'records_synced': records_synced}
        except Exception as e:
            return {'success': False, 'error': str(e)}


class WithingsIntegration:
    """Withings API Integration"""
    
    def __init__(self):
        self.base_url = "https://wbsapi.withings.net"
        self.auth_url = "https://account.withings.com/oauth2_user/authorize2"
        self.token_url = "https://wbsapi.withings.net/v2/oauth2"
    
    def get_authorization_url(self, state: str) -> str:
        """Generate OAuth authorization URL"""
        params = {
            'client_id': WITHINGS_CLIENT_ID,
            'redirect_uri': WITHINGS_REDIRECT_URI,
            'response_type': 'code',
            'scope': 'user.metrics user.activity user.sleepevents',
            'state': state
        }
        return f"{self.auth_url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
    
    def exchange_code_for_token(self, code: str) -> Dict:
        """Exchange authorization code for access token"""
        try:
            response = requests.post(self.token_url, data={
                'action': 'requesttoken',
                'grant_type': 'authorization_code',
                'client_id': WITHINGS_CLIENT_ID,
                'client_secret': WITHINGS_CLIENT_SECRET,
                'code': code,
                'redirect_uri': WITHINGS_REDIRECT_URI
            })
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 0:
                    body = result.get('body', {})
                    return {
                        'access_token': body.get('access_token'),
                        'refresh_token': body.get('refresh_token'),
                        'expires_in': body.get('expires_in', 10800),
                        'userid': body.get('userid')
                    }
                else:
                    return {'error': f'Token exchange failed: {result.get("error")}'}
            else:
                return {'error': f'Token exchange failed: {response.text}'}
        except Exception as e:
            return {'error': str(e)}
    
    def get_health_data(self, access_token: str, userid: str, start_date: str, end_date: str) -> Dict:
        """Fetch health data from Withings"""
        try:
            headers = {
                'Authorization': f'Bearer {access_token}'
            }
            
            # Convert dates to timestamps
            start_ts = int(datetime.fromisoformat(start_date).timestamp())
            end_ts = int(datetime.fromisoformat(end_date).timestamp())
            
            endpoints = {
                'weight': {
                    'url': f'{self.base_url}/measure',
                    'action': 'getmeas',
                    'params': {
                        'action': 'getmeas',
                        'userid': userid,
                        'startdate': start_ts,
                        'enddate': end_ts,
                        'category': 1  # Weight
                    }
                },
                'blood_pressure': {
                    'url': f'{self.base_url}/measure',
                    'action': 'getmeas',
                    'params': {
                        'action': 'getmeas',
                        'userid': userid,
                        'startdate': start_ts,
                        'enddate': end_ts,
                        'category': 2  # Blood Pressure
                    }
                },
                'activity': {
                    'url': f'{self.base_url}/v2/measure',
                    'action': 'getactivity',
                    'params': {
                        'action': 'getactivity',
                        'userid': userid,
                        'startdateymd': start_date.replace('-', ''),
                        'enddateymd': end_date.replace('-', '')
                    }
                },
                'sleep': {
                    'url': f'{self.base_url}/v2/sleep',
                    'action': 'getsummary',
                    'params': {
                        'action': 'getsummary',
                        'userid': userid,
                        'startdateymd': start_date.replace('-', ''),
                        'enddateymd': end_date.replace('-', '')
                    }
                }
            }
            
            data = {}
            for metric, config in endpoints.items():
                try:
                    response = requests.post(config['url'], headers=headers, data=config['params'])
                    if response.status_code == 200:
                        result = response.json()
                        if result.get('status') == 0:
                            data[metric] = result.get('body', {})
                except:
                    continue
            
            return {'success': True, 'data': data}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def sync_to_database(self, device_id: int, access_token: str, userid: str, days: int = 7) -> Dict:
        """Sync Withings data to database"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            health_data = self.get_health_data(
                access_token,
                userid,
                start_date.isoformat(),
                end_date.isoformat()
            )
            
            if not health_data.get('success'):
                return health_data
            
            records_synced = 0
            
            with database.get_db() as conn:
                cursor = conn.cursor()
                
                # Sync weight
                if 'weight' in health_data['data']:
                    measures = health_data['data']['weight'].get('measuregrps', [])
                    for measure_group in measures:
                        date = datetime.fromtimestamp(measure_group.get('date', 0)).date().isoformat()
                        measures_list = measure_group.get('measures', [])
                        for measure in measures_list:
                            if measure.get('type') == 1:  # Weight
                                weight_kg = measure.get('value', 0) * (10 ** measure.get('unit', 0))
                                if weight_kg > 0:
                                    cursor.execute('''
                                        INSERT OR REPLACE INTO health_tracker_data 
                                        (date, weight, created_at)
                                        VALUES (?, ?, CURRENT_TIMESTAMP)
                                    ''', (date, weight_kg))
                                    records_synced += 1
                
                # Sync blood pressure
                if 'blood_pressure' in health_data['data']:
                    measures = health_data['data']['blood_pressure'].get('measuregrps', [])
                    for measure_group in measures:
                        date = datetime.fromtimestamp(measure_group.get('date', 0)).date().isoformat()
                        measures_list = measure_group.get('measures', [])
                        systolic = 0
                        diastolic = 0
                        for measure in measures_list:
                            if measure.get('type') == 9:  # Systolic
                                systolic = measure.get('value', 0)
                            elif measure.get('type') == 10:  # Diastolic
                                diastolic = measure.get('value', 0)
                        
                        if systolic > 0 and diastolic > 0:
                            cursor.execute('''
                                INSERT OR REPLACE INTO health_tracker_data 
                                (date, blood_pressure, created_at)
                                VALUES (?, ?, CURRENT_TIMESTAMP)
                            ''', (date, f'{systolic}/{diastolic}'))
                            records_synced += 1
                
                # Sync activity
                if 'activity' in health_data['data']:
                    activities = health_data['data']['activity'].get('activities', [])
                    for activity in activities:
                        date = activity.get('date', '')
                        if date:
                            date_obj = datetime.strptime(date, '%Y%m%d').date().isoformat()
                            steps = activity.get('steps', 0)
                            distance = activity.get('distance', 0)
                            calories = activity.get('calories', 0)
                            
                            if steps > 0:
                                cursor.execute('''
                                    INSERT OR REPLACE INTO health_tracker_data 
                                    (date, exercise_minutes, notes, created_at)
                                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                                ''', (date_obj, steps // 20, f'Withings: {steps} steps, {distance}m, {calories} kcal'))
                                records_synced += 1
                
                # Sync sleep
                if 'sleep' in health_data['data']:
                    sleep_data = health_data['data']['sleep'].get('series', [])
                    for sleep_record in sleep_data:
                        date = sleep_record.get('date', '')
                        if date:
                            date_obj = datetime.strptime(date, '%Y%m%d').date().isoformat()
                            total_sleep_seconds = sleep_record.get('total_sleep_time', 0)
                            sleep_hours = total_sleep_seconds / 3600
                            
                            if sleep_hours > 0:
                                cursor.execute('''
                                    INSERT OR REPLACE INTO health_tracker_data 
                                    (date, sleep_hours, created_at)
                                    VALUES (?, ?, CURRENT_TIMESTAMP)
                                ''', (date_obj, sleep_hours))
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
                ''', (device_id, 'withings', records_synced, start_date.isoformat(), datetime.now().isoformat(), 'completed'))
            
            return {'success': True, 'records_synced': records_synced}
        except Exception as e:
            return {'success': False, 'error': str(e)}


def get_device_integration(device_type: str):
    """Factory function to get device integration instance"""
    device_type_lower = device_type.lower()
    if device_type_lower == 'apple_watch' or device_type_lower == 'apple':
        return AppleHealthKitIntegration()
    elif device_type_lower == 'garmin':
        return GarminConnectIntegration()
    elif device_type_lower == 'fitbit':
        return FitbitIntegration()
    elif device_type_lower == 'withings':
        return WithingsIntegration()
    else:
        raise ValueError(f"Unsupported device type: {device_type}")

