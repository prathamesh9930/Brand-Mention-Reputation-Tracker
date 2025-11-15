import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { TrendingUp, Bell, Settings, BarChart3, AlertCircle } from 'lucide-react'

const Navbar = () => {
  const location = useLocation()
  
  const navigation = [
    { name: 'Dashboard', href: '/', icon: BarChart3, current: location.pathname === '/' },
    { name: 'Brands', href: '/brands', icon: TrendingUp, current: location.pathname === '/brands' },
    { name: 'Alerts', href: '/alerts', icon: AlertCircle, current: location.pathname === '/alerts' },
  ]

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            {/* Logo */}
            <div className="flex-shrink-0 flex items-center">
              <div className="flex items-center">
                <TrendingUp className="h-8 w-8 text-primary-600" />
                <div className="ml-2">
                  <h1 className="text-xl font-bold text-gray-900">
                    Brand<span className="text-primary-600">Tracker</span>
                  </h1>
                  <p className="text-xs text-gray-500">Reputation Monitor</p>
                </div>
              </div>
            </div>
            
            {/* Navigation Links */}
            <div className="hidden sm:ml-8 sm:flex sm:space-x-8">
              {navigation.map((item) => (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`
                    inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors duration-200
                    ${item.current
                      ? 'border-primary-500 text-primary-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }
                  `}
                >
                  <item.icon className="w-4 h-4 mr-2" />
                  {item.name}
                </Link>
              ))}
            </div>
          </div>

          {/* Right side */}
          <div className="flex items-center space-x-4">
            {/* Status Indicator */}
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
              <span className="text-sm text-gray-500">Live Monitoring</span>
            </div>
            
            {/* Notifications */}
            <button className="p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 transition-colors duration-200">
              <Bell className="h-5 w-5" />
            </button>
            
            {/* Settings */}
            <button className="p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 transition-colors duration-200">
              <Settings className="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>
      
      {/* Mobile Navigation */}
      <div className="sm:hidden">
        <div className="pt-2 pb-3 space-y-1">
          {navigation.map((item) => (
            <Link
              key={item.name}
              to={item.href}
              className={`
                block pl-3 pr-4 py-2 border-l-4 text-base font-medium transition-colors duration-200
                ${item.current
                  ? 'bg-primary-50 border-primary-500 text-primary-700'
                  : 'border-transparent text-gray-600 hover:text-gray-800 hover:bg-gray-50 hover:border-gray-300'
                }
              `}
            >
              <div className="flex items-center">
                <item.icon className="w-4 h-4 mr-3" />
                {item.name}
              </div>
            </Link>
          ))}
        </div>
      </div>
    </nav>
  )
}

export default Navbar