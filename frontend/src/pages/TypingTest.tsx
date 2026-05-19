/**
 * Typing test page
 */

export default function TypingTest() {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <div className="lg:col-span-2">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8">
          <h2 className="text-2xl font-bold mb-6">Typing Test</h2>
          {/* Typing area will go here */}
          <div className="typing-area bg-gray-50 dark:bg-gray-700 p-6 rounded-lg mb-6 min-h-48">
            {/* Test text and input */}
          </div>
          {/* Controls */}
        </div>
      </div>

      <div className="lg:col-span-1">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
          <h3 className="text-lg font-bold mb-4">Live Stats</h3>
          {/* Real-time metrics */}
          <div className="space-y-4">
            <div className="stat-card">
              <div className="metric">0</div>
              <div className="metric-label">WPM</div>
            </div>
            <div className="stat-card">
              <div className="metric">0%</div>
              <div className="metric-label">Accuracy</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
