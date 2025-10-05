import { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { Button } from '@shared/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@shared/components/ui/card';
import { CheckCircle2, XCircle, Loader2 } from 'lucide-react';
import SiteHeader from '@client/components/site-header';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export default function VerifyEmailPage() {
  const { token } = useParams<{ token: string }>();
  const navigate = useNavigate();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState('');
  const hasVerified = useRef(false);

  useEffect(() => {
    const verifyEmail = async () => {
      // Prevent duplicate API calls (React StrictMode double render issue)
      if (hasVerified.current) return;
      hasVerified.current = true;

      try {
        const response = await fetch(`${API_BASE_URL}/api/auth/verify-email/${token}/`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        });

        const data = await response.json();

        if (response.ok) {
          setStatus('success');
          setMessage(data.message || 'Email verified successfully!');

          // Redirect to login after 3 seconds
          setTimeout(() => {
            navigate('/login?verified=true');
          }, 3000);
        } else {
          setStatus('error');
          setMessage(data.error || 'Failed to verify email. The link may be invalid or expired.');
        }
      } catch (error) {
        setStatus('error');
        setMessage('An error occurred while verifying your email. Please try again.');
        console.error('Email verification error:', error);
      }
    };

    if (token) {
      verifyEmail();
    } else {
      setStatus('error');
      setMessage('Invalid verification link.');
    }
  }, [token, navigate]);

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100">
      <SiteHeader />

      <div className="container mx-auto px-4 py-16 flex items-center justify-center min-h-[80vh]">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <div className="flex justify-center mb-4">
              {status === 'loading' && (
                <Loader2 className="h-16 w-16 text-blue-500 animate-spin" />
              )}
              {status === 'success' && (
                <CheckCircle2 className="h-16 w-16 text-green-500" />
              )}
              {status === 'error' && (
                <XCircle className="h-16 w-16 text-red-500" />
              )}
            </div>

            <CardTitle className="text-2xl">
              {status === 'loading' && 'Verifying Email...'}
              {status === 'success' && 'Email Verified!'}
              {status === 'error' && 'Verification Failed'}
            </CardTitle>

            <CardDescription className="mt-4 text-base">
              {message}
            </CardDescription>
          </CardHeader>

          <CardContent className="space-y-4">
            {status === 'success' && (
              <div className="text-center text-sm text-gray-600">
                Redirecting to login page in 3 seconds...
              </div>
            )}

            <div className="flex gap-4 justify-center">
              {status === 'success' ? (
                <Button onClick={() => navigate('/login')} className="w-full">
                  Go to Login
                </Button>
              ) : status === 'error' ? (
                <>
                  <Button onClick={() => navigate('/register')} variant="outline">
                    Register Again
                  </Button>
                  <Button onClick={() => navigate('/')}>
                    Go Home
                  </Button>
                </>
              ) : null}
            </div>

            {status !== 'loading' && (
              <div className="text-center text-sm text-gray-600">
                Need help? <Link to="/" className="text-blue-600 hover:underline">Contact Support</Link>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
