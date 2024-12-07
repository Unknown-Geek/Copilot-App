import { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';

export function AuthCallback() {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();

    useEffect(() => {
        const code = searchParams.get('code');
        if (!code) {
            navigate('/login?error=no_code');
            return;
        }

        fetch(`${import.meta.env.VITE_API_URL}/api/auth/callback?code=${code}`)
            .then(res => {
                if (!res.ok) throw new Error('Network response was not ok');
                return res.json();
            })
            .then(data => {
                if (data.token) {
                    localStorage.setItem('github_token', data.token);
                    navigate('/');
                } else {
                    navigate('/login?error=auth_failed');
                }
            })
            .catch(() => navigate('/login?error=server_error'));
    }, [searchParams, navigate]);

    return <div>Authenticating...</div>;
}