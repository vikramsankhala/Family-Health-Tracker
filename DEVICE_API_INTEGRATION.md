# Device API Integration Guide - Apple Watch & Garmin

## Overview

This application supports automatic health data synchronization from Apple Watch and Garmin devices through their respective APIs.

## Supported Devices

### 🍎 Apple Watch
- **API**: Apple HealthKit API
- **Data Synced**: Steps, Heart Rate, Sleep, Workouts
- **OAuth**: OAuth 2.0
- **Update Frequency**: Real-time (via webhooks) or manual sync

### 🏃 Garmin
- **API**: Garmin Connect API
- **Data Synced**: Activities, Steps, Heart Rate, Sleep, Workouts
- **OAuth**: OAuth 1.0a
- **Update Frequency**: Manual sync or scheduled sync

## Setup Instructions

### 1. Apple Watch Integration

#### Prerequisites
- Apple Developer Account
- HealthKit API access
- OAuth credentials

#### Steps

1. **Create Apple Developer Account**
   - Go to https://developer.apple.com
   - Enroll in Apple Developer Program ($99/year)

2. **Create App ID**
   - Create a new App ID with HealthKit capability
   - Enable "HealthKit" in App Services

3. **Get OAuth Credentials**
   - Create OAuth Client ID and Secret
   - Set redirect URI: `https://your-app.railway.app/api/devices/apple/callback`

4. **Set Environment Variables**
   ```bash
   APPLE_CLIENT_ID=your_client_id
   APPLE_CLIENT_SECRET=your_client_secret
   APPLE_REDIRECT_URI=https://your-app.railway.app/api/devices/apple/callback
   ```

5. **Connect Device**
   - Login to the application
   - Go to "Device API Integration" section
   - Click "Connect Apple Watch"
   - Authorize the application
   - Device will be connected automatically

### 2. Garmin Integration

#### Prerequisites
- Garmin Developer Account
- Garmin Connect API access
- OAuth credentials

#### Steps

1. **Create Garmin Developer Account**
   - Go to https://developer.garmin.com
   - Sign up for free developer account

2. **Create Application**
   - Create a new application
   - Get Consumer Key and Consumer Secret
   - Set callback URL: `https://your-app.railway.app/api/devices/garmin/callback`

3. **Set Environment Variables**
   ```bash
   GARMIN_CONSUMER_KEY=your_consumer_key
   GARMIN_CONSUMER_SECRET=your_consumer_secret
   GARMIN_REDIRECT_URI=https://your-app.railway.app/api/devices/garmin/callback
   ```

4. **Connect Device**
   - Login to the application
   - Go to "Device API Integration" section
   - Click "Connect Garmin"
   - Authorize the application
   - Device will be connected automatically

## API Endpoints

### Get All Devices
```
GET /api/devices
```
Returns list of all connected devices.

### Connect Device
```
GET /api/devices/{device_type}/connect
```
Initiates OAuth flow. Returns authorization URL.

**Device Types**: `apple`, `apple_watch`, `garmin`

### OAuth Callbacks
```
GET /api/devices/apple/callback
GET /api/devices/garmin/callback
```
Handles OAuth callbacks and stores device connection.

### Sync Device
```
POST /api/devices/{device_id}/sync
Body: { "days": 7 }
```
Manually trigger device sync. Syncs last N days of data.

### Toggle Sync
```
PUT /api/devices/{device_id}/toggle
Body: { "sync_enabled": true }
```
Enable or disable automatic sync for a device.

### Disconnect Device
```
DELETE /api/devices/{device_id}
```
Disconnect and remove device connection.

## Data Synchronization

### Automatic Sync
- Devices sync automatically when connected
- Can be enabled/disabled per device
- Syncs last 7 days of data by default

### Manual Sync
- Click "Sync Now" button for any connected device
- Syncs last 7 days (configurable)
- Updates health tracker data automatically

### Sync Frequency
- **Apple Watch**: Real-time (if webhooks configured) or manual
- **Garmin**: Manual or scheduled (every 6 hours recommended)

## Data Mapping

### Apple Watch → Health Tracker
- **Steps** → Exercise Minutes (steps / 20)
- **Heart Rate** → Notes (HR value)
- **Sleep** → Sleep Hours
- **Workouts** → Exercise Minutes + Notes

### Garmin → Health Tracker
- **Steps** → Exercise Minutes (steps / 20)
- **Activities** → Exercise Minutes + Notes
- **Heart Rate** → Notes (avg/max HR)
- **Sleep** → Sleep Hours

## Database Schema

### device_connections
- `id`: Primary key
- `device_type`: apple_watch, garmin
- `device_name`: Display name
- `access_token`: OAuth access token
- `refresh_token`: OAuth refresh token
- `sync_enabled`: Boolean
- `last_sync_at`: Timestamp
- `sync_status`: pending, syncing, completed, error
- `sync_error`: Error message if sync failed

### device_sync_log
- `id`: Primary key
- `device_connection_id`: Foreign key
- `sync_type`: apple_healthkit, garmin_connect
- `records_synced`: Number of records
- `sync_started_at`: Timestamp
- `sync_completed_at`: Timestamp
- `status`: pending, completed, error

## Troubleshooting

### Connection Issues

**Problem**: OAuth callback fails
- **Solution**: Verify redirect URI matches exactly in provider settings
- **Solution**: Check environment variables are set correctly

**Problem**: Token exchange fails
- **Solution**: Verify client credentials are correct
- **Solution**: Check token expiration and refresh if needed

### Sync Issues

**Problem**: No data synced
- **Solution**: Check device has data for the date range
- **Solution**: Verify access token is valid
- **Solution**: Check sync logs for errors

**Problem**: Partial data sync
- **Solution**: Some APIs may have rate limits
- **Solution**: Try syncing smaller date ranges
- **Solution**: Check API documentation for limits

## Security Considerations

1. **OAuth Tokens**: Stored encrypted in database
2. **HTTPS Required**: All OAuth flows use HTTPS
3. **Token Refresh**: Tokens automatically refreshed when expired
4. **Access Control**: Only authenticated users can manage devices

## Cost Considerations

### Apple HealthKit
- **Developer Account**: $99/year
- **API Access**: Free (included)
- **Rate Limits**: Generous limits

### Garmin Connect
- **Developer Account**: Free
- **API Access**: Free
- **Rate Limits**: 1000 requests/day (free tier)

## Future Enhancements

1. **Webhook Support**: Real-time data sync via webhooks
2. **Scheduled Syncs**: Automatic periodic syncs
3. **More Devices**: Fitbit, Withings, etc.
4. **Data Visualization**: Charts and graphs for synced data
5. **Export**: Export synced data to CSV/Excel

## Support

For issues or questions:
1. Check sync logs in database
2. Review API documentation
3. Check device connection status
4. Verify OAuth credentials

## Deployment Notes

### Railway.app

1. **Set Environment Variables**:
   ```
   APPLE_CLIENT_ID=your_client_id
   APPLE_CLIENT_SECRET=your_client_secret
   APPLE_REDIRECT_URI=https://your-app.railway.app/api/devices/apple/callback
   GARMIN_CONSUMER_KEY=your_consumer_key
   GARMIN_CONSUMER_SECRET=your_consumer_secret
   GARMIN_REDIRECT_URI=https://your-app.railway.app/api/devices/garmin/callback
   ```

2. **Update Redirect URIs**:
   - Update redirect URIs in Apple/Garmin developer portals
   - Use your Railway app URL

3. **Deploy**:
   - Push code to GitHub
   - Railway auto-deploys
   - Test OAuth flows

### Local Development

1. **Use ngrok** for local OAuth callbacks:
   ```bash
   ngrok http 5000
   ```
   Use ngrok URL as redirect URI

2. **Set Environment Variables**:
   ```bash
   export APPLE_CLIENT_ID=your_client_id
   export APPLE_CLIENT_SECRET=your_client_secret
   export APPLE_REDIRECT_URI=http://your-ngrok-url.ngrok.io/api/devices/apple/callback
   ```

## API Rate Limits

### Apple HealthKit
- **Requests**: 1000/hour per user
- **Data Points**: Unlimited
- **Refresh**: Tokens valid for 1 hour

### Garmin Connect
- **Requests**: 1000/day (free tier)
- **Data Points**: Unlimited
- **Refresh**: Tokens don't expire

## Best Practices

1. **Sync Frequency**: Don't sync more than once per hour
2. **Date Ranges**: Sync last 7-30 days at a time
3. **Error Handling**: Always check sync status and errors
4. **Token Management**: Refresh tokens before expiration
5. **User Privacy**: Only sync data user has authorized

