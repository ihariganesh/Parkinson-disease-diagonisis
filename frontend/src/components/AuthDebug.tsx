import React from 'react';
import { useAuth } from '../contexts/AuthContext';

const AuthDebug: React.FC = () => {
  const { state } = useAuth();
  const token = localStorage.getItem('auth_token');

  return (
    <div className="fixed top-4 right-4 bg-yellow-100 border border-yellow-400 p-4 rounded-lg shadow-lg z-50 max-w-sm">
      <h3 className="font-bold text-yellow-800 mb-2">Auth Debug Info</h3>
      <div className="text-sm text-yellow-700 space-y-1">
        <div><strong>Is Authenticated:</strong> {state.isAuthenticated ? 'Yes' : 'No'}</div>
        <div><strong>Is Loading:</strong> {state.isLoading ? 'Yes' : 'No'}</div>
        <div><strong>User:</strong> {state.user ? `${state.user.first_name} (${state.user.role})` : 'None'}</div>
        <div><strong>Token in localStorage:</strong> {token ? 'Yes' : 'No'}</div>
        <div><strong>Current Path:</strong> {window.location.pathname}</div>
      </div>
    </div>
  );
};

export default AuthDebug;