// Simple test component to check if React is working
export default function TestApp() {
  return (
    <div className="min-h-screen bg-blue-100 flex items-center justify-center">
      <div className="bg-white p-8 rounded-lg shadow-lg">
        <h1 className="text-2xl font-bold text-blue-600 mb-4">
          ParkinsonCare - Test Mode
        </h1>
        <p className="text-gray-600">
          If you can see this, React and Tailwind are working!
        </p>
        <div className="mt-4 p-4 bg-green-100 text-green-800 rounded">
          ✅ Frontend is running successfully
        </div>
      </div>
    </div>
  );
}