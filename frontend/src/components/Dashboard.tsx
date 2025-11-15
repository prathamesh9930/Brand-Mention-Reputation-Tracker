import React, { useState, useEffect } from 'react'
import { useQuery } from 'react-query'
import { TrendingUp, TrendingDown, AlertTriangle, MessageCircle, Eye, ThumbsUp, Share2 } from 'lucide-react'
import { brandApi, mentionsApi, sentimentApi, alertsApi } from '../services/api'
import { toast } from 'react-hot-toast'

interface DashboardProps {
  selectedBrandId: number | null
  setSelectedBrandId: (id: number | null) => void
}

const Dashboard: React.FC<DashboardProps> = ({ selectedBrandId, setSelectedBrandId }) => {
  const [timeRange, setTimeRange] = useState(24) // hours
  
  // Fetch brands
  const { data: brands, isLoading: brandsLoading } = useQuery('brands', brandApi.getAll)
  
  // Fetch brand stats
  const { data: brandStats } = useQuery(
    ['brandStats', selectedBrandId],
    () => selectedBrandId ? brandApi.getStats(selectedBrandId) : null,
    { enabled: !!selectedBrandId }
  )
  
  // Fetch mentions timeline
  const { data: mentionsTimeline } = useQuery(
    ['mentionsTimeline', selectedBrandId, timeRange],
    () => selectedBrandId ? mentionsApi.getTimeline(selectedBrandId, { hours: timeRange }) : null,
    { enabled: !!selectedBrandId }
  )
  
  // Fetch sentiment analysis
  const { data: sentimentData } = useQuery(
    ['sentimentAnalysis', selectedBrandId, timeRange],
    () => selectedBrandId ? sentimentApi.getAnalysis(selectedBrandId, { hours: timeRange }) : null,
    { enabled: !!selectedBrandId }
  )
  
  // Fetch recent mentions
  const { data: recentMentions } = useQuery(
    ['recentMentions', selectedBrandId],
    () => selectedBrandId ? mentionsApi.getByBrand(selectedBrandId, { limit: 10 }) : null,
    { enabled: !!selectedBrandId }
  )

  // Auto-select first brand if none selected
  useEffect(() => {
    if (brands?.data && brands.data.length > 0 && !selectedBrandId) {
      setSelectedBrandId(brands.data[0].id)
    }
  }, [brands, selectedBrandId, setSelectedBrandId])

  if (brandsLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (!brands?.data || brands.data.length === 0) {
    return (
      <div className="text-center py-12">
        <MessageCircle className="mx-auto h-12 w-12 text-gray-400" />
        <h3 className="mt-4 text-lg font-medium text-gray-900">No brands to monitor</h3>
        <p className="mt-2 text-gray-500">Get started by adding your first brand to monitor.</p>
        <button 
          onClick={() => window.location.href = '/brands'}
          className="btn-primary mt-4"
        >
          Add Your First Brand
        </button>
      </div>
    )
  }

  const selectedBrand = brands?.data.find(b => b.id === selectedBrandId)

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="mt-2 text-gray-600">
            Real-time brand monitoring and sentiment analysis
          </p>
        </div>
        
        <div className="mt-4 sm:mt-0 flex flex-col sm:flex-row gap-4">
          {/* Brand Selector */}
          <select
            value={selectedBrandId || ''}
            onChange={(e) => setSelectedBrandId(Number(e.target.value))}
            className="input-field"
          >
            <option value="">Select a brand</option>
            {brands?.data.map((brand) => (
              <option key={brand.id} value={brand.id}>
                {brand.name}
              </option>
            ))}
          </select>
          
          {/* Time Range Selector */}
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(Number(e.target.value))}
            className="input-field"
          >
            <option value={1}>Last Hour</option>
            <option value={24}>Last 24 Hours</option>
            <option value={168}>Last Week</option>
            <option value={720}>Last Month</option>
          </select>
        </div>
      </div>

      {selectedBrand && (
        <>
          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Total Mentions */}
            <div className="card">
              <div className="flex items-center">
                <div className="p-2 bg-primary-100 rounded-lg">
                  <MessageCircle className="h-6 w-6 text-primary-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Total Mentions</p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {brandStats?.data?.total_mentions || 0}
                  </p>
                </div>
              </div>
              <div className="mt-4 flex items-center text-sm">
                <span className="text-green-600 flex items-center">
                  <TrendingUp className="h-4 w-4 mr-1" />
                  {brandStats?.data?.today_mentions || 0} today
                </span>
              </div>
            </div>

            {/* Average Sentiment */}
            <div className="card">
              <div className="flex items-center">
                <div className={`p-2 rounded-lg ${
                  (brandStats?.data?.average_sentiment || 0) > 0 
                    ? 'bg-success-100' 
                    : (brandStats?.data?.average_sentiment || 0) < 0 
                      ? 'bg-error-100' 
                      : 'bg-gray-100'
                }`}>
                  {(brandStats?.data?.average_sentiment || 0) > 0 ? (
                    <ThumbsUp className="h-6 w-6 text-success-600" />
                  ) : (brandStats?.data?.average_sentiment || 0) < 0 ? (
                    <TrendingDown className="h-6 w-6 text-error-600" />
                  ) : (
                    <Eye className="h-6 w-6 text-gray-600" />
                  )}
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Avg Sentiment</p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {(brandStats?.data?.average_sentiment || 0).toFixed(2)}
                  </p>
                </div>
              </div>
              <div className="mt-4">
                <div className="flex items-center space-x-2">
                  {sentimentData?.data && (
                    <>
                      <span className="badge badge-positive">
                        {sentimentData.data.sentiment_breakdown.positive} +
                      </span>
                      <span className="badge badge-negative">
                        {sentimentData.data.sentiment_breakdown.negative} -
                      </span>
                      <span className="badge badge-neutral">
                        {sentimentData.data.sentiment_breakdown.neutral} ≈
                      </span>
                    </>
                  )}
                </div>
              </div>
            </div>

            {/* Week Mentions */}
            <div className="card">
              <div className="flex items-center">
                <div className="p-2 bg-warning-100 rounded-lg">
                  <TrendingUp className="h-6 w-6 text-warning-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">This Week</p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {brandStats?.data?.week_mentions || 0}
                  </p>
                </div>
              </div>
              <div className="mt-4 text-sm text-gray-500">
                Mentions in last 7 days
              </div>
            </div>

            {/* Active Alerts */}
            <div className="card">
              <div className="flex items-center">
                <div className="p-2 bg-error-100 rounded-lg">
                  <AlertTriangle className="h-6 w-6 text-error-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Active Alerts</p>
                  <p className="text-2xl font-semibold text-gray-900">0</p>
                </div>
              </div>
              <div className="mt-4 text-sm text-gray-500">
                No critical alerts
              </div>
            </div>
          </div>

          {/* Recent Mentions */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Mentions Feed */}
            <div className="card">
              <div className="card-header">
                <h3 className="text-lg font-semibold text-gray-900">Recent Mentions</h3>
                <span className="text-sm text-gray-500">
                  {recentMentions?.data?.length || 0} mentions
                </span>
              </div>
              
              <div className="space-y-4 max-h-96 overflow-y-auto custom-scrollbar">
                {recentMentions?.data?.map((mention, index) => (
                  <div key={mention.id} className="border-b border-gray-100 pb-4 last:border-b-0 last:pb-0">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <p className="text-sm text-gray-900 line-clamp-3">
                          {mention.content}
                        </p>
                        <div className="mt-2 flex items-center space-x-4 text-xs text-gray-500">
                          <span>@{mention.author}</span>
                          <span className="capitalize">{mention.source}</span>
                          <span>{new Date(mention.created_at).toLocaleDateString()}</span>
                        </div>
                      </div>
                      <div className="ml-4 flex flex-col items-end space-y-2">
                        {mention.sentiment_label && (
                          <span className={`badge ${
                            mention.sentiment_label === 'positive' 
                              ? 'badge-positive' 
                              : mention.sentiment_label === 'negative' 
                                ? 'badge-negative' 
                                : 'badge-neutral'
                          }`}>
                            {mention.sentiment_label}
                          </span>
                        )}
                        {(mention.likes > 0 || mention.shares > 0 || mention.comments > 0) && (
                          <div className="flex items-center space-x-2 text-xs text-gray-400">
                            {mention.likes > 0 && (
                              <span className="flex items-center">
                                <ThumbsUp className="h-3 w-3 mr-1" />
                                {mention.likes}
                              </span>
                            )}
                            {mention.shares > 0 && (
                              <span className="flex items-center">
                                <Share2 className="h-3 w-3 mr-1" />
                                {mention.shares}
                              </span>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
                
                {(!recentMentions?.data || recentMentions.data.length === 0) && (
                  <div className="text-center py-8 text-gray-500">
                    <MessageCircle className="mx-auto h-8 w-8 mb-2" />
                    <p>No recent mentions found</p>
                  </div>
                )}
              </div>
            </div>

            {/* Sentiment Breakdown */}
            <div className="card">
              <div className="card-header">
                <h3 className="text-lg font-semibold text-gray-900">Sentiment Analysis</h3>
                <span className="text-sm text-gray-500">Last {timeRange}h</span>
              </div>
              
              {sentimentData?.data ? (
                <div className="space-y-6">
                  {/* Sentiment Breakdown */}
                  <div className="grid grid-cols-3 gap-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-success-600">
                        {sentimentData.data.sentiment_breakdown.positive}
                      </div>
                      <div className="text-sm text-gray-500">Positive</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-gray-600">
                        {sentimentData.data.sentiment_breakdown.neutral}
                      </div>
                      <div className="text-sm text-gray-500">Neutral</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-error-600">
                        {sentimentData.data.sentiment_breakdown.negative}
                      </div>
                      <div className="text-sm text-gray-500">Negative</div>
                    </div>
                  </div>
                  
                  {/* Overall Score */}
                  <div className="border-t pt-4">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-gray-500">Overall Sentiment</span>
                      <span className={`text-lg font-bold ${
                        sentimentData.data.average_sentiment > 0 
                          ? 'text-success-600' 
                          : sentimentData.data.average_sentiment < 0 
                            ? 'text-error-600' 
                            : 'text-gray-600'
                      }`}>
                        {sentimentData.data.average_sentiment.toFixed(2)}
                      </span>
                    </div>
                    <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full ${
                          sentimentData.data.average_sentiment > 0 
                            ? 'bg-success-600' 
                            : sentimentData.data.average_sentiment < 0 
                              ? 'bg-error-600' 
                              : 'bg-gray-600'
                        }`}
                        style={{ 
                          width: `${Math.abs(sentimentData.data.average_sentiment) * 50}%` 
                        }}
                      ></div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <TrendingUp className="mx-auto h-8 w-8 mb-2" />
                  <p>No sentiment data available</p>
                </div>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  )
}

export default Dashboard