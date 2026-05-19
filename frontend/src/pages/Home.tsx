/**
 * Home page
 */

export default function Home() {
  return (
    <div className="text-center py-16">
      <h1 className="text-4xl font-bold mb-4">Personalized Adaptive Typing Trainer</h1>
      <p className="text-xl text-gray-600 dark:text-gray-400 mb-8">
        Improve your typing skills with AI-powered adaptive difficulty
      </p>
      <div className="flex gap-4 justify-center">
        <a href="/login" className="bg-primary-600 hover:bg-primary-700 text-white px-8 py-3 rounded-lg font-medium">
          Login
        </a>
        <a href="/register" className="bg-gray-200 hover:bg-gray-300 text-gray-900 px-8 py-3 rounded-lg font-medium">
          Register
        </a>
      </div>
    </div>
  )
}
