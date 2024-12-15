import axios from 'axios';

export const fetchDashboardData = async () => {
  try {
    const response = await axios.get('/api/dashboard/insights', {
      withCredentials: true
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching dashboard data:', error);
    if (axios.isAxiosError(error)) {
      if (error.response?.status === 500) {
        console.error('Server error details:', error.response.data);
      }
      if (error.response?.status === 401) {
        throw new Error('Authentication required');
      }
    }
    throw new Error('Failed to fetch dashboard data');
  }
}; 