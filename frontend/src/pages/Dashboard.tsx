/**
 * Dashboard page
 */

export default function Dashboard() {
  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold">Dashboard</h1>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { label: 'Total Sessions', value: '0' },
          { label: 'Average WPM', value: '0' },
          { label: 'Best WPM', value: '0' },
          { label: 'Accuracy', value: '0%' },
        ].map((stat) => (
          <div
            key={stat.label}
            className="bg-white dark:bg-gray-800 rounded-lg shadow p-6"
          >
            <p className="text-gray-600 dark:text-gray-400 text-sm">{stat.label}</p>
            <p className="text-3xl font-bold mt-2">{stat.value}</p>
          </div>
        ))}
      </div>

      {/* Progress Chart */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8">
        <h2 className="text-2xl font-bold mb-6">Progress Over Time</h2>
        {/* Chart will go here */}
        <div className="h-64 bg-gray-100 dark:bg-gray-700 rounded-lg" />
      </div>

      {/* Recent Sessions */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8">
        <h2 className="text-2xl font-bold mb-6">Recent Sessions</h2>
        {/* Sessions list will go here */}
      </div>
    </div>
  )
}
