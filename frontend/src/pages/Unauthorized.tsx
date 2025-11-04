import { Link } from "react-router-dom";
import { ExclamationTriangleIcon } from "@heroicons/react/24/outline";

export default function Unauthorized() {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100">
          <ExclamationTriangleIcon className="h-6 w-6 text-red-600" />
        </div>
        <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Access Denied
        </h2>
        <p className="mt-2 text-center text-sm text-gray-600">
          You don't have permission to access this page
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          <div className="text-center">
            <p className="text-gray-600 mb-6">
              This page is restricted to certain user roles. Please contact your
              administrator if you believe you should have access.
            </p>
            <div className="space-y-3">
              <Link to="/" className="btn-primary w-full flex justify-center">
                Go to Home
              </Link>
              <Link
                to="/login"
                className="btn-secondary w-full flex justify-center"
              >
                Sign In with Different Account
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
