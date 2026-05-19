/**
 * Header component - Top navigation and branding
 */

export default function Header() {
  return (
    <header className="bg-white dark:bg-gray-800 shadow">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-primary-600 rounded-lg" />
            <h1 className="text-xl font-bold text-gray-900 dark:text-white">
              Typing Trainer
            </h1>
          </div>
          <nav className="hidden md:flex gap-6">
            <a href="/" className="text-gray-600 dark:text-gray-400 hover:text-primary-600">
              Home
            </a>
            <a href="/typing-test" className="text-gray-600 dark:text-gray-400 hover:text-primary-600">
              Practice
            </a>
            <a href="/dashboard" className="text-gray-600 dark:text-gray-400 hover:text-primary-600">
              Dashboard
            </a>
          </nav>
        </div>
      </div>
    </header>
  )
}
