import axios from 'axios';

export const fetchDashboardData = async () => {
  try {
    const response = await axios.get('/api/dashboard/insights', {
      withCredentials: true
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching dashboard data:', error);
    throw error;
  }
};

export const generateAIInsights = async () => {
  try {
    const response = await axios.post('/api/dashboard/generate-insights', {}, {
      withCredentials: true
    });
    return response.data;
  } catch (error) {
    console.error('Error generating AI insights:', error);
    throw error;
  }
}; 