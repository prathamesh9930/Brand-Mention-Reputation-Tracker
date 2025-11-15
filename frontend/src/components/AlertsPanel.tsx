import React from 'react'
import { AlertTriangle, CheckCircle, Clock, X } from 'lucide-react'

const AlertsPanel = ({ selectedBrandId, setSelectedBrandId }) => {
  // Mock alerts data for demo
  const mockAlerts = [
    {
      id: 1,
      brand_id: 1,
      alert_type: 'volume_spike',
      title: 'Mention Volume Spike Detected',
      description: 'Unusual spike in mentions: 15 mentions in the last hour (normal: 3.2)',
      severity: 'high',
      created_at: new Date().toISOString(),
      is_read: false,
      is_resolved: false
    },
    {
      id: 2,
      brand_id: 1,
      alert_type: 'negative_sentiment',
      title: 'Negative Sentiment Alert',
      description: 'Sentiment has dropped significantly. Current sentiment: -0.65',
      severity: 'critical',
      created_at: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
      is_read: true,
      is_resolved: false
    }
  ]

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical': return 'severity-critical'
      case 'high': return 'severity-high'  
      case 'medium': return 'severity-medium'
      default: return 'severity-low'
    }
  }

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'critical': return <AlertTriangle className="h-5 w-5 text-error-600" />
      case 'high': return <AlertTriangle className="h-5 w-5 text-warning-600" />
      default: return <Clock className="h-5 w-5 text-primary-600" />
    }
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Alerts</h1>
          <p className="mt-2 text-gray-600">
            Monitor critical events and anomalies in real-time
          </p>
        </div>
        
        <div className="mt-4 sm:mt-0">
          <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
            <div className="w-2 h-2 bg-green-400 rounded-full mr-2 animate-pulse"></div>
            System Active
          </span>
        </div>
      </div>

      {/* Alert Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-error-100 rounded-lg">
              <AlertTriangle className="h-6 w-6 text-error-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Critical Alerts</p>
              <p className="text-2xl font-semibold text-error-600">1</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-warning-100 rounded-lg">
              <AlertTriangle className="h-6 w-6 text-warning-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">High Priority</p>
              <p className="text-2xl font-semibold text-warning-600">1</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-primary-100 rounded-lg">
              <Clock className="h-6 w-6 text-primary-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Unread Alerts</p>
              <p className="text-2xl font-semibold text-primary-600">1</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-success-100 rounded-lg">
              <CheckCircle className="h-6 w-6 text-success-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Resolved Today</p>
              <p className="text-2xl font-semibold text-success-600">3</p>
            </div>
          </div>
        </div>
      </div>

      {/* Alerts List */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-semibold text-gray-900">Recent Alerts</h3>
          <div className="flex space-x-2">
            <button className="btn-secondary text-sm">
              Mark All Read
            </button>
            <button className="btn-primary text-sm">
              Filter
            </button>
          </div>
        </div>

        <div className="space-y-4">
          {mockAlerts.map((alert) => (
            <div 
              key={alert.id}
              className={`p-4 rounded-lg border-l-4 ${getSeverityColor(alert.severity)} ${
                !alert.is_read ? 'bg-gray-50' : ''
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0 mt-1">
                    {getSeverityIcon(alert.severity)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2 mb-1">
                      <h4 className="text-sm font-semibold text-gray-900">
                        {alert.title}
                      </h4>
                      {!alert.is_read && (
                        <span className="inline-block w-2 h-2 bg-primary-500 rounded-full"></span>
                      )}
                      <span className={`px-2 py-1 text-xs font-medium rounded-full capitalize ${getSeverityColor(alert.severity)}`}>
                        {alert.severity}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">
                      {alert.description}
                    </p>
                    <div className="flex items-center space-x-4 text-xs text-gray-500">
                      <span>{new Date(alert.created_at).toLocaleString()}</span>
                      <span className="capitalize">{alert.alert_type.replace('_', ' ')}</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-2 ml-4">
                  {!alert.is_resolved && (
                    <button className="btn-success text-xs py-1 px-2">
                      Resolve
                    </button>
                  )}
                  <button className="p-1 text-gray-400 hover:text-gray-600">
                    <X className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
          
          {mockAlerts.length === 0 && (
            <div className="text-center py-8">
              <CheckCircle className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-4 text-lg font-medium text-gray-900">All Clear!</h3>
              <p className="mt-2 text-gray-500">
                No active alerts. Your brands are performing well.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default AlertsPanel