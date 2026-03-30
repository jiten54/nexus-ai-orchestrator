import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Cpu, AlertCircle } from 'lucide-react';

export const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);
    
    const result = await login(email, password);
    setIsLoading(false);
    
    if (result.success) {
      navigate('/dashboard');
    } else {
      setError(result.error);
    }
  };

  return (
    <div className="min-h-screen bg-[#0A0A0A] flex items-center justify-center p-4" data-testid="login-page">
      <div className="absolute inset-0 bg-gradient-to-br from-[#00E5FF]/5 via-transparent to-[#7000FF]/5" />
      
      <Card className="w-full max-w-md bg-[#141414] border-white/10 relative z-10">
        <CardHeader className="text-center space-y-4">
          <div className="mx-auto w-16 h-16 bg-[#00E5FF]/10 rounded-xl flex items-center justify-center border border-[#00E5FF]/30">
            <Cpu className="w-8 h-8 text-[#00E5FF]" />
          </div>
          <div>
            <CardTitle className="text-2xl font-bold text-white tracking-tight" style={{ fontFamily: 'Outfit, sans-serif' }}>
              NEXUS_AI
            </CardTitle>
            <CardDescription className="text-[#A0A0A0]">
              Autonomous Workflow Intelligence
            </CardDescription>
          </div>
        </CardHeader>
        
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="flex items-center gap-2 p-3 bg-[#FF3B30]/10 border border-[#FF3B30]/30 rounded-lg text-[#FF3B30] text-sm" data-testid="login-error">
                <AlertCircle className="w-4 h-4" />
                {error}
              </div>
            )}
            
            <div className="space-y-2">
              <Label htmlFor="email" className="text-[#A0A0A0] text-xs uppercase tracking-[0.2em]">Email</Label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="bg-[#0A0A0A] border-white/10 text-white focus:border-[#00E5FF] focus:ring-[#00E5FF]"
                placeholder="admin@nexusai.com"
                required
                data-testid="login-email-input"
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="password" className="text-[#A0A0A0] text-xs uppercase tracking-[0.2em]">Password</Label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="bg-[#0A0A0A] border-white/10 text-white focus:border-[#00E5FF] focus:ring-[#00E5FF]"
                placeholder="••••••••"
                required
                data-testid="login-password-input"
              />
            </div>
            
            <Button
              type="submit"
              className="w-full bg-[#00E5FF] text-black font-semibold hover:bg-[#00E5FF]/90 transition-all active:scale-[0.98]"
              disabled={isLoading}
              data-testid="login-submit-button"
            >
              {isLoading ? 'Authenticating...' : 'Access System'}
            </Button>
          </form>
          
          <p className="text-center text-[#666666] text-sm mt-6">
            No account?{' '}
            <Link to="/register" className="text-[#00E5FF] hover:underline" data-testid="register-link">
              Create one
            </Link>
          </p>
        </CardContent>
      </Card>
    </div>
  );
};

export const RegisterPage = () => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);
    
    const result = await register(email, password, name);
    setIsLoading(false);
    
    if (result.success) {
      navigate('/dashboard');
    } else {
      setError(result.error);
    }
  };

  return (
    <div className="min-h-screen bg-[#0A0A0A] flex items-center justify-center p-4" data-testid="register-page">
      <div className="absolute inset-0 bg-gradient-to-br from-[#00E5FF]/5 via-transparent to-[#7000FF]/5" />
      
      <Card className="w-full max-w-md bg-[#141414] border-white/10 relative z-10">
        <CardHeader className="text-center space-y-4">
          <div className="mx-auto w-16 h-16 bg-[#00E5FF]/10 rounded-xl flex items-center justify-center border border-[#00E5FF]/30">
            <Cpu className="w-8 h-8 text-[#00E5FF]" />
          </div>
          <div>
            <CardTitle className="text-2xl font-bold text-white tracking-tight" style={{ fontFamily: 'Outfit, sans-serif' }}>
              Join NEXUS_AI
            </CardTitle>
            <CardDescription className="text-[#A0A0A0]">
              Create your operator account
            </CardDescription>
          </div>
        </CardHeader>
        
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="flex items-center gap-2 p-3 bg-[#FF3B30]/10 border border-[#FF3B30]/30 rounded-lg text-[#FF3B30] text-sm" data-testid="register-error">
                <AlertCircle className="w-4 h-4" />
                {error}
              </div>
            )}
            
            <div className="space-y-2">
              <Label htmlFor="name" className="text-[#A0A0A0] text-xs uppercase tracking-[0.2em]">Name</Label>
              <Input
                id="name"
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="bg-[#0A0A0A] border-white/10 text-white focus:border-[#00E5FF] focus:ring-[#00E5FF]"
                placeholder="Operator Name"
                required
                data-testid="register-name-input"
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="email" className="text-[#A0A0A0] text-xs uppercase tracking-[0.2em]">Email</Label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="bg-[#0A0A0A] border-white/10 text-white focus:border-[#00E5FF] focus:ring-[#00E5FF]"
                placeholder="operator@company.com"
                required
                data-testid="register-email-input"
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="password" className="text-[#A0A0A0] text-xs uppercase tracking-[0.2em]">Password</Label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="bg-[#0A0A0A] border-white/10 text-white focus:border-[#00E5FF] focus:ring-[#00E5FF]"
                placeholder="••••••••"
                required
                data-testid="register-password-input"
              />
            </div>
            
            <Button
              type="submit"
              className="w-full bg-[#00E5FF] text-black font-semibold hover:bg-[#00E5FF]/90 transition-all active:scale-[0.98]"
              disabled={isLoading}
              data-testid="register-submit-button"
            >
              {isLoading ? 'Creating Account...' : 'Create Account'}
            </Button>
          </form>
          
          <p className="text-center text-[#666666] text-sm mt-6">
            Already have access?{' '}
            <Link to="/login" className="text-[#00E5FF] hover:underline" data-testid="login-link">
              Sign in
            </Link>
          </p>
        </CardContent>
      </Card>
    </div>
  );
};
