import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import { Plus, Edit2, Trash2, Settings, TrendingUp } from 'lucide-react'
import { brandApi } from '../services/api'
import { toast } from 'react-hot-toast'

const BrandManagement = () => {
  const [showAddForm, setShowAddForm] = useState(false)
  const [editingBrand, setEditingBrand] = useState(null)
  const queryClient = useQueryClient()

  // Fetch brands
  const { data: brands, isLoading } = useQuery('brands', brandApi.getAll)

  // Add brand mutation
  const addBrandMutation = useMutation(brandApi.create, {
    onSuccess: () => {
      queryClient.invalidateQueries('brands')
      toast.success('Brand added successfully!')
      setShowAddForm(false)
    },
    onError: (error) => {
      toast.error('Failed to add brand')
    }
  })

  // Delete brand mutation
  const deleteBrandMutation = useMutation(brandApi.delete, {
    onSuccess: () => {
      queryClient.invalidateQueries('brands')
      toast.success('Brand deleted successfully!')
    },
    onError: () => {
      toast.error('Failed to delete brand')
    }
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    const formData = new FormData(e.target)
    const brandData = {
      name: formData.get('name') as string || '',
      keywords: formData.get('keywords') ? (formData.get('keywords') as string).split(',').map(k => k.trim()) : [],
      alert_threshold: parseInt(formData.get('alert_threshold') as string) || 10,
      sentiment_threshold: parseFloat(formData.get('sentiment_threshold') as string) || -0.5
    }
    
    addBrandMutation.mutate(brandData)
  }

  const handleDelete = (brandId) => {
    if (confirm('Are you sure you want to delete this brand?')) {
      deleteBrandMutation.mutate(brandId)
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Brand Management</h1>
          <p className="mt-2 text-gray-600">
            Manage the brands you're monitoring for mentions and reputation.
          </p>
        </div>
        
        <button
          onClick={() => setShowAddForm(true)}
          className="btn-primary mt-4 sm:mt-0"
        >
          <Plus className="h-4 w-4" />
          Add Brand
        </button>
      </div>

      {/* Add Brand Form */}
      {showAddForm && (
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-semibold text-gray-900">Add New Brand</h3>
            <button
              onClick={() => setShowAddForm(false)}
              className="text-gray-400 hover:text-gray-600"
            >
              ×
            </button>
          </div>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Brand Name *
              </label>
              <input
                type="text"
                name="name"
                required
                className="input-field"
                placeholder="Enter brand name (e.g., Apple, Nike, Tesla)"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Keywords (optional)
              </label>
              <input
                type="text"
                name="keywords"
                className="input-field"
                placeholder="Additional keywords separated by commas"
              />
              <p className="text-xs text-gray-500 mt-1">
                Extra keywords to monitor beyond the brand name
              </p>
            </div>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Alert Threshold
                </label>
                <input
                  type="number"
                  name="alert_threshold"
                  defaultValue={10}
                  min="1"
                  className="input-field"
                  placeholder="10"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Mentions per hour to trigger alert
                </p>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Sentiment Threshold
                </label>
                <input
                  type="number"
                  name="sentiment_threshold"
                  defaultValue={-0.5}
                  min="-1"
                  max="1"
                  step="0.1"
                  className="input-field"
                  placeholder="-0.5"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Alert when sentiment drops below this value
                </p>
              </div>
            </div>
            
            <div className="flex justify-end space-x-3">
              <button
                type="button"
                onClick={() => setShowAddForm(false)}
                className="btn-secondary"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={addBrandMutation.isLoading}
                className="btn-primary"
              >
                {addBrandMutation.isLoading ? 'Adding...' : 'Add Brand'}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Brands List */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {brands?.data?.map((brand) => (
          <div key={brand.id} className="card">
            <div className="flex items-start justify-between">
              <div className="flex items-center">
                <div className="p-2 bg-primary-100 rounded-lg">
                  <TrendingUp className="h-6 w-6 text-primary-600" />
                </div>
                <div className="ml-3">
                  <h3 className="text-lg font-semibold text-gray-900">
                    {brand.name}
                  </h3>
                  <p className="text-sm text-gray-500">
                    Added {new Date(brand.created_at).toLocaleDateString()}
                  </p>
                </div>
              </div>
              
              <div className="flex space-x-1">
                <button
                  onClick={() => setEditingBrand(brand)}
                  className="p-1 text-gray-400 hover:text-gray-600"
                >
                  <Edit2 className="h-4 w-4" />
                </button>
                <button
                  onClick={() => handleDelete(brand.id)}
                  className="p-1 text-gray-400 hover:text-red-600"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            </div>
            
            <div className="mt-4 space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Alert Threshold:</span>
                <span className="font-medium">{brand.alert_threshold}/hour</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Sentiment Alert:</span>
                <span className="font-medium">{brand.sentiment_threshold}</span>
              </div>
              {brand.keywords && brand.keywords.length > 0 && (
                <div className="text-sm">
                  <span className="text-gray-500">Keywords:</span>
                  <div className="mt-1 flex flex-wrap gap-1">
                    {brand.keywords.map((keyword, index) => (
                      <span
                        key={index}
                        className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded"
                      >
                        {keyword}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
            
            <div className="mt-4 pt-4 border-t border-gray-200">
              <div className="flex items-center justify-between">
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                  brand.is_active 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-gray-100 text-gray-800'
                }`}>
                  {brand.is_active ? 'Active' : 'Inactive'}
                </span>
                <button className="text-sm text-primary-600 hover:text-primary-800">
                  View Details
                </button>
              </div>
            </div>
          </div>
        ))}
        
        {(!brands?.data || brands.data.length === 0) && !showAddForm && (
          <div className="col-span-full">
            <div className="flex flex-col items-center justify-center py-16 px-4">
              <div className="text-center max-w-md mx-auto">
                <div className="mx-auto w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-6">
                  <TrendingUp className="h-8 w-8 text-gray-400" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">No brands to monitor</h3>
                <p className="text-gray-600 mb-8">
                  Get started by adding your first brand to monitor for mentions and reputation tracking.
                </p>
                <button
                  onClick={() => setShowAddForm(true)}
                  className="btn-primary inline-flex items-center gap-2 px-6 py-3 text-base font-medium"
                >
                  <Plus className="h-5 w-5" />
                  Add Your First Brand
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default BrandManagement