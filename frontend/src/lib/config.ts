// Configuration for different environments
const config = {
  development: {
    apiUrl: 'http://localhost:5000/api', // Flask default port
    plaidEnv: 'sandbox',
  },
  production: {
    apiUrl: import.meta.env.VITE_API_URL || 'http://localhost:5000/api',
    plaidEnv: 'production',
  },
};

const environment = import.meta.env.MODE || 'development';

export default config[environment as keyof typeof config];