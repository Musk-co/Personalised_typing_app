/**
 * Settings page
 */

export default function Settings() {
  return (
    <div className="max-w-2xl">
      <h1 className="text-3xl font-bold mb-8">Settings</h1>

      {/* Preferences */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8 space-y-6">
        <div>
          <h2 className="text-xl font-bold mb-4">Appearance</h2>
          {/* Theme selector */}
        </div>

        <div>
          <h2 className="text-xl font-bold mb-4">Typing Preferences</h2>
          {/* Typing preferences */}
        </div>

        <div>
          <h2 className="text-xl font-bold mb-4">Adapter Settings</h2>
          {/* Adapter configuration */}
        </div>

        <div>
          <h2 className="text-xl font-bold mb-4">Notifications</h2>
          {/* Notification preferences */}
        </div>
      </div>
    </div>
  )
}
