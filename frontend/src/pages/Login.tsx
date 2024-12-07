
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

export function Login() {
    const navigate = useNavigate();

    const handleLogin = async () => {
        const response = await fetch('http://localhost:5000/api/auth/github');
        const data = await response.json();
        if (data.auth_url) {
            window.location.href = data.auth_url;
        }
    };

    return (
        <div className="flex justify-center items-center min-h-screen">
            <button
                onClick={handleLogin}
                className="bg-gray-900 text-white px-6 py-3 rounded-md hover:bg-gray-800"
            >
                Login with GitHub
            </button>
        </div>
    );
}